import base64
import collections
import gzip
import hashlib
import io
import json
import re
import subprocess
import tempfile
from pathlib import Path
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
            notice=None; recipe_files={}
            for m in t:
                if m.isfile() and m.name.startswith('info/recipe/') and (m.name.endswith('.sh') or m.name.endswith('.patch')) and m.size < 1000000:
                    recipe_files[m.name]=t.extractfile(m).read().decode('utf-8',errors='replace')
                if m.name=='info/licenses/COPYING':
                    assert m.isfile() and m.size < 1000000
                    notice=t.extractfile(m).read()
assert notice and digest(notice)==metadata['license_files']['info/licenses/COPYING']
with zipfile.ZipFile(io.BytesIO(pkg)) as z:
    payload=[n for n in z.namelist() if n.startswith('pkg-') and n.endswith('.tar.zst')]; assert len(payload)==1
    with z.open(payload[0]) as fp, zstandard.ZstdDecompressor().stream_reader(fp) as stream:
        with tarfile.open(fileobj=stream,mode='r|') as tar:
            elf=None; payload_notices=[]
            for m in tar:
                if m.isfile() and ('license' in m.name.lower() or 'copying' in m.name.lower()): payload_notices.append(m.name)
                if m.name=='lib/libspatialite.so.8.1.0':
                    assert m.isfile() and m.size < 100*1024*1024 and elf is None
                    elf=tar.extractfile(m).read()
assert elf
with tempfile.NamedTemporaryFile() as tmp:
    tmp.write(elf); tmp.flush()
    symbols=subprocess.check_output(['nm','-D','--defined-only',tmp.name],text=True)
    interesting=[line.strip() for line in symbols.splitlines() if re.search(r'control.?points|georef|I_compute|gaia.*(GCP|Control)',line,re.I)]

source=fetch(metadata['recipe_source']['url']); assert digest(source)==metadata['recipe_source']['sha256']
counts=collections.Counter(); examples={}; root_notices=[]; total=0; groups=collections.defaultdict(list); build_mentions=[]; target_files={}; gpl_excerpts={}
with tarfile.open(fileobj=io.BytesIO(source),mode='r:gz') as tar:
    for m in tar:
        if not m.isfile(): continue
        total+=1
        if m.size>2*1024*1024: continue
        path=m.name; name=path.rsplit('/',1)[-1].lower()
        if name in ('copying','license','license.txt','readme','readme.md','readme.txt') and (len(path.split('/'))==2 or '/src/control_points/' in path):
            raw=tar.extractfile(m).read()
            root_notices.append({'path':path,'sha256':digest(raw),'same_as_package_notice':raw==notice,'excerpt':raw[:800].decode('utf-8',errors='replace')})
        if path.endswith(('/src/Makefile.am','/src/control_points/Makefile.am')):
            target_files[path]=tar.extractfile(m).read().decode('utf-8',errors='replace')
        if name in ('makefile.am', 'configure.ac', 'cmakelists.txt'):
            content=tar.extractfile(m).read().decode('utf-8',errors='replace')
            lines=content.splitlines()
            relevant=[{'line':i+1,'text':line.strip()} for i,line in enumerate(lines) if re.search(r'control_points|grass_crs|grass_georef|epsg_update|code_generator',line,re.I)]
            if relevant: build_mentions.append({'path':path,'lines':relevant[:80]})
        if not name.endswith(('.c','.h','.cpp','.hpp')):continue
        text=tar.extractfile(m).read(12000).decode('utf-8',errors='replace')
        terms=[]
        if re.search(r'mozilla public license|mpl\s*(?:version\s*)?1[.]1',text,re.I): terms.append('MPL')
        if re.search(r'(?<!lesser )(?<!library )gnu general public license',text,re.I):terms.append('GPL')
        if re.search(r'gnu (?:lesser|library) general public license',text,re.I):terms.append('LGPL')
        k='+'.join(terms) if terms else 'no-marker-in-first-12000-bytes';counts[k]+=1;groups[k].append(path)
        if k == 'GPL' and '/src/control_points/' in path:
            match=re.search(r'gnu general public license',text,re.I)
            gpl_excerpts[path]=text[max(0,match.start()-150):match.start()+400]
        if terms and k not in examples:
            match=re.search(r'mozilla public license|gnu (?:lesser |library )?general public license',text,re.I)
            examples[k]={'path':path,'excerpt':text[max(0,match.start()-200):match.start()+1800]}
result={'binary_sha256':digest(pkg),'elf_sha256':digest(elf),'selected_dynamic_symbols':interesting,'payload_notice_paths':payload_notices,'source_sha256':digest(source),'package_license':record['license'],'package_copying_sha256':digest(notice),'total_regular_files':total,'source_scan_counts':dict(counts),'examples':examples,'selected_paths':{k:v[:80] for k,v in groups.items() if k != 'MPL+GPL+LGPL'},'build_mentions':build_mentions,'target_makefiles':target_files,'gpl_control_point_excerpts':gpl_excerpts,'package_recipe_files':recipe_files,'root_notices':root_notices,'warning':'Filename/header token scan is not a full source, license, provenance or compilation audit.'}
raw=json.dumps(result,sort_keys=True,indent=2).encode();enc=base64.b64encode(gzip.compress(raw,mtime=0)).decode();chunks=[enc[i:i+2700] for i in range(0,len(enc),2700)];assert len(chunks)<=40
print(f'::notice::SPATIALITE-INFO chunks={len(chunks)} sha256={digest(raw)}',flush=True)
for i,chunk in enumerate(chunks):print(f'::notice::SPATIALITE-CHUNK-{i:02d} {chunk}',flush=True)
