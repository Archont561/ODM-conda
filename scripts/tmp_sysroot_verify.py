import hashlib, json, subprocess, tarfile, tempfile, urllib.request, zipfile, gzip, bz2, lzma, xml.etree.ElementTree as ET
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
 kernel_record=next(x for x in inventory['build'] if x['name']=='kernel-headers_linux-64')
 kernel_package=d/'kernel-headers.conda'; download(kernel_record['binary_package_url'],kernel_package,kernel_record['sha256'])
 with zipfile.ZipFile(kernel_package) as z:
  n=next(n for n in z.namelist() if n.startswith('info-') and n.endswith('.tar.zst'))
  with z.open(n) as f, zstandard.ZstdDecompressor().stream_reader(f) as zf, tarfile.open(fileobj=zf,mode='r|') as tar:
   for m in tar:
    if m.name=='info/recipe/meta.yaml' and m.isfile() and m.size<1024*1024:
     kernel_recipe=yaml.safe_load(tar.extractfile(m).read()); break
   else: raise ValueError('missing kernel recipe')
 result['kernel_conda']={'sha256':kernel_record['sha256'],'sources_equal_sysroot':kernel_recipe['source']==recipe['source']}
 for item in recipe['source']:
  row={'url':item['url'],'declared_sha256':item['sha256']}
  try:
   path=d/'binary.rpm'; digest,size=download(item['url'],path,item['sha256'])
   row.update({'verified_sha256':digest,'bytes':size,'rpm_identity':rpmquery(path)})
  except Exception as e: row['error']=str(e)[:250]
  finally: (d/'binary.rpm').unlink(missing_ok=True)
  result['inputs'].append(row)
 repobase='https://repo.almalinux.org/vault/8.9/BaseOS/Source/'
 metadata={}
 try:
  repomd=urllib.request.urlopen(repobase+'repodata/repomd.xml',timeout=90).read()
  xml=ET.fromstring(repomd); ns={'r':'http://linux.duke.edu/metadata/repo'}
  primary=xml.find("r:data[@type='primary']",ns)
  primary_location=primary.find('r:location',ns).attrib['href']
  expected=primary.find('r:checksum',ns).text
  raw=urllib.request.urlopen(repobase+primary_location,timeout=90).read()
  if hashlib.sha256(raw).hexdigest()!=expected: raise ValueError('primary metadata hash mismatch')
  if primary_location.endswith('.gz'): raw=gzip.decompress(raw)
  elif primary_location.endswith('.bz2'): raw=bz2.decompress(raw)
  elif primary_location.endswith('.xz'): raw=lzma.decompress(raw)
  else: raise ValueError('unknown primary compression')
  root=ET.fromstring(raw); c={'c':'http://linux.duke.edu/metadata/common'}
  for package in root.findall('c:package',c):
   location=package.find('c:location',c).attrib['href']; check=package.find('c:checksum',c)
   if check.attrib.get('type')=='sha256': metadata[location.rsplit('/',1)[-1]]=check.text
  result['repo_metadata']={'repomd_observed_sha256':hashlib.sha256(repomd).hexdigest(),'primary_sha256':expected,'primary_location':primary_location}
 except Exception as e: result['repo_metadata']={'error':str(e)[:250]}
 source_names=sorted({x['rpm_identity'].split('|')[-1] for x in result['inputs'] if 'rpm_identity' in x})
 for name in source_names:
  row={'filename':name}
  try:
   if '/' in name or not name.endswith('.src.rpm'): raise ValueError('unexpected source RPM name')
   url='https://repo.almalinux.org/vault/8.9/BaseOS/Source/Packages/'+name
   path=d/'source.rpm'; expected=metadata.get(name); digest,size=download(url,path,expected)
   row.update({'url':url,'observed_sha256':digest,'repository_sha256':expected,'bytes':size,'rpm_identity':rpmquery(path)})
  except Exception as e: row['error']=str(e)[:250]
  finally: (d/'source.rpm').unlink(missing_ok=True)
  result['source_rpms'].append(row)
 print('::notice::CONDA '+result['conda_sha256'],flush=True)
 print('::notice::KERNEL_CONDA '+json.dumps(result['kernel_conda'],sort_keys=True),flush=True)
 print('::notice::REPOMD '+json.dumps(result['repo_metadata'],sort_keys=True),flush=True)
 for row in result['source_rpms']: print('::notice::SRPM '+json.dumps(row,sort_keys=True),flush=True)
 for row in result['inputs']: print('::notice::INPUT '+json.dumps(row,sort_keys=True),flush=True)
