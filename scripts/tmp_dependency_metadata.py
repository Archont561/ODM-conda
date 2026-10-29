import hashlib,io,json,tarfile,tempfile,urllib.request,zipfile
from pathlib import Path
import zstandard

packages={
'libgdal-core-3.12.2-h4f65170_3.conda':'7ea31130adc61b2cda72c02f51086deec699bb30ec6f51b37b6c67d02c93d061',
'libopencv-4.12.0-qt6_py313hbb662ea_612.conda':'4f28a2b341b24804cc60480e46b28986bd29dfe744856fa52d005c16d03dde76',
'libopenvino-2025.4.1-hb56ce9e_1.conda':'d85e5e3b6dc56d6fdfe0c51a8af92407a7ef4fc5584d0e172d059033b8d6d3e0',
'libopenvino-pytorch-frontend-2025.4.1-hecca717_1.conda':'5edd997be35bbdda6c8916de46a4ae7f321af6a6b07ba136228404cb713bcbe9',
}
for name,digest in packages.items():
 url='https://conda.anaconda.org/conda-forge/linux-64/'+name
 with tempfile.TemporaryDirectory() as d:
  p=Path(d)/name
  with urllib.request.urlopen(url) as source,p.open('wb') as target:
   while chunk:=source.read(1024*1024):target.write(chunk)
  assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
  with zipfile.ZipFile(p) as z:
   part=next(x for x in z.namelist() if x.startswith('info-') and x.endswith('.tar.zst'))
   with z.open(part) as f,zstandard.ZstdDecompressor().stream_reader(f) as decomp,tarfile.open(fileobj=decomp,mode='r|') as tar:
    meta={}; notices=[]
    for m in tar:
     if m.isfile() and m.name in ('info/index.json','info/about.json'):
      meta[m.name]=json.load(tar.extractfile(m))
     elif m.isfile() and m.name.startswith('info/licenses/'):
      fp=tar.extractfile(m); notices.append([m.name,hashlib.sha256(fp.read()).hexdigest()])
  about=meta.get('info/about.json',{}); index=meta.get('info/index.json',{})
  print('::notice::METADATA '+json.dumps({'name':name,'sha256':digest,'index_license':index.get('license'),'about_license':about.get('license'),'license_family':about.get('license_family'),'source_url':about.get('dev_url') or about.get('home'),'notices':notices},separators=(',',':')),flush=True)
