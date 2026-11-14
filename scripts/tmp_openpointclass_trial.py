import json, os, sys, tempfile, zipfile
from pathlib import Path
from common import ROOT, ScaffoldError, run, sha256
from private_odm_bundle import build_recipe, loopback
from private_conda_channel import create
from package_archive import read_package
from openpointclass_synthetic_fixture import run_fixture

archive=Path('/tmp/opc-model/vehicles-vegetation-buildings.zip')
if sha256(archive)!='258f67f02a9d2c329c61726a227281f3ac0af9dd4c274c5c893975beb9dc191a':raise ScaffoldError('Model archive differs from earlier observed hash')
with tempfile.TemporaryDirectory(prefix='opc-trial-') as tmp:
 root=Path(tmp);model=root/'model.bin'
 with zipfile.ZipFile(archive) as z:
  items=z.infolist()
  if len(items)!=1 or items[0].filename!='model.bin' or items[0].file_size>10_000_000:raise ScaffoldError('Unexpected model archive')
  model.write_bytes(z.read(items[0]))
 if sha256(model)!='2960ef1036bb66c42ec908fb5160f396062a9baf5a7ca9a08ba4644976d798c2':raise ScaffoldError('Model mismatch')
 package=build_recipe(ROOT/'research/recipes/openpointclass-research/recipe.yaml','openpointclass-research',root/'build')
 info,payload=read_package(package);idx=json.loads(info['info/index.json'])
 if idx['name']!='openpointclass-research' or idx.get('license')!='LicenseRef-Unreviewed' or set(payload)!={'bin/pcclassify','share/odm-conda/openpointclass-research/SOURCE.txt'} or not payload['bin/pcclassify'].startswith(b'\x7fELF'):
  raise ScaffoldError('Unexpected research classifier payload')
 channel=root/'channel';create([package],channel);project=root/'project'
 with loopback(channel,48179) as url:
  run(['pixi','init','--format','pixi','--scm','github','--channel',url,'--channel','conda-forge','--platform','linux-64',str(project)])
  run(['pixi','add','--manifest-path',str(project/'pixi.toml'),'openpointclass-research','pdal==2.10.0'])
 result=run_fixture(project/'.pixi/envs/default',model)
 report={'package':package.name,'sha256':sha256(package),'model_sha256':sha256(model),'result':result,'scope':'synthetic LAZ smoke test; model and source rights, accuracy and release unreviewed; artifacts discarded'}
 print('::notice::CLASSIFICATION_REPORT '+json.dumps(report,sort_keys=True),flush=True)
