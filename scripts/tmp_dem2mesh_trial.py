import base64, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
from common import ROOT, ScaffoldError, run, sha256
from prepare_opencv413_research import prepare
from private_odm_bundle import build_recipe, loopback, private_identity, verify, inventory_identities
from private_conda_channel import create
from package_archive import read_package
from inventory_conda_environment import inventory

BUNDLE=Path('/tmp/odm-research-bundle')
ANCHOR='81da120940a5236657854b51b9713aae0e40dbd11199a51859197837e21c3c7b'
port=verify(BUNDLE,expected_manifest_sha=ANCHOR)
with tempfile.TemporaryDirectory(prefix='dem2mesh-research-') as tmp:
 root=Path(tmp);staged=root/'packaging';prepare(staged)
 recipe=staged/'recipes/dem2mesh/recipe.yaml';text=recipe.read_text()
 old='libgdal-core >=3.11,<3.12';new='libgdal-core >=3.12.2,<3.12.3'
 if text.count(old)!=2 or new in text:raise ScaffoldError('Unexpected dem2mesh constraints')
 recipe.write_text('# PRIVATE GDAL ABI RESEARCH; NOT A RELEASE\n'+text.replace(old,new))
 private_identity(recipe,1)
 package=build_recipe(recipe,'dem2mesh',root/'component')
 run([sys.executable,str(ROOT/'scripts/audit_package.py'),'--component','dem2mesh','--output-dir',str(package.parent.parent),'--reports-dir',str(root/'reports')])
 info,_=read_package(package);index=json.loads(info['info/index.json'])
 deps=index['depends'];assert index['name']=='dem2mesh' and index['build'].startswith('research_')
 assert any(x.startswith('libgdal-core ') and '3.12' in x for x in deps)
 old_inventory=json.loads((BUNDLE/'conda-inventory.json').read_text());old=inventory_identities(old_inventory)
 new_channel=root/'channel'; files=list((BUNDLE/'channel/linux-64').glob('*.conda'))+[package];create(files,new_channel)
 project=root/'project';project.mkdir()
 for name in ('pixi.toml','pixi.lock'):shutil.copy2(BUNDLE/name,project/name)
 env=os.environ.copy();env['HOME']=str(root/'home');env['XDG_CACHE_HOME']=str(root/'cache');env['RATTLER_CACHE_DIR']=str(root/'cache/rattler');Path(env['HOME']).mkdir()
 with loopback(new_channel,port):
  run(['pixi','install','--manifest-path',str(project/'pixi.toml'),'--locked'],env=env)
  baseline=inventory_identities(inventory(project/'.pixi/envs/default'))
  if baseline!=old:raise ScaffoldError('Baseline inventory mismatch')
  run(['pixi','add','--manifest-path',str(project/'pixi.toml'),'dem2mesh==0.0.0.dev20231207'],env=env)
  updated=inventory_identities(inventory(project/'.pixi/envs/default'))
  # Run exact package installed in the new full-stack solve, not merely retest.
  fixture=project/'.pixi/envs/default/share/odm-conda/dem2mesh/functional_test.py'
  clean=env.copy();clean.pop('PYTHONPATH',None);clean.pop('PYTHONHOME',None);clean.pop('LD_LIBRARY_PATH',None)
  run([str(project/'.pixi/envs/default/bin/python'),'-s','-E',str(fixture)],env=clean)
 old_set=set(old);new_set=set(updated);added=sorted(new_set-old_set);removed=sorted(old_set-new_set)
 report={'candidate_filename':package.name,'candidate_sha256':sha256(package),'depends':deps,'baseline_manifest_sha256':ANCHOR,'baseline_inventory_count':len(old),'new_inventory_count':len(updated),'added':added,'removed':removed,'scope':'disposable research build and re-solve; no rights, source completeness, final release or approval'}
 data=base64.b64encode(json.dumps(report,sort_keys=True).encode()).decode()
 for i in range(0,len(data),1800):print(f'::notice::REPORT{i//1800:03d} {data[i:i+1800]}',flush=True)
