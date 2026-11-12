import hashlib, json, tarfile, tempfile, urllib.request
from pathlib import Path

sources={
 'cgal':('https://github.com/CGAL/cgal/releases/download/v6.2.1/CGAL-6.2.1.tar.xz','b6be77c60765a8456335de991eeaf6ffec55256984e4a9ecc6a97c37bbfe85bf'),
 'gcc-14':('https://ftp.gnu.org/gnu/gcc/gcc-14.4.0/gcc-14.4.0.tar.gz','f35aa1c7f14e6bbe5a7fab83abcb7813449aa1dc6d38bbf27b74614dee17db5e'),
 'gcc-16':('https://ftp.gnu.org/gnu/gcc/gcc-16.2.0/gcc-16.2.0.tar.gz','071d00a097579e5ef7ce97fc4a9e58e73fd3503c0a013c765c970370a5a53b9b'),
 'binutils':('https://ftp.gnu.org/gnu/binutils/binutils-2.46.1.tar.bz2','324ed40ada2633a28eaa5d104ca5db165fd3cc3162cc1d48a7b7fa9c932da439'),
 'zlib':('https://github.com/madler/zlib/releases/download/v1.3.1/zlib-1.3.1.tar.gz','9a93b2b7dfdac77ceba5a558a580e74667dd6fede4585b91eefb60f03b72df23'),
}
with tempfile.TemporaryDirectory() as d:
 for name,(url,expected) in sources.items():
  try:
   path=Path(d)/name; h=hashlib.sha256(); size=0
   with urllib.request.urlopen(url,timeout=90) as r, path.open('wb') as f:
    while b:=r.read(1024*1024):
     size+=len(b)
     if size>1024*1024*1024: raise ValueError('download limit exceeded')
     h.update(b); f.write(b)
   got=h.hexdigest()
   if got!=expected: raise ValueError('SHA256 mismatch '+got)
   counts={'files':0,'directories':0,'links':0,'other':0}; roots=set(); total=0
   with tarfile.open(path,'r:*') as a:
    for m in a:
     total+=1
     if total>1000000: raise ValueError('member limit exceeded')
     roots.add(m.name.split('/')[0])
     if len(roots)>10: raise ValueError('unexpected roots')
     if m.isfile(): counts['files']+=1
     elif m.isdir(): counts['directories']+=1
     elif m.issym() or m.islnk(): counts['links']+=1
     else: counts['other']+=1
   print('::notice::SOURCECHECK '+json.dumps({'name':name,'sha256':got,'bytes':size,'roots':sorted(roots),'counts':counts},sort_keys=True),flush=True)
  except Exception as e:
   print('::notice::SOURCEERROR '+json.dumps({'name':name,'error':str(e)[:300]}),flush=True)
  finally: path.unlink(missing_ok=True)
