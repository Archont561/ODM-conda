import base64
import gzip
import hashlib
import json
import os
import sys
import io
import tarfile
import urllib.request
import zstandard
import yaml
import zipfile
from pathlib import Path
from inventory_conda_environment import inventory
from package_archive import read_package
from private_conda_channel import create

root = Path(os.environ['RUNNER_TEMP'])
package_name = 'renderdem-1.0-h873e7db_1.conda'
expected_zip = 'cd2671e9f6184102887b08b01f843309210c2fddad7825439bb05e8f7bdd2385'
expected_package = 'a681202611aa3fa25281055825b75a89e1a256260a954ce69bcd5393a834d94c'

def digest(data): return hashlib.sha256(data).hexdigest()

if sys.argv[1] == 'prepare':
    original = (root/'original.zip').read_bytes()
    assert digest(original) == expected_zip
    with zipfile.ZipFile(root/'original.zip') as archive:
        names = [name for name in archive.namelist() if name.endswith('/'+package_name) or name == package_name]
        assert len(names) == 1 and len(archive.namelist()) == len(set(archive.namelist()))
        binary = archive.read(names[0])
    assert digest(binary) == expected_package
    package = root/package_name
    package.write_bytes(binary)
    info, _ = read_package(package)
    saved = {k: v.decode() for k, v in info.items() if k in ('info/index.json', 'info/about.json', 'info/recipe/recipe.yaml', 'info/recipe/variant_config.yaml', 'info/hash_input.json')}
    (root/'package-metadata.json').write_text(json.dumps(saved))
    create([package], root/'channel')
    project = root/'runtime'
    project.mkdir()
    (project/'pixi.toml').write_text('[workspace]\nname = "renderdem-closure"\nversion = "0.1.0"\nchannels = ["'+(root/'channel').as_uri()+'", "conda-forge"]\nplatforms = ["linux-64"]\n\n[dependencies]\nrenderdem = "==1.0"\n')
elif sys.argv[1] == 'report':
    data = inventory(root/'runtime/.pixi/envs/default')
    matching = [r for r in data['packages'] if r['name'] == 'renderdem']
    assert len(matching) == 1 and matching[0]['sha256'] == expected_package
    review = {}
    selected = {'libpdal-core', 'libgdal-core', 'libarchive', 'libspatialite', 'librttopo', 'lzo', 'readline', 'geos', 'libgcc', 'libgomp', 'libstdcxx'}
    for record in data['packages']:
        if record['name'] not in selected:
            continue
        url = record['binary_package_url']
        assert url.startswith('https://conda.anaconda.org/conda-forge/')
        with urllib.request.urlopen(url, timeout=120) as response:
            raw_package = response.read(150 * 1024 * 1024 + 1)
        assert len(raw_package) <= 150 * 1024 * 1024 and digest(raw_package) == record['sha256']
        info_files = {}
        with zipfile.ZipFile(io.BytesIO(raw_package)) as package:
            candidates = [x for x in package.namelist() if x.startswith('info-') and x.endswith('.tar.zst')]
            assert len(candidates) == 1
            with package.open(candidates[0]) as stream, zstandard.ZstdDecompressor().stream_reader(stream) as decoded:
                with tarfile.open(fileobj=decoded, mode='r|') as archive:
                    for member in archive:
                        if member.isfile() and (member.name in ('info/about.json', 'info/index.json', 'info/recipe/recipe.yaml', 'info/recipe/meta.yaml') or member.name.startswith('info/licenses/')):
                            assert member.size <= 5 * 1024 * 1024 and member.name not in info_files
                            info_files[member.name] = archive.extractfile(member).read()
        about = json.loads(info_files['info/about.json']) if 'info/about.json' in info_files else {}
        index = json.loads(info_files['info/index.json'])
        recipe_name = next((n for n in ('info/recipe/recipe.yaml', 'info/recipe/meta.yaml') if n in info_files), None)
        recipe_source = None
        if recipe_name:
            try:
                recipe_source = yaml.safe_load(info_files[recipe_name]).get('source')
            except (yaml.YAMLError, AttributeError):
                pass
        review[record['name']] = {'sha256': record['sha256'], 'index_depends': index.get('depends', []), 'about': {k: about.get(k) for k in ('license', 'license_family', 'license_url', 'home', 'dev_url', 'summary')}, 'recipe_source': recipe_source, 'license_files': {n: digest(v) for n,v in info_files.items() if n.startswith('info/licenses/')}}
    assert set(review) == selected
    output = {'reviewed_dependency_metadata': review, 'candidate_sha256': expected_package, 'package_metadata': json.loads((root/'package-metadata.json').read_text()), 'runtime_inventory': data, 'note': 'Fresh runtime solve of retained build-1 binary; not original build environment or future release solve. URLs are sanitized binary URLs; license metadata and file paths are not legal conclusions.'}
    raw = json.dumps(output, sort_keys=True, indent=2).encode()
    encoded = base64.b64encode(gzip.compress(raw, mtime=0)).decode()
    chunks = [encoded[i:i+2700] for i in range(0, len(encoded), 2700)]
    assert len(chunks) <= 40
    print(f'::notice::CLOSURE-INFO chunks={len(chunks)} sha256={digest(raw)} records={len(data["packages"])}', flush=True)
    for index, chunk in enumerate(chunks):
        print(f'::notice::CLOSURE-CHUNK-{index:02d} {chunk}', flush=True)
else:
    raise ValueError('Unknown operation')
