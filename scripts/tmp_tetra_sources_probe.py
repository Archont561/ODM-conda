import hashlib
import json
import tempfile
import urllib.request
from pathlib import Path
import yaml
from package_archive import read_package

inventory=json.loads(Path('research/tetraflow-build-input-inventory.json').read_text())
for item in inventory['host']:
    if item['name'] not in ('cgal-cpp','nanoflann','libboost-devel','libjpeg-turbo'): continue
    with tempfile.TemporaryDirectory(prefix='tetra-dep-') as temp:
        target=Path(temp)/item['fn']
        urllib.request.urlretrieve(item['binary_package_url'],target)
        assert hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256']
        info,_=read_package(target)
        recipe=yaml.safe_load(info['info/recipe/rendered_recipe.yaml'])
        keys = ['finalized_sources','recipe']
        source={key:recipe.get(key) for key in keys}
        if isinstance(source.get('recipe'),dict): source['recipe']={'source':source['recipe'].get('source')}
        print('::notice::SOURCE-'+item['name']+' '+json.dumps(source,sort_keys=True)[:2800],flush=True)
