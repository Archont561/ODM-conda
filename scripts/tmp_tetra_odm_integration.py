"""Ephemeral alternate-only ODM integration probe; never publish outputs."""
import subprocess
import tempfile
from pathlib import Path

from common import ROOT, ScaffoldError, run
from run_private_odm_workflow import DATASET_URL, DATASET_COMMIT
from prepare_jxl_vendor_scope import CRATE_SHA256
from common import sha256

source = (ROOT/'scripts/private_odm_bundle.py').read_text()
before = """    run([sys.executable,str(ROOT/'scripts/check_open_research_sources.py'),'openmvs','--cache',str(work/'source-cache')])
    package=build_recipe(staged/'research/recipes/openmvs-odm/reduced.yaml','openmvs-odm',work/'openmvs')
    run([sys.executable,str(ROOT/'scripts/audit_open_research.py'),'openmvs-odm',str(package)]); packages.append(package)
"""
after = """    # This distinct experimental package has its own hash/absence and link-map guards.
    # The historical audit does not apply; do not present this as a production audit.
    package=build_recipe(staged/'research/recipes/openmvs-tetraflow-research/recipe.yaml','openmvs-tetraflow-research',work/'openmvs-tetraflow')
    packages.append(package)
"""
if source.count(before) != 1: raise ScaffoldError('Unexpected historical OpenMVS build block')
source = source.replace(before, after)
needle = "    configure_odm_research_recipe(recipe, reduced_jxl=reduced_jxl, vendor_scope=vendor_scope_crate is not None)\n"
inject = """    original = '    - openmvs-odm ==0.0.0.dev20260516 research_*'
    alternate = '    - openmvs-tetraflow-research ==0.0.0.dev20260827 research_*'
    text = recipe.read_text()
    if text.count(original) != 1: raise ScaffoldError('Unexpected ODM OpenMVS dependency')
    recipe.write_text(text.replace(original, alternate))
"""
if source.count(needle) != 1: raise ScaffoldError('Unexpected ODM recipe block')
source = source.replace(needle, inject + needle)
replay_needle = "            run([str(prefix/'bin/odm-fast-research'),'--fast-orthophoto','--help'])\n"
replay_check = "            run(['ldd', str(prefix/'bin/ReconstructMesh')])\n            missing=subprocess.check_output(['ldd', str(prefix/'bin/ReconstructMesh')],text=True)\n            if 'not found' in missing: raise ScaffoldError('Unresolved TetraFlow runtime library')\n"
if source.count(replay_needle) != 1: raise ScaffoldError('Unexpected replay block')
source = source.replace(replay_needle, replay_check + replay_needle)
namespace = {'__name__': 'private_tetraflow_bundle', '__file__': str(ROOT/'scripts/private_odm_bundle.py')}
exec(compile(source, namespace['__file__'], 'exec'), namespace)
with tempfile.TemporaryDirectory(prefix='tetra-odm-integration-') as tmp:
    root=Path(tmp); dataset=root/'seneca'; crate=Path('/tmp/jpegxl-src-0.11.2.crate')
    if not crate.is_file() or sha256(crate)!=CRATE_SHA256: raise ScaffoldError('Unexpected original JXL crate')
    run(['git','init',str(dataset)])
    run(['git','-C',str(dataset),'fetch','--depth=1',DATASET_URL,DATASET_COMMIT])
    run(['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD'])
    if subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()!=DATASET_COMMIT: raise ScaffoldError('Unexpected dataset')
    namespace['build'](root/'bundle',namespace['PORT'],dataset,runtime_profile='reduced',reduced_jxl=True,vendor_scope_crate=crate)
print('::notice::TETRAFLOW ODM integration and relocated replay passed; all research files discarded',flush=True)
