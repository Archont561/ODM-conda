import hashlib, json, subprocess, tarfile, tempfile, urllib.request, zipfile
from pathlib import Path
import yaml, zstandard

inventory=json.loads(Path('research/tetraflow-build-input-inventory.json').read_text())
record=next(x for x in inventory['build'] if x['name']=='sysroot_linux-64')
result={'conda_sha256':record['sha256'],'inputs':[],'source_rpms':[]}
def download(url, path, expected=None):
 h=hashlib.sha256(); size=0
 with urllib.request.urlopen(url,timeout=90) as response, path.open('wb') as output:
  while b:=response.read(1024*1024):
   size+=len(b)
   if size>1024*1024*1024: raise ValueError('download too large')
   h.update(b); output.write(b)
 digest=h.hexdigest()
 if expected and digest!=expected: raise ValueError('sha256 mismatch')
 return digest,size

def rpmquery(path):
 return subprocess.check_output(['rpm','-qp','--qf','%{NAME}|%{VERSION}|%{RELEASE}|%{ARCH}|%{SOURCERPM}',str(path)],text=True,stderr=subprocess.DEVNULL).strip()
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp); package=d/'sysroot.conda'; download(record['binary_package_url'],package,record['sha256'])
 with zipfile.ZipFile(package) as z:
  n=next(n for n in z.namelist() if n.startswith('info-') and n.endswith('.tar.zst'))
  with z.open(n) as f, zstandard.ZstdDecompressor().stream_reader(f) as zf, tarfile.open(fileobj=zf,mode='r|') as tar:
   for m in tar:
    if m.name=='info/recipe/meta.yaml' and m.isfile() and m.size<1024*1024:
     recipe=yaml.safe_load(tar.extractfile(m).read()); break
   else: raise ValueError('missing embedded recipe')
 for item in recipe['source']:
  row={'url':item['url'],'declared_sha256':item['sha256']}
  try:
   path=d/'binary.rpm'; digest,size=download(item['url'],path,item['sha256'])
   row.update({'verified_sha256':digest,'bytes':size,'rpm_identity':rpmquery(path)})
  except Exception as e: row['error']=str(e)[:250]
  finally: (d/'binary.rpm').unlink(missing_ok=True)
  result['inputs'].append(row)
 source_names=sorted({x['rpm_identity'].split('|')[-1] for x in result['inputs'] if 'rpm_identity' in x})
 for name in source_names:
  row={'filename':name}
  try:
   if '/' in name or not name.endswith('.src.rpm'): raise ValueError('unexpected source RPM name')
   url='https://repo.almalinux.org/vault/8.9/BaseOS/Source/SPackages/'+name
   path=d/'source.rpm'; digest,size=download(url,path)
   row.update({'url':url,'observed_sha256':digest,'bytes':size,'rpm_identity':rpmquery(path)})
  except Exception as e: row['error']=str(e)[:250]
  finally: (d/'source.rpm').unlink(missing_ok=True)
  result['source_rpms'].append(row)
 print('::notice::SYSROOT_RESULT '+json.dumps(result,sort_keys=True,separators=(',',':')),flush=True)
