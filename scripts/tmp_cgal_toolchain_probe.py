import base64, gzip, hashlib, json, tarfile, tempfile, urllib.request, zipfile
from pathlib import Path
import yaml, zstandard

names = {'cgal-cpp','gcc_impl_linux-64','gxx_impl_linux-64','binutils_impl_linux-64','sysroot_linux-64','kernel-headers_linux-64','libgcc','libgcc-devel_linux-64'}
x=json.loads(Path('research/tetraflow-build-input-inventory.json').read_text())
records={p['name']:p for group in ('build','host') for p in x[group] if p['name'] in names}
out={}
with tempfile.TemporaryDirectory() as d:
 for name,p in sorted(records.items()):
  try:
   path=Path(d)/p['fn']; urllib.request.urlretrieve(p['binary_package_url'],path)
   digest=hashlib.sha256()
   with path.open('rb') as f:
    while b:=f.read(1024*1024): digest.update(b)
   if digest.hexdigest()!=p['sha256']: raise ValueError('binary checksum mismatch')
   info={}
   with zipfile.ZipFile(path) as z:
    members=[n for n in z.namelist() if n.startswith('info-') and n.endswith('.tar.zst') and '/' not in n]
    if len(members)!=1: raise ValueError('unexpected info archive count')
    with z.open(members[0]) as f, zstandard.ZstdDecompressor().stream_reader(f) as zf, tarfile.open(fileobj=zf,mode='r|') as tar:
     for m in tar:
      if m.isfile() and m.name.startswith('info/recipe/') and m.size<=4*1024*1024:
       if m.name.endswith(('meta.yaml','rendered_recipe.yaml','recipe.yaml')) or '/patches/' in m.name:
        data=tar.extractfile(m).read(); info[m.name]=data
   sources={}; patches={}
   for k,v in info.items():
    if '/patches/' in k: patches[k]=hashlib.sha256(v).hexdigest(); continue
    try:
     recipe=yaml.safe_load(v)
     if isinstance(recipe,dict):
      s=recipe.get('finalized_sources') or recipe.get('source') or (recipe.get('recipe') or {}).get('source')
      if s: sources[k]=s
    except Exception: pass
   out[name]={'binary_sha256':p['sha256'],'sources':sources,'patches':patches}
  except Exception as e: out[name]={'error':str(e)}
  finally:
   if 'path' in locals(): path.unlink(missing_ok=True)
encoded=base64.b64encode(gzip.compress(json.dumps(out,sort_keys=True).encode(),mtime=0)).decode()
print('::notice::RESULTCHUNKS '+str((len(encoded)+2500-1)//2500),flush=True)
for i in range(0,len(encoded),2500): print(f'::notice::RESULT{i//2500:03} {encoded[i:i+2500]}',flush=True)
