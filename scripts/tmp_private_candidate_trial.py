import base64,gzip,hashlib,json,subprocess,tarfile,tempfile
from pathlib import Path
from common import run,sha256
from private_odm_bundle import build,PORT,candidate_summary
from private_orthophoto_candidate import create
from run_private_odm_workflow import DATASET_URL,DATASET_COMMIT,download_crate

with tempfile.TemporaryDirectory(prefix='candidate-handoff-') as tmp:
 root=Path(tmp); dest=root/'candidate';create(dest)
 receipt=json.loads((dest/'receipt.json').read_text())
 source=dest/'source'/receipt['source_bundle']['filename']; package=dest/'package'/receipt['package']['filename']
 with tarfile.open(source,'r:gz') as tar:
  manifest=json.load(tar.extractfile('SOURCE-MANIFEST.json')); expected=manifest['files']
  if set(tar.getnames()) != set(expected)|{'SOURCE-MANIFEST.json','README-SOURCE.txt'}: raise ValueError('source entries mismatch')
  for name,digest in expected.items():
   if hashlib.sha256(tar.extractfile(name).read()).hexdigest()!=digest: raise ValueError('source hash mismatch')
  if manifest['component']!='odm-orthophoto' or manifest['build_number']!=3: raise ValueError('source identity mismatch')
  if expected['packaging/recipes/odm-orthophoto/recipe.yaml']!=receipt['staged_recipe_sha256'] or expected['packaging/recipes/components.json']!=receipt['staged_manifest_sha256']: raise ValueError('staged packaging mismatch')
  if manifest['upstream']['sha256']!=expected['upstream/odm-orthophoto-'+manifest['upstream']['commit']+'.tar.gz']: raise ValueError('upstream pin mismatch')
 dataset=root/'seneca';crate=root/'jpegxl.crate';bundle=root/'bundle'
 run(['git','init',str(dataset)]);run(['git','-C',str(dataset),'fetch','--depth=1',DATASET_URL,DATASET_COMMIT]);run(['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD'])
 if subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()!=DATASET_COMMIT: raise ValueError('dataset identity mismatch')
 download_crate(crate)
 build(bundle,PORT,dataset,runtime_profile='reduced',reduced_jxl=True,vendor_scope_crate=crate,openmvs_variant='tetraflow',orthophoto_candidate=True,orthophoto_package=package,orthophoto_sha256=receipt['package']['sha256'])
 data=candidate_summary(bundle,sha256(bundle/'private-bundle.json')); candidates=[p for p in data['local_packages'] if p['filename'].startswith('odm-orthophoto-')]
 if candidates != [receipt['package']] or sha256(package)!=receipt['package']['sha256'] or sha256(source)!=receipt['source_bundle']['sha256']: raise ValueError('candidate or source bytes changed')
 data.update(source_bundle=receipt['source_bundle'],staged_recipe_sha256=receipt['staged_recipe_sha256'],staged_manifest_sha256=receipt['staged_manifest_sha256'],source_manifest_entries=len(expected),dataset_commit=DATASET_COMMIT,scope='ephemeral same-byte candidate and source-input rehearsal; not full dependency closure, installed-byte verification or release approval')
 encoded=base64.b64encode(gzip.compress(json.dumps(data,sort_keys=True).encode(),mtime=0)).decode()
 for i in range(0,len(encoded),1800):print('::notice::HANDOFF%03d '%(i//1800)+encoded[i:i+1800],flush=True)
