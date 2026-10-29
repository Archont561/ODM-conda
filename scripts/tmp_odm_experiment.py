"""Diagnose only the existing package compatibility, in a disposable CI directory."""
import hashlib, os, subprocess, sys, tempfile, traceback, zipfile
from pathlib import Path
sys.excepthook = lambda typ, value, tb: print('::error::' + ' '.join(traceback.format_exception(typ,value,tb)).replace('\n', ' | '), flush=True)
archives=[('dem2points',12892015321,'a04b3651eebe670cb9549904567565f15bf8047c9ef6faf71da720b20c2a67ad'),('renderdem',12884831960,'21526568d7fb39f0070ef929c01c50367881eb81eee1cdf6382cad496b6d2265')]
with tempfile.TemporaryDirectory(dir=os.environ['RUNNER_TEMP']) as temp:
    root=Path(temp); pkgs=[]
    for name, aid, expected in archives:
        with (root/'source.zip').open('wb') as file:
            subprocess.run(['gh','api',f'repos/Archont561/ODM-conda/actions/artifacts/{aid}/zip'],stdout=file,check=True)
        assert hashlib.sha256((root/'source.zip').read_bytes()).hexdigest() == expected
        with zipfile.ZipFile(root/'source.zip') as z:
            matches=[n for n in z.namelist() if Path(n).name.startswith(name+'-') and n.endswith('.conda')]
            assert len(matches)==1
            p=root/Path(matches[0]).name; p.write_bytes(z.read(matches[0])); pkgs.append(str(p))
    project=root/'project'; subprocess.run(['pixi','init','--format','pixi','--scm','github','--channel','conda-forge','--platform','linux-64',str(project)],check=True)
    result=subprocess.run(['pixi','add','--manifest-path',str(project/'pixi.toml'),*pkgs],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if result.returncode:
        print('::error::Two-package solve failed: '+result.stdout[:12000].replace('\n',' | '),flush=True)
        sys.exit(result.returncode)
    print('::notice::dem2points + renderdem solved successfully; the full nine-package conflict is elsewhere',flush=True)
