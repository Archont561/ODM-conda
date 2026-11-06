import base64
import gzip
import hashlib
import json
import os
import sys
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
    output = {'candidate_sha256': expected_package, 'package_metadata': json.loads((root/'package-metadata.json').read_text()), 'runtime_inventory': data, 'note': 'Fresh runtime solve of retained build-1 binary; not original build environment or future release solve. URLs are sanitized binary URLs; license metadata and file paths are not legal conclusions.'}
    raw = json.dumps(output, sort_keys=True, indent=2).encode()
    encoded = base64.b64encode(gzip.compress(raw, mtime=0)).decode()
    chunks = [encoded[i:i+2700] for i in range(0, len(encoded), 2700)]
    assert len(chunks) <= 40
    print(f'::notice::CLOSURE-INFO chunks={len(chunks)} sha256={digest(raw)} records={len(data["packages"])}', flush=True)
    for index, chunk in enumerate(chunks):
        print(f'::notice::CLOSURE-CHUNK-{index:02d} {chunk}', flush=True)
else:
    raise ValueError('Unknown operation')
