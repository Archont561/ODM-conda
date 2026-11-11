import base64
import hashlib
import io
import json
import re
import subprocess
import tarfile
import tempfile
import tomllib
import urllib.parse
import urllib.request
import zlib
from pathlib import Path
from common import ROOT
from private_odm_bundle import download_sdist
from prepare_jxl_source import SOURCE_SHA256, prepare

URL='https://files.pythonhosted.org/packages/0a/0e/77af926bdf99bac7f1decdca8102b13945a2e2aa9c716ce617e36bcd82d3/pillow_jxl_plugin-1.3.4.tar.gz'
with tempfile.TemporaryDirectory(prefix='jxl-crate-review-') as tmp:
    root=Path(tmp); archive=root/'source.tar.gz'
    download_sdist(URL, SOURCE_SHA256, archive)
    prepare(archive,root/'prepared')
    source=root/'prepared/source'
    lock=tomllib.loads((source/'Cargo.lock').read_text())
    crates=[x for x in lock['package'] if 'source' in x]
    assert len(crates)==40
    records=[]
    for item in crates:
        name,version=item['name'],item['version']
        url='https://static.crates.io/crates/'+urllib.parse.quote(name,safe='')+'/'+urllib.parse.quote(f'{name}-{version}.crate',safe='')
        with urllib.request.urlopen(url,timeout=90) as response:
            data=response.read(32*1024*1024+1)
        assert len(data)<=32*1024*1024 and hashlib.sha256(data).hexdigest()==item['checksum'],name
        with tarfile.open(fileobj=io.BytesIO(data),mode='r:gz') as tar:
            files={m.name:m for m in tar if m.isfile()}
            path=f'{name}-{version}/Cargo.toml'; assert path in files,(name,path)
            manifest=tomllib.loads(tar.extractfile(files[path]).read().decode())
            pkg=manifest['package']
            assert pkg['name']==name and pkg['version']==version
            notices={}
            for path,member in files.items():
                rel=path.split('/',1)[-1]
                if '/' not in rel and re.search(r'^(licen[sc]e|copying|notice|unlicense)([.\-_]|$)',rel,re.I):
                    assert member.size<1024*1024
                    notices[rel]=hashlib.sha256(tar.extractfile(member).read()).hexdigest()
            records.append({'name':name,'version':version,'sha256':item['checksum'],'manifest_license':pkg.get('license'),'manifest_license_file':pkg.get('license-file'),'notice_sha256':notices})
    tree=subprocess.check_output(['cargo','tree','--locked','--offline','--target','x86_64-unknown-linux-gnu','--no-default-features','--features','pyo3/extension-module,dynamic','--edges','normal,build','--prefix','none','--format','{p}'],cwd=source,text=True)
    lines=sorted(set(tree.splitlines()))
    payload={'scope':'Research-only, 40 independently downloaded crate archives verified against pinned Cargo.lock; Cargo.toml declarations and root notice filenames/hashes are metadata, not full notice, license, source, linkage or legal review. Tree is resolution, not proof of linked code.','source_sha256':SOURCE_SHA256,'target':'x86_64-unknown-linux-gnu','features':['pyo3/extension-module','dynamic'],'cargo_tree':lines,'crates':records}
    data=(json.dumps(payload,sort_keys=True,indent=2)+'\n').encode()
    b64=base64.b64encode(zlib.compress(data,9)).decode()
    chunks=[b64[i:i+2800] for i in range(0,len(b64),2800)]
    assert len(chunks)<=8
    print('::notice::JXL-INFO '+json.dumps({'sha256':hashlib.sha256(data).hexdigest(),'chunks':len(chunks),'crates':len(records),'tree_lines':len(lines)},separators=(',',':')),flush=True)
    for i,chunk in enumerate(chunks):print(f'::notice::JXL-CHUNK-{i:02d}:{chunk}',flush=True)
