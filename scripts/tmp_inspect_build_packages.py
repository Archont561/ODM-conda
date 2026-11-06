import base64
import gzip
import hashlib
import io
import json
import tarfile
import urllib.request
import zipfile
import yaml
import zstandard

selected = {'gcc_impl_linux-64','gxx_impl_linux-64','binutils_impl_linux-64','sysroot_linux-64','kernel-headers_linux-64','cmake','python','ninja'}
records = json.load(open('release-artifacts/build-host-inventory.json'))['environments']['build']['packages']
result = {}
for item in records:
    if item['name'] not in selected: continue
    url = item['binary_package_url']
    assert url.startswith('https://conda.anaconda.org/conda-forge/')
    with urllib.request.urlopen(url, timeout=120) as response: binary = response.read(200*1024*1024+1)
    assert len(binary) <= 200*1024*1024 and hashlib.sha256(binary).hexdigest() == item['sha256']
    files = {}
    with zipfile.ZipFile(io.BytesIO(binary)) as outer:
        infos = [p for p in outer.namelist() if p.startswith('info-') and p.endswith('.tar.zst')]
        assert len(infos)==1
        with outer.open(infos[0]) as compressed, zstandard.ZstdDecompressor().stream_reader(compressed) as stream:
            with tarfile.open(fileobj=stream, mode='r|') as tar:
                for member in tar:
                    if member.isfile() and (member.name in ('info/about.json', 'info/recipe/recipe.yaml', 'info/recipe/meta.yaml') or member.name.startswith('info/licenses/')):
                        assert member.size <= 5*1024*1024 and member.name not in files
                        files[member.name] = tar.extractfile(member).read()
    about = json.loads(files['info/about.json']) if 'info/about.json' in files else {}
    recipe = next((p for p in ('info/recipe/recipe.yaml','info/recipe/meta.yaml') if p in files), None)
    source = None
    if recipe:
        try: source = yaml.safe_load(files[recipe]).get('source')
        except (yaml.YAMLError,AttributeError): pass
    result[item['name']] = {'version':item['version'], 'build':item['build'], 'sha256':item['sha256'], 'binary_package_url':url, 'license':item['license'], 'about':{k:about.get(k) for k in ('home','dev_url','license','license_family','license_url')}, 'recipe_source':source, 'license_files':{k:hashlib.sha256(v).hexdigest() for k,v in files.items() if k.startswith('info/licenses/')}}
assert set(result) == selected
raw = json.dumps(result, sort_keys=True, indent=2).encode()
encoded = base64.b64encode(gzip.compress(raw, mtime=0)).decode()
chunks = [encoded[i:i+2700] for i in range(0,len(encoded),2700)]
assert len(chunks)<=30
print(f'::notice::TOOLS-INFO chunks={len(chunks)} sha256={hashlib.sha256(raw).hexdigest()}',flush=True)
for i, chunk in enumerate(chunks): print(f'::notice::TOOLS-CHUNK-{i:02d} {chunk}',flush=True)
