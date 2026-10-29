import hashlib, json, tarfile, tempfile, zipfile
from pathlib import Path
from common import config
from audit_package import audit
from package_archive import read_package

expected='44c7723e16c9d1bc40e9b1634578836657c02ff4eebf6d13d363146f850903bf'
raw=Path('/tmp/license-artifact.zip').read_bytes()
assert hashlib.sha256(raw).hexdigest()==expected
with zipfile.ZipFile('/tmp/license-artifact.zip') as z:
 names=z.namelist(); print('Artifact members:',names)
 packages=[n for n in names if n.endswith('.conda')]
 bundles=[n for n in names if n.endswith('.tar.gz')]
 assert len(packages)==len(bundles)==1 and 'poissonrecon-odm' in packages[0] and 'poissonrecon-odm' in bundles[0]
 with tempfile.TemporaryDirectory() as temp:
  p=Path(temp)/Path(packages[0]).name;p.write_bytes(z.read(packages[0]))
  result=audit('poissonrecon-odm',config()['components']['poissonrecon-odm'],p)
  info,payload=read_package(p)
  print('Audit:',json.dumps(result,sort_keys=True))
  print('Notice files:',*[k for k in sorted(info) if k.startswith('info/licenses/')],sep='\n')
  p=Path(temp)/'bundle.tar.gz';p.write_bytes(z.read(bundles[0])); print('Source bundle SHA256:',hashlib.sha256(p.read_bytes()).hexdigest())
  with tarfile.open(p) as a:
   m=json.load(a.extractfile('SOURCE-MANIFEST.json'))
   assert not m['packaging_dirty'] and m['packaging_commit']=='ec83f085461b30c99e3b2f5d6f362c92da8c103d'
   for n,h in m['files'].items(): assert hashlib.sha256(a.extractfile(n).read()).hexdigest()==h,n
   print('Verified source manifest entries:',len(m['files']))
   for n in ('packaging/research/notices/ijg-6b-README.txt','packaging/research/notices/ijg-6b-poisson-differences.json'):
    print(n,m['files'][n])
