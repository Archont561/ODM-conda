import hashlib
import json
import re
import subprocess
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path
import yaml
import zstandard

from common import ROOT

names={'libjxl','libhwy','libbrotlidec','libbrotlienc','libbrotlicommon','libgcc','libstdcxx'}
inventory=json.loads((ROOT/'research/odm-alternate-candidate-2026-11-07/conda-inventory.json').read_text())['packages']
records=[p for p in inventory if p['name'] in names]
assert len(records)==len(names)
with tempfile.TemporaryDirectory(prefix='jxl-native-review-') as temp:
    root=Path(temp)
    for p in records:
        path=root/(p['name']+'.conda')
        with urllib.request.urlopen(p['binary_package_url'],timeout=90) as response:
            data=response.read(100_000_000)
        digest=hashlib.sha256(data).hexdigest()
        assert digest==p['sha256'], (p['name'],digest)
        path.write_bytes(data); info={}; elf={}; payload_notices={}
        with zipfile.ZipFile(path) as package:
            for group in ('info','pkg'):
                member=next(x for x in package.namelist() if x.startswith(group+'-') and x.endswith('.tar.zst'))
                with package.open(member) as compressed, zstandard.ZstdDecompressor().stream_reader(compressed) as stream, tarfile.open(fileobj=stream,mode='r|') as tar:
                    for item in tar:
                        if not item.isfile(): continue
                        name=item.name.removeprefix('./')
                        if group=='info' and (name in ('info/index.json','info/about.json') or name.startswith('info/recipe/') or name.startswith('info/licenses/')):
                            assert item.size<20_000_000
                            info[name]=tar.extractfile(item).read()
                        if group=='pkg' and re.search(r'(^|/)(licenses?|notices?|copying|copyright)(/|[.\-_]|$)', name, re.IGNORECASE):
                            if item.size < 2_000_000:
                                payload_notices[name]=hashlib.sha256(tar.extractfile(item).read()).hexdigest()
                        if group=='pkg' and p['name'] in {'libjxl','libhwy','libbrotlidec','libbrotlienc','libbrotlicommon'} and re.fullmatch(r'lib/lib[^/]+\.so\.\d+(?:\.\d+)*',name):
                            assert item.size<60_000_000
                            raw=tar.extractfile(item).read()
                            if not raw.startswith(b'\x7fELF'): continue
                            f=root/'tmp-elf'; f.write_bytes(raw)
                            dynamic=subprocess.run(['readelf','-d',str(f)],text=True,stdout=subprocess.PIPE,check=True).stdout
                            elf[name]=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dynamic)
        index=json.loads(info['info/index.json']); about=json.loads(info['info/about.json'])
        notices={k:hashlib.sha256(v).hexdigest() for k,v in info.items() if k.startswith('info/licenses/')}
        recipes={k:hashlib.sha256(v).hexdigest() for k,v in info.items() if k.startswith('info/recipe/')}
        source={}
        for key in ('info/recipe/rendered_recipe.yaml','info/recipe/recipe.yaml','info/recipe/meta.yaml'):
            if key in info:
                try:
                    parsed=yaml.safe_load(info[key]); parsed=parsed.get('recipe',parsed) if isinstance(parsed,dict) else {}; source=parsed.get('source',{}) if isinstance(parsed,dict) else {}; break
                except Exception as ex: source={'parse_error':type(ex).__name__}
        recipe_inventory_hash=hashlib.sha256(json.dumps(recipes,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        relevant={k:v for k,v in recipes.items() if p['name'] in {'libjxl','libhwy'} and ('patch' in k or k.endswith(('recipe.yaml','meta.yaml','install.sh')))}
        record={'name':p['name'],'version':p['version'],'build':p['build'],'sha256':digest,'license':about.get('license',index.get('license')),'depends':index.get('depends'), 'notices':notices,'payload_notices':payload_notices,'recipe_inventory_sha256':recipe_inventory_hash,'recipe_count':len(recipes),'selected_recipes':relevant,'source':source,'elf_needed':elf}

        text=json.dumps(record,separators=(',',':'),sort_keys=True)
        assert len(text)<3000, (p['name'],len(text))
        print(f'::notice::NATIVE-{p["name"]} '+text,flush=True)
