"""Temporary private-only TetraFlow ODM full-stack test; no artifacts uploaded."""
import subprocess
import tempfile
from pathlib import Path

from common import ScaffoldError, run, sha256
from private_odm_bundle import build, PORT
from prepare_jxl_vendor_scope import CRATE_SHA256
from run_private_odm_workflow import DATASET_URL, DATASET_COMMIT

with tempfile.TemporaryDirectory(prefix='tetra-bundle-trial-') as temp:
    root = Path(temp); dataset = root/'seneca'; crate=Path('/tmp/jpegxl-src-0.11.2.crate')
    if not crate.is_file() or sha256(crate) != CRATE_SHA256: raise ScaffoldError('Unexpected JXL crate')
    run(['git','init',str(dataset)])
    run(['git','-C',str(dataset),'fetch','--depth=1',DATASET_URL,DATASET_COMMIT])
    run(['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD'])
    if subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()!=DATASET_COMMIT:
        raise ScaffoldError('Unexpected dataset')
    build(root/'bundle',PORT,dataset,runtime_profile='reduced',reduced_jxl=True,
          vendor_scope_crate=crate,openmvs_variant='tetraflow')
print('::notice::PRIVATE TETRAFLOW BUNDLE build, selected audits, relocated replay and Seneca passed; files discarded',flush=True)
