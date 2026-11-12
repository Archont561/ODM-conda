import json
import tempfile
from pathlib import Path
from common import ROOT, sha256
from private_odm_bundle import build_recipe
from conda_build_provenance import inspect

with tempfile.TemporaryDirectory(prefix='tetra-meta-') as temp:
    package = build_recipe(ROOT/'research/recipes/openmvs-tetraflow-research/recipe.yaml', 'openmvs-tetraflow-research', Path(temp))
    report = inspect(package)
    Path('/tmp/tetra-metadata.json').write_text(json.dumps(report, sort_keys=True, indent=2)+'\n')
    print(f'::notice::TETRA-METADATA package={sha256(package)} build={len(report["build"])} host={len(report["host"])}',flush=True)
