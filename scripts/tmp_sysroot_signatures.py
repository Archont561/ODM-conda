import base64,gzip,hashlib,json,subprocess,tempfile,urllib.request
from pathlib import Path

evidence=json.load(open('research/tetraflow-sysroot-rpm-evidence.json'))
key_url='https://repo.almalinux.org/almalinux/RPM-GPG-KEY-AlmaLinux'
primary='5E9B8F5617B5066CE92057C3488FCF7C3ABB34F8'
sub='E53CF5EF91CEB0AD1812ECB851D6647EC21AD6EA'
def cmd(*args):
 return subprocess.run(args,check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True).stdout
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp); key=d/'key'; urllib.request.urlretrieve(key_url,key)
 listing=cmd('gpg','--batch','--show-keys','--with-colons',str(key))
 fps=[l.split(':')[9] for l in listing.splitlines() if l.startswith('fpr:')]
 if not fps or fps[0]!=primary or sub not in fps: raise ValueError('key fingerprint mismatch')
 result_all={'key':{'url':key_url,'fingerprints':fps,'key_sha256':hashlib.sha256(key.read_bytes()).hexdigest()},'rpm_checks':[],'errors':[]}
 db=d/'rpmdb'; db.mkdir()
 cmd('rpm','--dbpath',str(db),'--initdb'); cmd('rpm','--dbpath',str(db),'--import',str(key))
 for item in evidence['source_rpm_checks']+evidence['binary_rpm_checks']:
  name=item.get('filename') or item['url'].rsplit('/',1)[-1]; path=d/'item.rpm'
  try:
   urllib.request.urlretrieve(item['url'],path)
   digest=hashlib.sha256(path.read_bytes()).hexdigest()
   expected=item.get('observed_sha256') or item['verified_sha256']
   if digest!=expected: raise ValueError('checksum mismatch')
   out=cmd('rpm','--dbpath',str(db),'-Kv',str(path))
   if 'NOKEY' in out or 'NOT OK' in out or not any('Signature' in l and 'OK' in l for l in out.splitlines()): raise ValueError('missing verified signature: '+out[-500:])
   result={'name':name,'sha256':digest,'signature_lines':[s.strip() for s in out.splitlines() if 'Signature' in s]}
   if name.endswith('.src.rpm'):
    files=cmd('rpm','--dbpath',str(db),'-qpl',str(path)).splitlines()
    result['file_count']=len(files); result['patch_count']=sum(x.lower().endswith(('.patch','.diff')) for x in files)
    result['spec_files']=[x for x in files if x.endswith('.spec')]
    result['first_files']=files[:8]
   result_all['rpm_checks'].append(result)
  except Exception as e: result_all['errors'].append({'name':name,'error':str(e)[:300]})
  finally: path.unlink(missing_ok=True)

 data=base64.b64encode(gzip.compress(json.dumps(result_all,sort_keys=True).encode(),mtime=0)).decode()
 for i in range(0,len(data),2000): print('::notice::CHUNK%03d '%(i//2000)+data[i:i+2000],flush=True)
 if result_all['errors'] or len(result_all['rpm_checks'])!=10: raise ValueError('one or more RPM checks failed')
