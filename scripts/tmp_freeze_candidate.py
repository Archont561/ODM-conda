import base64,gzip,hashlib,json,subprocess,tempfile,urllib.request
from pathlib import Path
from common import sha256
from private_odm_bundle import PORT, build
from prepare_jxl_vendor_scope import CRATE_SHA256
from run_private_odm_workflow import DATASET_URL, DATASET_COMMIT

with tempfile.TemporaryDirectory(prefix='odm-candidate-check-') as tmp:
 root=Path(tmp); dataset=root/'seneca'; crate=root/'jpegxl-src.crate'; bundle=root/'bundle'
 subprocess.run(['git','init',str(dataset)],check=True)
 subprocess.run(['git','-C',str(dataset),'fetch','--depth=1',DATASET_URL,DATASET_COMMIT],check=True)
 subprocess.run(['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD'],check=True)
 assert subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()==DATASET_COMMIT
 urllib.request.urlretrieve('https://static.crates.io/crates/jpegxl-src/jpegxl-src-0.11.2.crate',crate)
 if sha256(crate)!=CRATE_SHA256: raise ValueError('crate checksum mismatch')
 build(bundle,PORT,dataset,runtime_profile='reduced',reduced_jxl=True,vendor_scope_crate=crate,openmvs_variant='tetraflow')
 manifest=json.loads((bundle/'private-bundle.json').read_text()); inv=json.loads((bundle/'conda-inventory.json').read_text())
 pkgs=[{'filename':Path(n).name,'sha256':h} for n,h in manifest['files'].items() if n.startswith('channel/linux-64/') and n.endswith('.conda')]
 if len(pkgs)!=15: raise ValueError('unexpected local package count')
 result={'scope':'one ephemeral private research trial, not release selection, source completeness, rights or owner-retained bundle', 'local_packages':sorted(pkgs,key=lambda p:p['filename']),'package_count':len(pkgs),'inventory_record_count':len(inv['packages']),'inventory_sha256':sha256(bundle/'conda-inventory.json'),'lock_sha256':sha256(bundle/'pixi.lock'),'manifest_sha256':sha256(bundle/'private-bundle.json'),'dataset_commit':DATASET_COMMIT}
 data=base64.b64encode(gzip.compress(json.dumps(result,sort_keys=True).encode(),mtime=0)).decode()
 for i in range(0,len(data),1800):print('::notice::RESULT%03d '%(i//1800)+data[i:i+1800],flush=True)
