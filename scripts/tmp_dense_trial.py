import json, subprocess, sys, tempfile
from pathlib import Path
from common import ROOT, run, sha256
from package_archive import read_package
from private_odm_bundle import build_recipe

with tempfile.TemporaryDirectory(prefix='dense-trial-') as tmp:
    root=Path(tmp)
    package=build_recipe(ROOT/'research/recipes/openmvs-dense-research/recipe.yaml','openmvs-dense-research',root)
    run([sys.executable,str(ROOT/'scripts/audit_openmvs_dense_research.py'),str(package)])
    info,_=read_package(package);idx=json.loads(info['info/index.json'])
    report={'filename':package.name,'sha256':sha256(package),'depends':idx['depends'],'scope':'research-only, CPU help and mesh fixtures; no real dense reconstruction, rights or release approval'}
    print('::notice::DENSE_REPORT '+json.dumps(report,sort_keys=True),flush=True)
