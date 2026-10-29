import hashlib, io, json, subprocess, tarfile, tempfile, zipfile, sys, traceback
sys.excepthook=lambda typ, value, tb: print("::error::" + " | ".join(traceback.format_exception(typ, value, tb)).replace("\n", " "))
from pathlib import Path, PurePosixPath
from common import config, first_comment
from audit_package import audit
from package_archive import read_package

cases = [
 ('dem2mesh','/tmp/artifact-dem.zip','a04b3651eebe670cb9549904567565f15bf8047c9ef6faf71da720b20c2a67ad','9355b8a8c904726f2b40f011dd43c64f457f22e0'),
 ('renderdem','/tmp/artifact-batch.zip','21526568d7fb39f0070ef929c01c50367881eb81eee1cdf6382cad496b6d2265','2cc2861a8746589fda4bef57fcf29b1cd60b7f50'),
]
def sha(b): return hashlib.sha256(b).hexdigest()
def notice(msg): print('::notice::'+msg,flush=True)
with tempfile.TemporaryDirectory() as temp:
 for name, filename, expected_zip, revision in cases:
  assert sha(Path(filename).read_bytes()) == expected_zip
  with zipfile.ZipFile(filename) as z:
   notice(name+' artifact members '+str(z.namelist()))
   packages=[n for n in z.namelist() if Path(n).name.startswith(name+'-') and n.endswith('.conda')]
   bundles=[n for n in z.namelist() if Path(n).name.startswith('source-'+name+'-') and n.endswith('.tar.gz')]
   if not packages and not bundles and name=='dem2mesh':
    notice('WARNING: owner run contains dem2points, NOT dem2mesh; no dem2mesh build 1 artifact was produced')
    continue
   assert len(packages)==len(bundles)==1, (packages,bundles)
   if name=='dem2mesh':
    assert len([n for n in z.namelist() if n.endswith('.conda')])==1
   package=Path(temp)/Path(packages[0]).name; package.write_bytes(z.read(packages[0])); component=config()['components'][name]
   result=audit(name,component,package); info,payload=read_package(package)
   data=z.read(bundles[0]); notice(name+' source SHA256 '+sha(data))
   with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as source:
    manifest=json.load(source.extractfile('SOURCE-MANIFEST.json'))
    assert manifest['packaging_commit']==revision and not manifest['packaging_dirty']
    for path,digest in manifest['files'].items(): assert sha(source.extractfile(path).read())==digest,path
    archives=[p for p in manifest['files'] if p.startswith('upstream/'+name+'-') and p.endswith('.tar.gz')]
    assert len(archives)==1
    upstream=source.extractfile(archives[0]).read(); assert sha(upstream)==component['source']['sha256']
    with tarfile.open(fileobj=io.BytesIO(upstream),mode='r:gz') as orig:
     members=orig.getmembers(); tops={PurePosixPath(m.name).parts[0] for m in members}; assert len(tops)==1
     root=next(iter(tops))
     for item in component['notices']:
      if item['source']=='Simplify-MIT.txt':
       raw=source.extractfile('packaging/research/notices/fast-quadric-2019-MIT.txt').read()
      else:
       raw=orig.extractfile(root+'/'+item['source']).read()
       if item['kind']=='first-comment': raw=first_comment(raw)
      target=item['target']; actual=payload['share/licenses/'+name+'/'+target]
      matches=[v for k,v in info.items() if k.startswith('info/licenses/') and PurePosixPath(k).name==target]
      assert raw==actual and len(matches)==1 and matches[0]==raw,target
    notice(name+' source entries verified '+str(len(manifest['files']))+'; all '+str(len(component['notices']))+' declared notice bytes match payload and metadata')
   notice(name+' audit '+json.dumps(result,sort_keys=True))
   result = subprocess.run(['rattler-build','test','--package-file',str(package),'--channel','conda-forge','--channel-priority','strict','--output-dir',str(Path(temp)/('test-'+name)),'--log-style','plain'],text=True,capture_output=True)
   if result.returncode:
    notice(name+' test failed: '+(result.stderr or result.stdout)[-1000:]); result.check_returncode()
   import re
   matches = []
   for line in (result.stdout+'\n'+result.stderr).splitlines():
    if re.search(r'(?i)(libpdal|libgdal|libgomp|libgcc|libstdcxx)', line):
     matches.append(line.strip())
   notice('fresh solve selected dependencies '+json.dumps(matches[:30]))
   cache=Path.home()/'.cache/rattler/cache/pkgs'
   found=[]
   for pat in ('libpdal-core-2.10.2*','libgdal-core-3.13.3*','libgomp-16.2.0*'):
    for entry in cache.glob(pat):
     about=entry/'info/about.json'
     if about.is_file():
      d=json.loads(about.read_text()); found.append({'cache':entry.name,'license':d.get('license'),'license_family':d.get('license_family'),'license_file':d.get('license_file')})
   notice('fresh solve cached package metadata '+json.dumps(found))
   notice(name+' independent fresh retest PASS')
