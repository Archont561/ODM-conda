import os
import subprocess
import sys
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory(prefix='odm-bundle-test-') as tmp:
    root=Path(tmp); dataset=root/'seneca'
    for cmd in (['git','init',str(dataset)],['git','-C',str(dataset),'fetch','--depth=1','https://github.com/OpenDroneMap/odm_data_seneca.git','9220acfdca75cc5e2dd6d27fe48550c5ae0877f2'],['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD']):
        subprocess.run(cmd,check=True)
    assert subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()=='9220acfdca75cc5e2dd6d27fe48550c5ae0877f2'
    result=subprocess.run([sys.executable,'scripts/private_odm_bundle.py','build','--destination',str(root/'bundle'),'--dataset',str(dataset)],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    print(result.stdout,flush=True)
    if result.returncode:
        print('::error::PRIVATE BUNDLE FAILED '+result.stdout[-4500:].replace('\n',' | '),flush=True)
        result.check_returncode()
    print('::notice::Private source-build bundle, relocated replay and Seneca pipeline PASS; no outputs uploaded.',flush=True)
