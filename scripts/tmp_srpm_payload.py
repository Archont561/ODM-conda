import hashlib,json,os,stat,subprocess,tempfile,urllib.request
from pathlib import Path,PurePosixPath

records=json.loads(Path('research/tetraflow-sysroot-rpm-evidence.json').read_text())['source_rpm_checks']
def exact(stream, n):
 data=bytearray()
 while len(data)<n:
  buf=stream.read(n-len(data))
  if not buf: raise ValueError('truncated cpio')
  data.extend(buf)
 return bytes(data)
def inspect(path):
 proc=subprocess.Popen(['rpm2cpio',str(path)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 stream=proc.stdout; files={}; total=0; count=0; trailer=False
 try:
  while True:
   head=exact(stream,110)
   if head[:6] not in (b'070701',b'070702'): raise ValueError('invalid cpio magic')
   v=[int(head[6+i*8:14+i*8],16) for i in range(13)]
   mode,nlink,size,namesize=v[1],v[4],v[6],v[11]
   if not 1<=namesize<=4096 or size>512*1024*1024: raise ValueError('member limit')
   raw=exact(stream,namesize)
   if not raw.endswith(b'\0'): raise ValueError('invalid name')
   name=raw[:-1].decode('utf-8'); exact(stream,(-(110+namesize))%4)
   if name=='TRAILER!!!': trailer=True; break
   parts=PurePosixPath(name).parts
   if not name or name.startswith('/') or '\\' in name or '..' in parts or name in files: raise ValueError('unsafe or duplicate name')
   if not stat.S_ISREG(mode) or nlink!=1: raise ValueError('unsupported member type or links')
   count+=1;total+=size
   if count>5000 or total>1024*1024*1024: raise ValueError('archive limit')
   digest=hashlib.sha256(); remain=size
   while remain:
    chunk=exact(stream,min(remain,1024*1024));digest.update(chunk);remain-=len(chunk)
   exact(stream,(-size)%4)
   files[name]={'sha256':digest.hexdigest(),'size':size}
  if not trailer or proc.wait(timeout=30)!=0: raise ValueError('rpm2cpio failure')
 finally:
  if proc.poll() is None: proc.kill();proc.wait()
 patches={k:v for k,v in sorted(files.items()) if k.lower().endswith(('.patch','.diff'))}
 manifest=json.dumps(dict(sorted(files.items())),sort_keys=True,separators=(',',':')).encode()
 patch_manifest=json.dumps(patches,sort_keys=True,separators=(',',':')).encode()
 return {'file_count':count,'uncompressed_bytes':total,'file_manifest_sha256':hashlib.sha256(manifest).hexdigest(),'patch_count':len(patches),'patch_manifest_sha256':hashlib.sha256(patch_manifest).hexdigest(),'specs':{k:v for k,v in files.items() if k.endswith('.spec')},'archives':{k:v for k,v in files.items() if k.endswith(('.tar.gz','.tar.xz','.tar.bz2','.tar.zst'))},'sample_patches':dict(list(patches.items())[:3])}
with tempfile.TemporaryDirectory() as tmp:
 for rec in records:
  path=Path(tmp)/'source.rpm'
  try:
   urllib.request.urlretrieve(rec['url'],path)
   h=hashlib.sha256()
   with path.open('rb') as f:
    while chunk:=f.read(1024*1024): h.update(chunk)
   if h.hexdigest()!=rec['observed_sha256']: raise ValueError('RPM SHA mismatch')
   result=inspect(path); result['source_rpm']=rec['filename']; result['source_rpm_sha256']=rec['observed_sha256']
   print('::notice::PAYLOAD '+json.dumps(result,sort_keys=True),flush=True)
  except Exception as e:
   print('::notice::PAYLOADERROR '+json.dumps({'name':rec['filename'],'error':str(e)[:300]}),flush=True)
  finally: path.unlink(missing_ok=True)
