import base64
import collections
import gzip
import hashlib
import io
import json
import re
import tarfile
import urllib.request
import zipfile
import zstandard

inventory = json.load(open('research/renderdem-runtime-closure-2026-11-06.json'))
record = next(i for i in inventory['runtime_inventory']['packages'] if i['name'] == 'libspatialite')
metadata = inventory['reviewed_dependency_metadata']['libspatialite']
def digest(data): return hashlib.sha256(data).hexdigest()
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'ODM-conda-evidence-review/1'}),timeout=120) as r:
        data=r.read(100*1024*1024+1)
        assert len(data)<=100*1024*1024
        return data
pkg=fetch(record['binary_package_url']); assert digest(pkg)==record['sha256']
with zipfile.ZipFile(io.BytesIO(pkg)) as z:
    info=[n for n in z.namelist() if n.startswith('info-') and n.endswith('.tar.zst')]; assert len(info)==1
    with z.open(info[0]) as fp, zstandard.ZstdDecompressor().stream_reader(fp) as stream:
        with tarfile.open(fileobj=stream,mode='r|') as t:
            notice=None
            for m in t:
                if m.name=='info/licenses/COPYING':
                    assert m.isfile() and m.size < 1000000
                    notice=t.extractfile(m).read()
assert notice and digest(notice)==metadata['license_files']['info/licenses/COPYING']
source=fetch(metadata['recipe_source']['url']); assert digest(source)==metadata['recipe_source']['sha256']
counts=collections.Counter(); examples={}; root_notices=[]; total=0
with tarfile.open(fileobj=io.BytesIO(source),mode='r:gz') as tar:
    for m in tar:
        if not m.isfile(): continue
        total+=1
        if m.size>2*1024*1024: continue
        path=m.name; name=path.rsplit('/',1)[-1].lower()
        if name in ('copying','license','license.txt','readme','readme.md','readme.txt') and len(path.split('/'))==2:
            raw=tar.extractfile(m).read()
            root_notices.append({'path':path,'sha256':digest(raw),'same_as_package_notice':raw==notice,'excerpt':raw[:800].decode('utf-8',errors='replace')})
        if not name.endswith(('.c','.h','.cpp','.hpp')):continue
        text=tar.extractfile(m).read(12000).decode('utf-8',errors='replace')
        terms=[]
        if re.search(r'mozilla public license|mpl\s*(?:version\s*)?1[.]1',text,re.I): terms.append('MPL')
        if re.search(r'(?<!lesser )(?<!library )gnu general public license',text,re.I):terms.append('GPL')
        if re.search(r'gnu (?:lesser|library) general public license',text,re.I):terms.append('LGPL')
        k='+'.join(terms) if terms else 'no-marker-in-first-12000-bytes';counts[k]+=1
        if terms and k not in examples:
            match=re.search(r'mozilla public license|gnu (?:lesser |library )?general public license',text,re.I)
            examples[k]={'path':path,'excerpt':text[max(0,match.start()-200):match.start()+800]}
result={'binary_sha256':digest(pkg),'source_sha256':digest(source),'package_license':record['license'],'package_copying_sha256':digest(notice),'total_regular_files':total,'source_scan_counts':dict(counts),'examples':examples,'root_notices':root_notices,'warning':'Filename/header token scan is not a full source, license, provenance or compilation audit.'}
raw=json.dumps(result,sort_keys=True,indent=2).encode();enc=base64.b64encode(gzip.compress(raw,mtime=0)).decode();chunks=[enc[i:i+2700] for i in range(0,len(enc),2700)];assert len(chunks)<=40
print(f'::notice::SPATIALITE-INFO chunks={len(chunks)} sha256={digest(raw)}',flush=True)
for i,chunk in enumerate(chunks):print(f'::notice::SPATIALITE-CHUNK-{i:02d} {chunk}',flush=True)
