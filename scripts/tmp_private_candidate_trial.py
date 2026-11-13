import base64,gzip,json,tarfile,tempfile
from pathlib import Path
from common import sha256
from private_orthophoto_candidate import create

with tempfile.TemporaryDirectory(prefix='candidate-handoff-') as tmp:
 dest=Path(tmp)/'candidate';create(dest)
 receipt=json.loads((dest/'receipt.json').read_text())
 source=dest/'source'/receipt['source_bundle']['filename']
 with tarfile.open(source,'r:gz') as tar:
  manifest=json.load(tar.extractfile('SOURCE-MANIFEST.json'))
  expected=manifest['files']
  assert set(tar.getnames()) == set(expected)|{'SOURCE-MANIFEST.json','README-SOURCE.txt'}
  import hashlib
  for name,digest in expected.items():
   assert hashlib.sha256(tar.extractfile(name).read()).hexdigest()==digest
  assert manifest['component']=='odm-orthophoto' and manifest['build_number']==3
  assert expected['packaging/recipes/odm-orthophoto/recipe.yaml']==receipt['staged_recipe_sha256']
  assert expected['packaging/recipes/components.json']==receipt['staged_manifest_sha256']
  assert manifest['upstream']['sha256']==expected['upstream/odm-orthophoto-'+manifest['upstream']['commit']+'.tar.gz']
 data={'package':receipt['package'],'source_bundle':receipt['source_bundle'],'staged_recipe_sha256':receipt['staged_recipe_sha256'],'staged_manifest_sha256':receipt['staged_manifest_sha256'],'source_manifest_entries':len(expected),'scope':'private ephemeral rehearsal; source inputs only, not dependency closure or legal approval; outputs discarded'}
 encoded=base64.b64encode(gzip.compress(json.dumps(data,sort_keys=True).encode(),mtime=0)).decode()
 for i in range(0,len(encoded),1800):print('::notice::HANDOFF%03d '%(i//1800)+encoded[i:i+1800],flush=True)
