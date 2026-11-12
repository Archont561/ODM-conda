import json
import tempfile
from pathlib import Path
import yaml
from common import ROOT
from private_odm_bundle import build_recipe
from package_archive import read_package

with tempfile.TemporaryDirectory(prefix='tetra-meta-') as temp:
    package = build_recipe(ROOT/'research/recipes/openmvs-tetraflow-research/recipe.yaml', 'openmvs-tetraflow-research', Path(temp))
    info, _ = read_package(package)
    print('::notice::RECIPE-FILES '+repr(sorted(name for name in info if name.startswith('info/recipe/'))), flush=True)
    for name in sorted(info):
        if name.endswith('rendered_recipe.yaml'):
            parsed = yaml.safe_load(info[name]); print('::notice::RENDER-KEYS '+repr(list(parsed)), flush=True)
            deps = parsed.get('finalized_dependencies', {}); print('::notice::DEP-KEYS '+repr(list(deps)), flush=True)
            for key, value in deps.items():
                print('::notice::DEP-SAMPLE '+key+' '+json.dumps(value, sort_keys=True)[:2000], flush=True)
