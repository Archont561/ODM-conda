import urllib.request,re
urls=['https://repo.almalinux.org/vault/8.9/BaseOS/Source/','https://repo.almalinux.org/vault/8.9/BaseOS/Source/Packages/','https://repo.almalinux.org/vault/8.9/BaseOS/Source/SPackages/','https://repo.almalinux.org/vault/8.9/BaseOS/Source/tree/','https://repo.almalinux.org/vault/8.9/']
for url in urls:
 try:
  with urllib.request.urlopen(url,timeout=35) as r: data=r.read(3000000).decode('utf8','replace')
  links=re.findall(r'href=["\']([^"\']+)',data,re.I)
  relevant=[x for x in links if any(t in x.lower() for t in ('glibc','kernel','package','source','tree','baseos'))]
  print('::notice::DIR '+url+' '+repr(relevant[:50])[:1800],flush=True)
 except Exception as e: print('::notice::DIRFAIL '+url+' '+str(e),flush=True)
