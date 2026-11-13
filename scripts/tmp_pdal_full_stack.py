import base64,gzip,json,os,shutil,subprocess,tempfile
from pathlib import Path
from common import run,sha256
from private_odm_bundle import build,PORT,loopback,candidate_summary
from run_private_odm_workflow import DATASET_URL,DATASET_COMMIT,download_crate

with tempfile.TemporaryDirectory(prefix='pdal-full-stack-') as tmp:
 root=Path(tmp); dataset=root/'seneca';crate=root/'jpegxl.crate';bundle=root/'bundle'
 run(['git','init',str(dataset)]);run(['git','-C',str(dataset),'fetch','--depth=1',DATASET_URL,DATASET_COMMIT]);run(['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD'])
 if subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()!=DATASET_COMMIT:raise ValueError('dataset mismatch')
 download_crate(crate)
 build(bundle,PORT,dataset,runtime_profile='reduced',reduced_jxl=True,vendor_scope_crate=crate,openmvs_variant='tetraflow',orthophoto_candidate=True)
 report=candidate_summary(bundle,sha256(bundle/'private-bundle.json'));project=root/'probe';project.mkdir()
 for name in ('pixi.toml','pixi.lock'):shutil.copy2(bundle/name,project/name)
 env=os.environ.copy();env['HOME']=str(root/'home');env['XDG_CACHE_HOME']=str(root/'cache');env['RATTLER_CACHE_DIR']=str(root/'cache/rattler');Path(env['HOME']).mkdir()
 with loopback(bundle/'channel',PORT):run(['pixi','install','--manifest-path',str(project/'pixi.toml'),'--locked'],env=env)
 prefix=project/'.pixi/envs/default';selected=[]
 for file in (prefix/'conda-meta').glob('*.json'):
  item=json.loads(file.read_text())
  if item.get('name') in ('hdf5','libpdal-core','libpdal-hdf','libpdal-icebridge','libgdal-core'):
   selected.append({k:item.get(k) for k in ('name','version','build','sha256')})
 test_env=env.copy();test_env.pop('PYTHONPATH',None);test_env.pop('PYTHONHOME',None)
 out=subprocess.check_output(['/tmp/fixture-env/bin/python','scripts/pdal_synthetic_formats.py','--prefix',str(prefix)],text=True,env=test_env)
 result=json.loads(out.splitlines()[-1]);assert result['formats']==['las','laz','hdf','icebridge'] and result['point_count']==3
 report.update(dataset_commit=DATASET_COMMIT,selected_dependencies=sorted(selected,key=lambda d:d['name']),fixture_results=result,scope='ephemeral research stack; synthetic formats only; not final release lock, installed-byte verification, source closure or legal approval')
 encoded=base64.b64encode(gzip.compress(json.dumps(report,sort_keys=True).encode(),mtime=0)).decode()
 for i in range(0,len(encoded),1800):print('::notice::FORMATS%03d '%(i//1800)+encoded[i:i+1800],flush=True)
