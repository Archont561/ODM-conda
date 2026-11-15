import json, os, re, shutil, subprocess, sys, tempfile, tarfile, urllib.request, zipfile
from collections import Counter
from pathlib import Path
from common import ROOT, ScaffoldError, rattler, run, sha256
from private_odm_bundle import build_recipe, build_packages, loopback, private_identity, inventory_identities
from run_private_odm_workflow import download_crate
from private_conda_channel import create
from prepare_opencv413_research import prepare
from package_archive import read_package
from inventory_conda_environment import inventory
from openmvs_pointcloud_fixture import DATASET_FILES, verify_dataset
from openmvs_dense_dataset_fixture import test_dense

port=48179
with tempfile.TemporaryDirectory(prefix='z-', dir='/tmp') as tmp:
 root=Path(tmp)
 crate=root/'jpegxl.crate'; download_crate(crate)
 baseline=root/'baseline'; baseline.mkdir()
 work=root/'b'; work.mkdir()
 packages=build_packages(work, reduced_jxl=True, vendor_scope_crate=crate,
                         openmvs_variant='tetraflow', orthophoto_candidate=True)
 keep=baseline/'linux-64'; keep.mkdir()
 base=[]
 for package in packages:
  info,_=read_package(package); name=json.loads(info['info/index.json'])['name']
  if name not in ('odm-fast-research','openmvs-tetraflow-research'):
   target=keep/package.name; shutil.copy2(package,target); base.append(target)
 if len(base)!=13:raise ScaffoldError('Unexpected rebuilt baseline package set')
 shutil.rmtree(work); crate.unlink()
 opc=build_recipe(ROOT/'research/recipes/openpointclass-research/recipe.yaml','openpointclass-research',root/'opc')
 dense=build_recipe(ROOT/'research/recipes/openmvs-dense-research/recipe.yaml','openmvs-dense-research',root/'dense')
 run([sys.executable,str(ROOT/'scripts/audit_openmvs_dense_research.py'),str(dense)])
 stage=root/'stage';prepare(stage);recipe=stage/'recipes/dem2mesh/recipe.yaml';text=recipe.read_text()
 old='libgdal-core >=3.11,<3.12';new='libgdal-core >=3.12.2,<3.12.3'
 if text.count(old)!=2:raise ScaffoldError('Unexpected dem2mesh constraints')
 recipe.write_text('# PRIVATE RESEARCH ONLY\n'+text.replace(old,new));private_identity(recipe,1)
 dem=build_recipe(recipe,'dem2mesh',root/'dem')
 run([sys.executable,str(ROOT/'scripts/audit_package.py'),'--component','dem2mesh','--output-dir',str(dem.parent.parent),'--reports-dir',str(root/'reports')])
 channel=root/'build-channel';create(base+[dense,dem,opc],channel)
 out=root/'odm-build';out.mkdir()
 with loopback(channel,port) as url:
  cmd=[rattler(),'build','--recipe',str(ROOT/'research/recipes/odm-dense-research/recipe.yaml'),'--target-platform','linux-64','--variant-config',str(ROOT/'recipes/variants.yaml'),'--channel',url,'--channel','conda-forge','--channel-priority','strict','--output-dir',str(out),'--log-style','plain']
  run(cmd)
  packages=list((out/'linux-64').glob('odm-dense-research-*.conda'))
  if len(packages)!=1:raise ScaffoldError('Expected one ODM package')
  odm=packages[0]
  run([rattler(),'test','--package-file',str(odm),'--channel',url,'--channel','conda-forge','--channel-priority','strict','--output-dir',str(root/'odm-retest'),'--log-style','plain'])
 info,payload=read_package(odm);idx=json.loads(info['info/index.json'])
 if idx.get('name')!='odm-dense-research' or idx.get('license')!='LicenseRef-Unreviewed' or not any(x.startswith('openmvs-dense-research ') for x in idx['depends']) or not any(x.startswith('dem2mesh ') for x in idx['depends']):raise ScaffoldError('Unexpected ODM package metadata')
 if not {'bin/odm-dense-research','share/odm-conda/odm-dense-research/app/run.py'} <= payload.keys():raise ScaffoldError('Missing ODM files')
 final_channel=root/'final-channel';create(base+[dense,dem,opc,odm],final_channel)
 project=root/'project';env=os.environ.copy();env['HOME']=str(root/'home');env['XDG_CACHE_HOME']=str(root/'cache');env['RATTLER_CACHE_DIR']=str(root/'cache/rattler');Path(env['HOME']).mkdir()
 with loopback(final_channel,port) as url:
  run(['pixi','init','--format','pixi','--scm','github','--channel',url,'--channel','conda-forge','--platform','linux-64',str(project)],env=env)
  run(['pixi','add','--manifest-path',str(project/'pixi.toml'),'odm-dense-research','libgdal-core==3.12.2','libpdal-core==2.10.0','libspatialite==5.1.0','libarchive==3.8.11'],env=env)
  prefix=project/'.pixi/envs/default'; identities=inventory_identities(inventory(prefix));records={r[0]:r for r in identities}
  for package in (dense,dem,opc,odm):
   info,_=read_package(package);item=json.loads(info['info/index.json']);record=records[item['name']]
   if record[3]!=sha256(package) or record[2]!=item['build']:raise ScaffoldError('Installed package identity mismatch')
  if 'openmvs-tetraflow-research' in records or 'odm-fast-research' in records:raise ScaffoldError('Unexpected baseline packages')
  # A second fresh prefix must replay the unchanged lock and identities.
  relocated=root/'relocated';relocated.mkdir()
  for name in ('pixi.toml','pixi.lock'):shutil.copy2(project/name,relocated/name)
  env2=env.copy();env2['HOME']=str(root/'home2');env2['XDG_CACHE_HOME']=str(root/'cache2');env2['RATTLER_CACHE_DIR']=str(root/'cache2/rattler');Path(env2['HOME']).mkdir()
  run(['pixi','install','--manifest-path',str(relocated/'pixi.toml'),'--locked'],env=env2)
  prefix=relocated/'.pixi/envs/default'
  if inventory_identities(inventory(prefix))!=identities:raise ScaffoldError('Relocated inventory differs')
  if (relocated/'pixi.lock').read_bytes()!=(project/'pixi.lock').read_bytes():raise ScaffoldError('Lock changed on replay')
  # Fault injection against the installed patched module; original cloud must survive.
  probe = root/'probe.py'
  probe.write_text("""import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from opendm import opc
os.environ['ODM_CONDA_MODEL_ROOT'] = '/private/offline'
with tempfile.TemporaryDirectory() as d:
 p=Path(d)/'input.laz'; p.write_bytes(b'original')
 opc.get_model=lambda *a, **k: '/unused/model'
 def broken(*a, **k): raise RuntimeError('injected failure')
 opc.run=broken
 try: opc.classify(str(p))
 except RuntimeError as e: assert 'injected failure' in str(e)
 else: raise AssertionError('classifier error was swallowed')
 assert p.read_bytes()==b'original'
 opc.run=lambda *a, **k: None
 try: opc.classify(str(p))
 except RuntimeError as e: assert 'no nonempty output' in str(e)
 else: raise AssertionError('missing output was swallowed')
 assert p.read_bytes()==b'original'
print('NEGATIVE_CLASSIFICATION_PROBES_PASS')
""")
  probe_env=env2.copy();probe_env['ODM_CONDA_LOCAL_PREFIX']=str(prefix)
  run([str(prefix/'bin/python'),'-s','-E',str(probe),str(prefix/'share/odm-conda/odm-dense-research/app')],env=probe_env)
  fixture_env=env2.copy();fixture_env['ODM_CONDA_LOCAL_PREFIX']=str(prefix)
  synth=subprocess.check_output([str(prefix/'bin/python'),'-s','-E',str(ROOT/'scripts/odm_research_merge_fixture.py'),str(prefix),str(prefix/'share/odm-conda/odm-dense-research/app')],env=fixture_env,text=True)
  print('MERGE_SYNTHETIC '+synth.strip().splitlines()[-1],flush=True)
  run([str(prefix/'bin/odm-dense-research'),'--help'],env=env2)
  run([str(prefix/'bin/python'),'-s','-E',str(prefix/'share/odm-conda/dem2mesh/functional_test.py')],env=env2)
  app=prefix/'share/odm-conda/odm-dense-research/app'
  runenv=env2.copy();runenv.update({'ODM_CONDA_LOCAL_PREFIX':str(prefix),'PROJ_DATA':str(prefix/'share/proj'),'PROJ_LIB':str(prefix/'share/proj'),'PATH':str(prefix/'bin')+os.pathsep+os.defpath})
  result=subprocess.check_output([str(prefix/'bin/python'),'-s','-E',str(ROOT/'scripts/odm_dem_zero_packaged_fixture.py'),str(prefix),str(app)],env=runenv,text=True)
  print('::notice::ZERO_REPORT '+next(line.split('FIXTURE_JSON ',1)[1] for line in result.splitlines() if 'FIXTURE_JSON ' in line),flush=True)
  result=subprocess.check_output([str(prefix/'bin/python'),'-s','-E',str(ROOT/'scripts/odm_dem_distance_fixture.py'),str(prefix),str(app)],env=runenv,text=True)
  print('::notice::DISTANCE_REPORT '+next(line.split('FIXTURE_JSON ',1)[1] for line in result.splitlines() if 'FIXTURE_JSON ' in line),flush=True)
  print('::notice::REPLAY_REPORT '+json.dumps({'count':len(identities),'lock_sha256':sha256(project/'pixi.lock'),'odm_package':odm.name,'odm_sha256':sha256(odm),'no_binary_overlay':True,'no_source_overlay':True},sort_keys=True),flush=True)
  sample=root/'srtm.zip'
  with sample.open('wb') as output:
   subprocess.run(['gh','api','-H','Accept: application/vnd.github.raw+json','repos/rasterio/rasterio/contents/tests/data/N10W110.hgt.zip?ref=124e23f4060678460f39a0d838ac8c83b6fe2fe7'],stdout=output,check=True)
  result=subprocess.check_output([str(prefix/'bin/python'),'-s','-E',str(ROOT/'scripts/odm_srtm_zero_overlap_fixture.py'),str(prefix),str(app),str(sample)],env=runenv,text=True)
  print('::notice::SRTM_REPORT '+next(line.split('FIXTURE_JSON ',1)[1] for line in result.splitlines() if 'FIXTURE_JSON ' in line),flush=True)
