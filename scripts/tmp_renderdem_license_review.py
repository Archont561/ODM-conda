import base64
import gzip
import hashlib
import io
import json
import re
import tarfile
import urllib.error
import urllib.request
import zipfile
import zstandard
from pathlib import PurePosixPath

inv=json.load(open('research/renderdem-runtime-closure-2026-11-06.json'))
wanted={'lzo':'https://www.oberhumer.com/opensource/lzo/download/lzo-2.10.tar.gz','librttopo':'https://www.gaia-gis.it/gaia-sins/librttopo-1.1.0.tar.gz'}
def digest(data): return hashlib.sha256(data).hexdigest()
def fetch(url):
    request=urllib.request.Request(url,headers={'User-Agent':'ODM-conda-evidence-review/1'})
    with urllib.request.urlopen(request,timeout=60) as r:
        data=r.read(50*1024*1024+1)
        assert len(data)<=50*1024*1024
        return data
result={}
for name,url in wanted.items():
    record=next(p for p in inv['runtime_inventory']['packages'] if p['name']==name)
    pkg=fetch(record['binary_package_url']); assert digest(pkg)==record['sha256']
    with zipfile.ZipFile(io.BytesIO(pkg)) as z:
        info=[n for n in z.namelist() if n.startswith('info-') and n.endswith('.tar.zst')]; assert len(info)==1
        with z.open(info[0]) as fp, zstandard.ZstdDecompressor().stream_reader(fp) as stream:
            with tarfile.open(fileobj=stream,mode='r|') as t:
                for m in t:
                    if m.name=='info/licenses/COPYING':
                        assert m.isfile() and m.size < 1000000
                        notice=t.extractfile(m).read()
    assert digest(notice)==inv['reviewed_dependency_metadata'][name]['license_files']['info/licenses/COPYING']
    item={'binary_sha256':record['sha256'],'license_metadata':record['license'],'package_notice_sha256':digest(notice),'source_url':url}
    try: source=fetch(url)
    except (urllib.error.URLError, TimeoutError) as e:
        item['source_download_error']=str(e)[:300]; result[name]=item; continue
    expected=inv['reviewed_dependency_metadata'][name]['recipe_source']['sha256']
    assert digest(source)==expected
    item['source_archive_sha256']=digest(source)
    hits=[]; copying=[]; count=0
    with tarfile.open(fileobj=io.BytesIO(source),mode='r:gz') as tar:
        for m in tar:
            if not m.isfile(): continue
            count+=1
            if m.size>2*1024*1024: continue
            filename=PurePosixPath(m.name).name.lower()
            if filename not in ('copying','license','license.txt','readme','readme.md','readme.txt') and not filename.endswith(('.c','.cc','.cpp','.h','.hpp')): continue
            raw=tar.extractfile(m).read()
            if filename in ('copying','license','license.txt'):
                copying.append({'file':m.name,'sha256':digest(raw),'same_as_package_notice':raw==notice})
            text=raw.decode('utf-8',errors='replace')
            if re.search(r'(?is)(?:version\s+2|version\s+two).{0,100}(?:or\s+(?:at\s+your\s+option\s+)?any\s+later\s+version)', text):
                if len(hits)<12:
                    lines=text.splitlines(); matching=[l.strip() for l in lines if re.search(r'version\s+2|any\s+later\s+version',l,re.I)][:4]
                    hits.append({'file':m.name,'lines':matching})
    item.update(source_regular_files=count,license_files=copying,version_2_or_later_examples=hits)
    result[name]=item
raw=json.dumps(result,indent=2,sort_keys=True).encode(); encoded=base64.b64encode(gzip.compress(raw,mtime=0)).decode();chunks=[encoded[i:i+2700] for i in range(0,len(encoded),2700)]
assert len(chunks)<=40
print(f'::notice::LICENSE-INFO chunks={len(chunks)} sha256={digest(raw)}',flush=True)
for i,c in enumerate(chunks):print(f'::notice::LICENSE-CHUNK-{i:02d} {c}',flush=True)
