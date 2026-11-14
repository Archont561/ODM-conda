import json, os, re, shutil, subprocess, sys, tempfile, tarfile, urllib.request, zipfile
from collections import Counter
from pathlib import Path
from common import ROOT, ScaffoldError, rattler, run, sha256
from private_odm_bundle import build_recipe, loopback, private_identity, verify, inventory_identities
from private_conda_channel import create
from prepare_opencv413_research import prepare
from package_archive import read_package
from inventory_conda_environment import inventory
from openmvs_pointcloud_fixture import DATASET_FILES, verify_dataset
from openmvs_dense_dataset_fixture import test_dense

BUNDLE=Path('/tmp/odm-research-bundle')
ANCHOR='81da120940a5236657854b51b9713aae0e40dbd11199a51859197837e21c3c7b'
port=verify(BUNDLE,expected_manifest_sha=ANCHOR)
with tempfile.TemporaryDirectory(prefix='odm-dense-integration-') as tmp:
 root=Path(tmp)
 model_archive=Path('/tmp/opc-model/vehicles-vegetation-buildings.zip')
 if sha256(model_archive)!='258f67f02a9d2c329c61726a227281f3ac0af9dd4c274c5c893975beb9dc191a':raise ScaffoldError('model archive mismatch')
 modelroot=root/'models';model=modelroot/'openpointclass/v1_0_0/model.bin';model.parent.mkdir(parents=True)
 with zipfile.ZipFile(model_archive) as z:
  items=z.infolist()
  if len(items)!=1 or items[0].filename!='model.bin' or items[0].file_size>10000000:raise ScaffoldError('bad model archive')
  model.write_bytes(z.read(items[0]))
 if sha256(model)!='2960ef1036bb66c42ec908fb5160f396062a9baf5a7ca9a08ba4644976d798c2':raise ScaffoldError('model mismatch')
 opc=build_recipe(ROOT/'research/recipes/openpointclass-research/recipe.yaml','openpointclass-research',root/'opc')
 dense=build_recipe(ROOT/'research/recipes/openmvs-dense-research/recipe.yaml','openmvs-dense-research',root/'dense')
 run([sys.executable,str(ROOT/'scripts/audit_openmvs_dense_research.py'),str(dense)])
 stage=root/'stage';prepare(stage);recipe=stage/'recipes/dem2mesh/recipe.yaml';text=recipe.read_text()
 old='libgdal-core >=3.11,<3.12';new='libgdal-core >=3.12.2,<3.12.3'
 if text.count(old)!=2:raise ScaffoldError('Unexpected dem2mesh constraints')
 recipe.write_text('# PRIVATE RESEARCH ONLY\n'+text.replace(old,new));private_identity(recipe,1)
 dem=build_recipe(recipe,'dem2mesh',root/'dem')
 run([sys.executable,str(ROOT/'scripts/audit_package.py'),'--component','dem2mesh','--output-dir',str(dem.parent.parent),'--reports-dir',str(root/'reports')])
 base=[]
 for p in (BUNDLE/'channel/linux-64').glob('*.conda'):
  info,_=read_package(p);idx=json.loads(info['info/index.json'])
  if idx['name'] not in ('odm-fast-research','openmvs-tetraflow-research'):base.append(p)
 if len(base)!=13:raise ScaffoldError('Unexpected baseline package set')
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
  run([str(prefix/'bin/python'),'-s','-E',str(probe),str(prefix/'share/odm-conda/odm-dense-research/app')],env=env2)
  run([str(prefix/'bin/odm-dense-research'),'--help'],env=env2)
  run([str(prefix/'bin/python'),'-s','-E',str(prefix/'share/odm-conda/dem2mesh/functional_test.py')],env=env2)
  archive=root/'openmvs-old.tar.gz'
  urllib.request.urlretrieve('https://codeload.github.com/OpenDroneMap/openMVS/tar.gz/8e4c5f31a16e0e329132c8f26e20a8c5d7b47f53',archive)
  if sha256(archive)!='949d420d4506ccd0189574252c8214acce666de837e400e44682e8ddc13e666b':raise ScaffoldError('scene archive mismatch')
  scene_dataset=root/'scene-data';scene_dataset.mkdir()
  with tarfile.open(archive,'r:gz') as tar:
   for name in DATASET_FILES:
    member=tar.getmember('openMVS-8e4c5f31a16e0e329132c8f26e20a8c5d7b47f53/apps/Tests/data/'+name)
    if not member.isfile() or member.size>10*1024*1024:raise ScaffoldError('invalid scene member')
    target=scene_dataset/name;target.parent.mkdir(parents=True,exist_ok=True)
    with tar.extractfile(member) as src,target.open('wb') as dst:shutil.copyfileobj(src,dst)
  verify_dataset(scene_dataset);scene=root/'fixture-scene';scene.mkdir()
  dense_points=test_dense(prefix/'bin/DensifyPointCloud',scene_dataset,scene)
  print('::notice::DENSE_PLY_VALIDATED '+str(dense_points),flush=True)
  dataset=root/'seneca';run(['git','init',str(dataset)]);run(['git','-C',str(dataset),'fetch','--depth=1','https://github.com/OpenDroneMap/odm_data_seneca.git','9220acfdca75cc5e2dd6d27fe48550c5ae0877f2']);run(['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD'])
  if subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()!='9220acfdca75cc5e2dd6d27fe48550c5ae0877f2':raise ScaffoldError('dataset mismatch')
  images=sorted((dataset/'images').glob('*.jpg'))[:35]
  if len(images)!=35:raise ScaffoldError('missing images')
  projects=root/'projects';dest=projects/'dataset/images';dest.mkdir(parents=True)
  for img in images:shutil.copy2(img,dest/img.name)
  print('::notice::PACKAGED_REPLAY_PASS '+json.dumps({'package_count':len(identities),'packages':[{'filename':p.name,'sha256':sha256(p)} for p in (dense,dem,opc,odm)],'lock_sha256':sha256(project/'pixi.lock'),'no_binary_overlay':True,'standalone_dense_points':dense_points}),flush=True)
  env2['ODM_RESEARCH_MODEL_ROOT']=str(modelroot)
  run([str(prefix/'bin/odm-dense-research'),'--pc-classify','--mesh-octree-depth','8','--mesh-size','100000','--pc-quality','lowest','--feature-quality','low','--max-concurrency','2','--project-path',str(projects),'dataset'],env=env2)
  dense_output=projects/'dataset/opensfm/undistorted/openmvs/scene_dense_dense_filtered.ply'
  raster=projects/'dataset/odm_orthophoto/odm_orthophoto.tif';report=projects/'dataset/odm_report/report.pdf'
  mesh=projects/'dataset/odm_meshing/odm_mesh.ply';model=projects/'dataset/odm_texturing/odm_textured_model_geo.obj'
  if not all(p.is_file() and p.stat().st_size>1000 for p in (dense_output,raster,report,mesh,model)):raise ScaffoldError('ODM dense pipeline missing outputs')
  rasterenv=env2.copy();rasterenv['PROJ_DATA']=rasterenv['PROJ_LIB']=str(prefix/'share/proj');rasterenv['PATH']=str(prefix/'bin')+os.pathsep+os.defpath
  classified=projects/'dataset/odm_georeferencing/odm_georeferenced_model.laz'
  marker=projects/'dataset/odm_georeferencing/pc_classify_done.txt'
  if not classified.is_file() or not marker.is_file():raise ScaffoldError('Missing classified point cloud or marker')
  summary=json.loads(subprocess.check_output([str(prefix/'bin/pdal'),'info','--stats','--dimensions','Classification',str(classified)],text=True,env=rasterenv))
  stats=summary.get('stats',{}).get('statistic',[])
  if len(stats)!=1 or stats[0]['count']<=0 or stats[0]['maximum']<=2:raise ScaffoldError('No non-ground model classifications')
  from odm_raster_sanity import validate
  raster_json=subprocess.check_output([str(prefix/'bin/gdalinfo'),'-json','-stats',str(raster)],text=True,env=rasterenv);validate(json.loads(raster_json))
  from odm_textured_model_sanity import validate as validate_model
  model_info=validate_model(model)
  result={'classification_stats':stats[0], 'classification_model_sha256':'2960ef1036bb66c42ec908fb5160f396062a9baf5a7ca9a08ba4644976d798c2','model':model_info,'mesh_bytes':mesh.stat().st_size,'scope':'private CPU dense 3D and orthophoto research; not full ODM features, accuracy, rights or release','baseline_manifest_sha256':ANCHOR,'package_count':len(identities),'packages':[{ 'filename':p.name,'sha256':sha256(p)} for p in (dense,dem,opc,odm)],'lock_sha256':sha256(project/'pixi.lock'),'images':len(images),'dense_bytes':dense_output.stat().st_size,'orthophoto_bytes':raster.stat().st_size,'report_bytes':report.stat().st_size,'relocated_locked_replay':True,'no_binary_overlay':True,'standalone_dense_points':dense_points}
  print('::notice::INTEGRATION_REPORT '+json.dumps(result,sort_keys=True),flush=True)
