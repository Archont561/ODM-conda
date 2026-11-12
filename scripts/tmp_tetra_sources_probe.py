import hashlib
import json
import tempfile
import urllib.request
from pathlib import Path
import yaml
from package_archive import read_package

inventory=json.loads(Path('research/tetraflow-build-input-inventory.json').read_text())
for item in inventory['host']:
    if item['name'] not in ('cgal-cpp','nanoflann','libboost-devel'): continue
    with tempfile.TemporaryDirectory(prefix='tetra-dep-') as temp:
        target=Path(temp)/item['fn']
        urllib.request.urlretrieve(item['binary_package_url'],target)
        assert hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256']
        info,_=read_package(target)
        names=sorted(n for n in info if n.startswith('info/recipe/'))
        print('::notice::RECIPEFILES-'+item['name']+' '+repr(names)[:2700], flush=True)
        for filename in ('info/recipe/rendered_recipe.yaml','info/recipe/recipe.yaml','info/recipe/meta.yaml'):
            if filename not in info: continue
            try:
                recipe=yaml.safe_load(info[filename])
                if isinstance(recipe,dict):
                    val={'source':recipe.get('source'),'finalized_sources':recipe.get('finalized_sources')}
                    if 'recipe' in recipe and isinstance(recipe['recipe'],dict): val['recipe_source']=recipe['recipe'].get('source')
                    print('::notice::SOURCE-'+item['name']+' '+json.dumps(val,sort_keys=True)[:2700],flush=True)
            except Exception as error: print('::notice::PARSE-'+item['name']+' '+str(error)[:400],flush=True)
