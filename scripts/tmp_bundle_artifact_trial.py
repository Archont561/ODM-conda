import base64,gzip,json,os,shutil,subprocess,tempfile
from pathlib import Path
from common import run,sha256
from private_odm_bundle import PORT,build,verify,loopback,candidate_summary,replay
from run_private_odm_workflow import DATASET_URL,DATASET_COMMIT,download_crate

MODE=os.environ['TRIAL_MODE']; BUNDLE=Path('/tmp/odm-validated-bundle')
if MODE=='build':
 with tempfile.TemporaryDirectory(prefix='private-odm-inputs-') as tmp:
  root=Path(tmp);dataset=root/'seneca';crate=root/'jpegxl.crate'
  run(['git','init',str(dataset)]);run(['git','-C',str(dataset),'fetch','--depth=1',DATASET_URL,DATASET_COMMIT]);run(['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD'])
  if subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()!=DATASET_COMMIT:raise ValueError('dataset identity mismatch')
  download_crate(crate)
  build(BUNDLE,PORT,dataset,runtime_profile='reduced',reduced_jxl=True,vendor_scope_crate=crate,openmvs_variant='tetraflow',orthophoto_candidate=True)
 manifest=sha256(BUNDLE/'private-bundle.json');verify(BUNDLE,expected_manifest_sha=manifest)
 # Verify the artifact contains only the explicit sealed binary-channel and
 # metadata set. In particular, never upload source archives or the dataset.
 allowed={'private-bundle.json','pixi.toml','pixi.lock','conda-inventory.json','channel/linux-64/repodata.json','channel/noarch/repodata.json'}
 allowed.update(p.relative_to(BUNDLE).as_posix() for p in (BUNDLE/'channel/linux-64').glob('*.conda'))
 actual={p.relative_to(BUNDLE).as_posix() for p in BUNDLE.rglob('*') if p.is_file() or p.is_symlink()}
 if actual != allowed or len(allowed)!=21 or any(p.is_symlink() for p in BUNDLE.rglob('*')):raise ValueError('Unexpected artifact content')
 with open(os.environ['GITHUB_OUTPUT'],'a') as out:out.write(f'manifest_sha={manifest}\n')
 print(f'::notice::MANIFEST_SHA256 {manifest}',flush=True)
elif MODE=='inspect':
 manifest=os.environ['MANIFEST_SHA'];verify(BUNDLE,expected_manifest_sha=manifest)
 replay(BUNDLE,expected_manifest_sha=manifest,test_jxl=True)
 report=candidate_summary(BUNDLE,manifest)
 with tempfile.TemporaryDirectory(prefix='artifact-format-probe-') as tmp:
  root=Path(tmp);project=root/'project';project.mkdir()
  for name in ('pixi.toml','pixi.lock'):shutil.copy2(BUNDLE/name,project/name)
  env=os.environ.copy();env['HOME']=str(root/'home');env['XDG_CACHE_HOME']=str(root/'cache');env['RATTLER_CACHE_DIR']=str(root/'cache/rattler');Path(env['HOME']).mkdir()
  with loopback(BUNDLE/'channel',PORT):run(['pixi','install','--manifest-path',str(project/'pixi.toml'),'--locked'],env=env)
  prefix=project/'.pixi/envs/default';env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None)
  out=subprocess.check_output(['/tmp/fixture-env/bin/python','scripts/pdal_synthetic_formats.py','--prefix',str(prefix)],text=True,env=env)
  result=json.loads(out.splitlines()[-1]);assert result['formats']==['las','laz','hdf','icebridge'] and result['point_count']==3
  report['fixture_results']=result
 report['scope']='temporarily uploaded research bundle; exact manifest anchored and replayed; no final release, source completeness, installed-byte, rights or approval'
 encoded=base64.b64encode(gzip.compress(json.dumps(report,sort_keys=True).encode(),mtime=0)).decode()
 for i in range(0,len(encoded),1800):print('::notice::REPORT%03d '%(i//1800)+encoded[i:i+1800],flush=True)
else:raise ValueError('invalid mode')
