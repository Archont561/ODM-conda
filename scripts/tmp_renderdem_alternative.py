import base64
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from inventory_conda_environment import inventory
from private_conda_channel import create

root=Path(os.environ['RUNNER_TEMP'])
name='renderdem-1.0-h873e7db_1.conda'
expected='a681202611aa3fa25281055825b75a89e1a256260a954ce69bcd5393a834d94c'
def digest(b): return hashlib.sha256(b).hexdigest()
if sys.argv[1]=='prepare':
    zippath=root/'original.zip'
    assert digest(zippath.read_bytes())=='cd2671e9f6184102887b08b01f843309210c2fddad7825439bb05e8f7bdd2385'
    with zipfile.ZipFile(zippath) as z:
        names=[n for n in z.namelist() if n.endswith('/'+name) or n==name]; assert len(names)==1 and len(set(z.namelist()))==len(z.namelist())
        raw=z.read(names[0])
    assert digest(raw)==expected
    package=root/name;package.write_bytes(raw);create([package],root/'channel')
    project=root/'runtime'; project.mkdir()
    (project/'pixi.toml').write_text('[workspace]\nname = "renderdem-alt"\nversion = "0.1.0"\nchannels = ["'+(root/'channel').as_uri()+'", "conda-forge"]\nplatforms = ["linux-64"]\n\n[dependencies]\nrenderdem = "==1.0"\nlibspatialite = { version = "==5.1.0", build = "lgpl_*" }\nlibarchive = { version = "==3.8.11", build = "lgpl_*" }\npdal = "==2.10.0"\n')
elif sys.argv[1]=='inspect':
    prefix=(root/'runtime/.pixi/envs/default').resolve()
    records=inventory(prefix)['packages']; p={i['name']:i for i in records}
    assert p['renderdem']['sha256']==expected
    assert p['libspatialite']['build'].startswith('lgpl_') and p['libarchive']['build'].startswith('lgpl_')
    assert 'lzo' not in p and 'librttopo' not in p
    env=os.environ.copy();env.pop('LD_LIBRARY_PATH',None);env['PATH']=str(prefix/'bin')+os.pathsep+os.defpath;env['PROJ_DATA']=env['PROJ_LIB']=str(prefix/'share/proj')
    test=prefix/'share/odm-conda/renderdem/functional_test.py'
    proc=subprocess.run([sys.executable,str(test)],env=env,capture_output=True,text=True,timeout=180)
    print(proc.stdout,proc.stderr,flush=True);assert proc.returncode==0
    objects={}
    for label,pattern in [('archive','lib/libarchive.so.*'),('spatialite','lib/libspatialite.so.*')]:
        real={v.resolve() for v in prefix.glob(pattern) if v.is_file()};assert len(real)==1
        file=real.pop();assert file.is_relative_to(prefix)
        out=subprocess.check_output(['readelf','-d',str(file)],text=True)
        objects[label]={'path':str(file.relative_to(prefix)),'sha256':digest(file.read_bytes()),'needed':re.findall(r'\(NEEDED\).*?\[([^\]]+)\]',out)}
    assert 'liblzo2.so.2' not in objects['archive']['needed']
    assert 'librttopo.so.1' not in objects['spatialite']['needed']
    raw=json.dumps({'candidate_sha256':expected,'inventory':[{k:r[k] for k in ('name','version','build','sha256','license')} for r in records],'objects':objects,'tests':'Candidate installed-prefix ldd and generated PLY/LAS tests passed. Not LAZ or full ODM validation.','scope':'Experimental runtime variant constraints; not an approved release lock, compatibility guarantee, complete license or corresponding source review.'},sort_keys=True,indent=2).encode()
    encoded=base64.b64encode(gzip.compress(raw,mtime=0)).decode();chunks=[encoded[i:i+2700] for i in range(0,len(encoded),2700)];assert len(chunks)<=9
    print(f'::notice::ALT-INFO chunks={len(chunks)} sha256={digest(raw)} records={len(records)}',flush=True)
    for i,chunk in enumerate(chunks):print(f'::notice::ALT-CHUNK-{i:02d} {chunk}',flush=True)
else: raise ValueError('unknown operation')
