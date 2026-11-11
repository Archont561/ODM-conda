import tempfile
from pathlib import Path
from common import ROOT, run
from private_odm_bundle import build_recipe
import sys
with tempfile.TemporaryDirectory(prefix='tetra-audit-trial-') as temp:
    package=build_recipe(ROOT/'research/recipes/openmvs-tetraflow-research/recipe.yaml','openmvs-tetraflow-research',Path(temp))
    run([sys.executable,str(ROOT/'scripts/audit_tetraflow_research.py'),str(package)])
print('::notice::TetraFlow package build, retest and bounded audit passed; files discarded',flush=True)
