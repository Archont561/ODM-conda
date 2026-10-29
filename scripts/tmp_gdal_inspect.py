"""Read-only inspection of owner-produced native artifacts; temporary CI helper."""
import hashlib, io, json, os, subprocess, sys, tarfile, tempfile, traceback, zipfile
from pathlib import Path, PurePosixPath
from audit_package import audit
from common import config, first_comment
from package_archive import read_package

sys.excepthook = lambda typ, val, tb: print('::error::' + ' '.join(traceback.format_exception(typ, val, tb)).replace('\n', ' | '), flush=True)
NAMES = ('dem2points', 'fastrasterfilter', 'odm-orthophoto', 'renderdem')
REV = '75564b4c0f2869da40151783f54abd378be36a1d'
def digest(b): return hashlib.sha256(b).hexdigest()
def notice(s): print('::notice::' + s, flush=True)
def run(cmd):
    p = subprocess.run([str(x) for x in cmd], text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode:
        notice('Command failed: '+str(cmd[0])+' '+p.stdout[:9000].replace('\n', ' | ')); p.check_returncode()
    return p.stdout

with tempfile.TemporaryDirectory(prefix='gdal-review-', dir=os.environ.get('RUNNER_TEMP')) as temp:
    root=Path(temp); source=Path('/tmp/gdal-build.zip'); assert digest(source.read_bytes())=='fff273a42ac145811f36447824fc86e03820d13b6a6efd2f04111992100970a2'
    packages=[]
    with zipfile.ZipFile(source) as z:
        members=z.namelist(); notice('Verified artifact ZIP; members '+json.dumps(members))
        condas=[n for n in members if n.endswith('.conda')]
        assert len(condas)==4 and all(sum(Path(n).name.startswith(name+'-') for n in condas)==1 for name in NAMES), condas
        for name in NAMES:
            pth=next(n for n in condas if Path(n).name.startswith(name+'-'))
            bundle=[n for n in members if Path(n).name.startswith('source-'+name+'-') and n.endswith('.tar.gz')]
            assert len(bundle)==1, (name,bundle)
            pkg=root/Path(pth).name; pkg.write_bytes(z.read(pth)); packages.append(pkg)
            c=config()['components'][name]; result=audit(name,c,pkg)
            info,payload=read_package(pkg); idx=json.loads(info['info/index.json']); assert idx['build_number']==c['build_number']
            assert any(s.startswith('libgdal-core >=3.12.2') and '<3.12.3' in s for s in idx['depends']),idx['depends']
            data=z.read(bundle[0]);
            with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as src:
                manifest=json.load(src.extractfile('SOURCE-MANIFEST.json'))
                assert manifest['packaging_commit']==REV and not manifest['packaging_dirty'],manifest
                for path,sha in manifest['files'].items(): assert digest(src.extractfile(path).read()) == sha,path
                upstreams=[n for n in manifest['files'] if n.startswith('upstream/'+name+'-') and n.endswith('.tar.gz')]
                assert len(upstreams)==1
                upstream=src.extractfile(upstreams[0]).read(); assert digest(upstream)==c['source']['sha256']
                with tarfile.open(fileobj=io.BytesIO(upstream), mode='r:gz') as orig:
                    tops={PurePosixPath(m.name).parts[0] for m in orig.getmembers()}; assert len(tops)==1
                    top=next(iter(tops))
                    for item in c['notices']:
                        raw=orig.extractfile(top+'/'+item['source']).read()
                        if item['kind']=='first-comment': raw=first_comment(raw)
                        target=item['target']; meta=[v for k,v in info.items() if k.startswith('info/licenses/') and PurePosixPath(k).name==target]
                        assert len(meta)==1 and raw==meta[0]==payload['share/licenses/'+name+'/'+target],target
                count=len(manifest['files'])
            run(['rattler-build','test','--package-file',pkg,'--channel','conda-forge','--channel-priority','strict','--output-dir',root/('test-'+name),'--log-style','plain'])
            notice(name+' PASS source bundle sha256 '+digest(data)+' entries '+str(count)+' upstream notice bytes verified, current audit and fresh retest passed; '+json.dumps(result,sort_keys=True))
    project=root/'project'; run(['pixi','init','--format','pixi','--scm','github','-c','conda-forge','-p','linux-64',project])
    run(['pixi','add','--manifest-path',project/'pixi.toml','--no-install',packages[0],packages[-1]])
    notice('dem2points and RenderDEM actual artifact solve PASS')
    run(['pixi','add','--manifest-path',project/'pixi.toml',*packages,'pdal','python-pdal','gdal','exiftool'])
    output=run(['pixi','list','--manifest-path',project/'pixi.toml','--locked'])
    selected=[x.strip() for x in output.splitlines() if any(n in x for n in ('libgdal-core','libpdal-core','py-opencv','libopencv','python-pdal'))]
    notice('Four actual artifact packages installed together with selected dependencies: '+' | '.join(selected))
    for name in NAMES:
        exe=config()['components'][name]['executable']; assert (project/'.pixi/envs/default/bin'/exe).is_file()
    notice('Four-component install and binary presence PASS; full ODM integration not tested')
