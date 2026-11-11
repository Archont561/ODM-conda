import tempfile
from pathlib import Path
from common import ROOT, sha256
from private_odm_bundle import build_recipe

with tempfile.TemporaryDirectory(prefix='openmvs-alt-') as temp:
    package = build_recipe(ROOT/'research/recipes/openmvs-tetraflow-research/recipe.yaml', 'openmvs-tetraflow-research', Path(temp)/'trial')
    print(f'::notice::OPENMVS-TETRAFLOW-GUARDS package={package.name} sha256={sha256(package)}; source and binaries discarded', flush=True)
