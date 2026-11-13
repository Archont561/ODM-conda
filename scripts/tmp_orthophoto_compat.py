import json,subprocess,tempfile,zipfile,tarfile
from pathlib import Path
import zstandard
from common import sha256,rattler,run
from private_conda_channel import create
from private_odm_bundle import loopback,PORT

NAME='odm-orthophoto-0.0.0.dev20250225-h873e7db_2.conda'
DIGEST='c64be4380202cfe6e41cc41ac4ec171d25f2ceaaf45b666a21a2250f3b6ae614'
with tempfile.TemporaryDirectory(prefix='orthophoto-compat-') as tmp:
 root=Path(tmp); p=root/NAME
 subprocess.run(['gh','release','download','odm-orthophoto-v0.0.0.dev20250225-b2','--repo','Archont561/ODM-conda','--pattern',NAME,'--dir',str(root)],check=True)
 if sha256(p)!=DIGEST: raise ValueError('published artifact hash mismatch')
 with zipfile.ZipFile(p) as z:
  m=next(x for x in z.namelist() if x.startswith('info-') and x.endswith('.tar.zst'))
  with z.open(m) as f, zstandard.ZstdDecompressor().stream_reader(f) as zf, tarfile.open(fileobj=zf,mode='r|') as tar:
   for item in tar:
    if item.name=='info/index.json' and item.isfile() and item.size<1024*1024:
     index=json.load(tar.extractfile(item));break
   else: raise ValueError('missing package index')
 dep=[d for d in index['depends'] if d.startswith('libopencv ')]
 if len(dep)!=1: raise ValueError('unexpected OpenCV dependency')
 channel=root/'channel'; create([p],channel)
 with loopback(channel,PORT) as url:
  run([rattler(),'test','--package-file',str(p),'--channel',url,'--channel','conda-forge','--channel-priority','strict','--output-dir',str(root/'retest'),'--log-style','plain'])
  print('::notice::ORTHO_RETEST_PASSED '+NAME,flush=True)
  project=root/'project'
  run(['pixi','init','--format','pixi','--scm','github','--channel',url,'--channel','conda-forge','--platform','linux-64',str(project)])
  cmd=['pixi','add','--manifest-path',str(project/'pixi.toml'),'odm-orthophoto==0.0.0.dev20250225','libopencv>=4.13,<4.14']
  result=subprocess.run(cmd,text=True,capture_output=True,timeout=600)
  msg=(result.stdout+'\n'+result.stderr)
  result_data={'package':NAME,'sha256':DIGEST,'declared_opencv':dep[0], 'tetraflow_host_opencv':'libopencv >=4.13,<4.14', 'retest_passed':True,'solver_exit_code':result.returncode,'solver_excerpt':msg[-2000:]}
  import base64,gzip
  data=base64.b64encode(gzip.compress(json.dumps(result_data,sort_keys=True).encode(),mtime=0)).decode()
  for i in range(0,len(data),1800):print('::notice::ORTHO%03d '%(i//1800)+data[i:i+1800],flush=True)
