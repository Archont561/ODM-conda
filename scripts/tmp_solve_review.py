import hashlib, re, subprocess, sys, tempfile, zipfile
from pathlib import Path

cases = [('dem2mesh','/tmp/dem.zip','432b5b58d45d0cc3844a9980afc1ba84b0fb8f92da75af3b93d1863d33236d5f'), ('poissonrecon-odm','/tmp/poisson.zip','44c7723e16c9d1bc40e9b1634578836657c02ff4eebf6d13d363146f850903bf')]
for name, path, digest in cases:
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest
    with tempfile.TemporaryDirectory() as temp, zipfile.ZipFile(path) as z:
        pkgs = [n for n in z.namelist() if Path(n).name.startswith(name+'-') and n.endswith('.conda')]
        assert len(pkgs) == 1, (name, pkgs)
        pkg = Path(temp)/Path(pkgs[0]).name
        pkg.write_bytes(z.read(pkgs[0]))
        print(f'::notice::{name} verified package {pkg.name}, SHA256 {hashlib.sha256(pkg.read_bytes()).hexdigest()}', flush=True)
        proc = subprocess.run(['rattler-build','test','--package-file',str(pkg),'--channel','conda-forge','--channel-priority','strict','--output-dir',str(Path(temp)/'test'),'--log-style','plain','--color','never'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = proc.stdout
        Path('/tmp/'+name+'-test.log').write_text(output)
        for line in output.splitlines():
            if re.search(r'\b(libgdal-core|libgomp|libgcc|libstdcxx|libjpeg-turbo|libpng|zlib|libzlib|_openmp_mutex)\b',line,re.I):
                print('::notice::'+name+' fresh test '+line.strip(),flush=True)
        if proc.returncode:
            print('::error::'+name+' retest failed: '+output[-3000:].replace('\n',' | '),flush=True)
            sys.exit(proc.returncode)
        print('::notice::'+name+' isolated retest passed; selected solve lines above are not complete closure',flush=True)
