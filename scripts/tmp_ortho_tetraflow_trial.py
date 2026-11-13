import base64,gzip,json,subprocess,tempfile
from pathlib import Path
from common import run,sha256
from private_odm_bundle import build,PORT,candidate_summary
from run_private_odm_workflow import DATASET_URL,DATASET_COMMIT,download_crate

with tempfile.TemporaryDirectory(prefix='ortho-tetraflow-') as d:
 root=Path(d); dataset=root/'seneca'; crate=root/'jpegxl.crate'; bundle=root/'bundle'
 run(['git','init',str(dataset)])
 run(['git','-C',str(dataset),'fetch','--depth=1',DATASET_URL,DATASET_COMMIT])
 run(['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD'])
 if subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()!=DATASET_COMMIT: raise ValueError('dataset identity mismatch')
 download_crate(crate)
 build(bundle,PORT,dataset,runtime_profile='reduced',reduced_jxl=True,vendor_scope_crate=crate,openmvs_variant='tetraflow',orthophoto_candidate=True)
 data=candidate_summary(bundle,sha256(bundle/'private-bundle.json'))
 records=[p for p in data['local_packages'] if p['filename'].startswith('odm-orthophoto-')]
 if len(records)!=1 or '-candidate_opencv413_' not in records[0]['filename']: raise ValueError('Candidate not selected')
 data['dataset_commit']=DATASET_COMMIT
 encoded=base64.b64encode(gzip.compress(json.dumps(data,sort_keys=True).encode(),mtime=0)).decode()
 for i in range(0,len(encoded),1800): print('::notice::RECORD%03d '%(i//1800)+encoded[i:i+1800],flush=True)
