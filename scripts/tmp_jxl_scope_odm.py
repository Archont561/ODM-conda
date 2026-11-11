import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path
from common import ScaffoldError, run, sha256
from private_odm_bundle import PORT, build
from prepare_jxl_vendor_scope import CRATE_SHA256

URL='https://github.com/OpenDroneMap/odm_data_seneca.git'
COMMIT='9220acfdca75cc5e2dd6d27fe48550c5ae0877f2'
with tempfile.TemporaryDirectory(prefix='odm-vendor-scope-') as tmp:
    root=Path(tmp); dataset=root/'seneca'; crate=root/'source.crate'
    with urllib.request.urlopen('https://static.crates.io/crates/jpegxl-src/jpegxl-src-0.11.2.crate',timeout=90) as response:
        crate.write_bytes(response.read(100000000))
    if sha256(crate)!=CRATE_SHA256: raise ScaffoldError('Crate mismatch')
    run(['git','init',str(dataset)]); run(['git','-C',str(dataset),'fetch','--depth=1',URL,COMMIT]); run(['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD'])
    if subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()!=COMMIT: raise ScaffoldError('Unexpected dataset revision')
    bundle=root/'bundle'; build(bundle,PORT,dataset,runtime_profile='reduced',reduced_jxl=True,vendor_scope_crate=crate)
    records={x['name']:x for x in json.loads((bundle/'conda-inventory.json').read_text())['packages']}
    jxl=records['odm-research-pillow-jxl-plugin']; odm=records['odm-fast-research']
    if not jxl['build'].startswith('research_vendor_scope_') or not jxl['build'].endswith('_3') or odm['build_number']!=5: raise ScaffoldError('Unexpected candidate identities')
    print('::notice::JXL-ODM-SCOPE '+json.dumps({'count':len(records),'jxl':{k:jxl.get(k) for k in ('version','build','sha256','license')},'odm':{k:odm.get(k) for k in ('version','build','sha256','license')}},separators=(',',':')),flush=True)
print('::notice::Private scoped JXL ODM source build, relocated replay, synthetic codec and Seneca raster passed; outputs discarded',flush=True)
