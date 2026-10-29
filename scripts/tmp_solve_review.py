import hashlib, json, subprocess, sys, tarfile, tempfile, traceback, urllib.request, zipfile
import zstandard
from pathlib import Path
sys.excepthook = lambda typ, value, tb: print("::error::" + " ".join(traceback.format_exception(typ, value, tb)).replace("\n", " | "), flush=True)

cases = [('dem2mesh','/tmp/dem.zip','432b5b58d45d0cc3844a9980afc1ba84b0fb8f92da75af3b93d1863d33236d5f'), ('poissonrecon-odm','/tmp/poisson.zip','44c7723e16c9d1bc40e9b1634578836657c02ff4eebf6d13d363146f850903bf')]
wanted = {'libgdal-core', 'libgomp', 'libjpeg-turbo', 'libpng', 'libzlib'}
for name, path, digest in cases:
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest
    with tempfile.TemporaryDirectory() as temp, zipfile.ZipFile(path) as z:
        pkgs = [n for n in z.namelist() if Path(n).name.startswith(name+'-') and n.endswith('.conda')]
        assert len(pkgs) == 1, (name, pkgs)
        pkg = Path(temp)/Path(pkgs[0]).name
        pkg.write_bytes(z.read(pkgs[0]))
        proc = subprocess.run(['rattler-build','test','--package-file',str(pkg),'--channel','conda-forge','--channel-priority','strict','--output-dir',str(Path(temp)/'test'),'--log-style','plain','--color','never'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        if proc.returncode:
            print('::error::'+name+' retest failed: '+proc.stdout[-3000:].replace('\n',' | '),flush=True); sys.exit(proc.returncode)
        selected = {}
        for line in proc.stdout.splitlines():
            cols = [s.strip(' │') for s in line.split('┆')]
            if len(cols) >= 4 and cols[0] in wanted:
                selected[cols[0]] = cols[1:3]
        assert 'libgomp' in selected and 'libpng' in selected, selected
        results = {}
        for dep, (version, build) in selected.items():
            filename=f'{dep}-{version}-{build}.conda'
            url='https://conda.anaconda.org/conda-forge/linux-64/'+filename
            data=urllib.request.urlopen(url,timeout=90).read()
            p=Path(temp)/filename; p.write_bytes(data)
            with zipfile.ZipFile(p) as outer:
            info_name = next(n for n in outer.namelist() if n.startswith('info-') and n.endswith('.tar.zst'))
            with outer.open(info_name) as compressed, zstandard.ZstdDecompressor().stream_reader(compressed) as stream, tarfile.open(fileobj=stream,mode='r|') as tar:
                info = {m.name: tar.extractfile(m).read() for m in tar if m.isfile() and (m.name == 'info/index.json' or m.name.startswith('info/licenses/'))}
            idx=json.loads(info['info/index.json'])
            assert (idx['name'],idx['version'],idx['build'])==(dep,version,build)
            notices={key:hashlib.sha256(value).hexdigest() for key,value in info.items() if key.startswith('info/licenses/')}
            results[dep]={'version':version,'build':build,'sha256':hashlib.sha256(data).hexdigest(),'license':idx.get('license'),'info_license_files':notices}
        print('::notice::'+name+' fresh retest PASS; independently downloaded exact-name dependency packages (solver bytes not hash-correlated): '+json.dumps(results,sort_keys=True),flush=True)
