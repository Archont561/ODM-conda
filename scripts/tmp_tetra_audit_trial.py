import tempfile
from pathlib import Path
from common import ROOT, run
from private_odm_bundle import build_recipe
import sys
with tempfile.TemporaryDirectory(prefix='tetra-audit-trial-') as temp:
    package=build_recipe(ROOT/'research/recipes/openmvs-tetraflow-research/recipe.yaml','openmvs-tetraflow-research',Path(temp))
    from package_archive import read_package
    import hashlib
    info, payload = read_package(package)
    print('::notice::NOTICES ' + repr({name: hashlib.sha256(data).hexdigest() for name, data in info.items() if name.startswith('info/licenses/')}), flush=True)
    print('::notice::PAYLOAD ' + repr(sorted(payload)), flush=True)
    run([sys.executable,str(ROOT/'scripts/audit_tetraflow_research.py'),str(package)])
print('::notice::TetraFlow package build, retest and bounded audit passed; files discarded',flush=True)
