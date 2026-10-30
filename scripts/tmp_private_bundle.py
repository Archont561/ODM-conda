import os
import subprocess
import sys
import tempfile
from collections import deque
from pathlib import Path

with tempfile.TemporaryDirectory(prefix='odm-bundle-test-') as tmp:
    root=Path(tmp); dataset=root/'seneca'
    for cmd in (['git','init',str(dataset)],['git','-C',str(dataset),'fetch','--depth=1','https://github.com/OpenDroneMap/odm_data_seneca.git','9220acfdca75cc5e2dd6d27fe48550c5ae0877f2'],['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD']):
        subprocess.run(cmd,check=True)
    assert subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()=='9220acfdca75cc5e2dd6d27fe48550c5ae0877f2'
    cmd=[sys.executable,'scripts/private_odm_bundle.py','build','--destination',str(root/'bundle'),'--dataset',str(dataset)]
    tail=deque(maxlen=15)
    with subprocess.Popen(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=1) as result:
        for line in result.stdout:
            print(line,end='',flush=True)
            tail.append(line)
        code=result.wait()
    if code:
        message=' '.join(tail).encode('ascii','backslashreplace').decode('ascii')[-2500:].replace('\n',' | ')
        print('::error::PRIVATE BUNDLE FAILED '+message,flush=True)
        raise SystemExit(code)
    print('::notice::Private source-build bundle, relocated replay and Seneca pipeline PASS; no outputs uploaded.',flush=True)
