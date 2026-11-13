import base64,gzip,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
from common import run,sha256
from private_odm_bundle import build,PORT,loopback,candidate_summary
from run_private_odm_workflow import DATASET_URL,DATASET_COMMIT,download_crate

with tempfile.TemporaryDirectory(prefix='odm-stack-probe-') as tmp:
 root=Path(tmp); dataset=root/'seneca';crate=root/'jpegxl.crate';bundle=root/'bundle'
 run(['git','init',str(dataset)]);run(['git','-C',str(dataset),'fetch','--depth=1',DATASET_URL,DATASET_COMMIT]);run(['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD'])
 if subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()!=DATASET_COMMIT: raise ValueError('dataset commit mismatch')
 download_crate(crate)
 build(bundle,PORT,dataset,runtime_profile='reduced',reduced_jxl=True,vendor_scope_crate=crate,openmvs_variant='tetraflow',orthophoto_candidate=True)
 report=candidate_summary(bundle,sha256(bundle/'private-bundle.json'))
 project=root/'probe';project.mkdir()
 for f in ('pixi.toml','pixi.lock'):shutil.copy2(bundle/f,project/f)
 env=os.environ.copy();env['HOME']=str(root/'home');env['XDG_CACHE_HOME']=str(root/'cache');env['RATTLER_CACHE_DIR']=str(root/'cache/rattler');Path(env['HOME']).mkdir()
 with loopback(bundle/'channel',PORT):run(['pixi','install','--manifest-path',str(project/'pixi.toml'),'--locked'],env=env)
 prefix=project/'.pixi/envs/default'; selected=[]
 for f in (prefix/'conda-meta').glob('*.json'):
  d=json.loads(f.read_text());
  if d.get('name') in ('hdf5','libpdal-core','libpdal-hdf','libpdal-icebridge','libgdal-core','odm-research-codem'):
   selected.append({k:d.get(k) for k in ('name','version','build','sha256')})
 plugins=[]
 for path in sorted((prefix/'lib').glob('libpdal_plugin_*.so')):
  output=subprocess.run(['ldd',str(path)],capture_output=True,text=True)
  missing=[]
  for line in output.stdout.splitlines():
   if 'not found' in line:
    match=re.match(r'\s*([^\s/]+)\s*=>\s*not found\s*$',line)
    if not match: raise ValueError('Unexpected unresolved-library output')
    missing.append(match.group(1))
  plugins.append({'name':path.name,'ldd_returncode':output.returncode,'missing':missing})
 if not plugins:raise ValueError('No PDAL plugin libraries found')
 report.update(dataset_commit=DATASET_COMMIT,selected_dependencies=sorted(selected,key=lambda d:d['name']),plugins=plugins,scope='ephemeral research solve; metadata and direct plugin ldd only, not full runtime, installed-byte, source or legal review')
 encoded=base64.b64encode(gzip.compress(json.dumps(report,sort_keys=True).encode(),mtime=0)).decode()
 for i in range(0,len(encoded),1800):print('::notice::STACK%03d '%(i//1800)+encoded[i:i+1800],flush=True)
 if any(p['missing'] or p['ldd_returncode'] for p in plugins):raise ValueError('Unresolved PDAL plugin dependencies in research solve')
