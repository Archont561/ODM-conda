import json
import subprocess
import tempfile
from pathlib import Path
from common import ScaffoldError, run
from private_odm_bundle import PORT, build

URL='https://github.com/OpenDroneMap/odm_data_seneca.git'
COMMIT='9220acfdca75cc5e2dd6d27fe48550c5ae0877f2'
with tempfile.TemporaryDirectory(prefix='odm-reduced-jxl-') as tmp:
    root=Path(tmp); dataset=root/'seneca'
    run(['git','init',str(dataset)])
    run(['git','-C',str(dataset),'fetch','--depth=1',URL,COMMIT])
    run(['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD'])
    if subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()!=COMMIT:
        raise ScaffoldError('Unexpected dataset revision')
    bundle=root/'bundle'
    build(bundle,PORT,dataset,runtime_profile='reduced',reduced_jxl=True)
    data=json.loads((bundle/'conda-inventory.json').read_text()); records={x['name']:x for x in data['packages']}
    jxl=records['odm-research-pillow-jxl-plugin']; odm=records['odm-fast-research']
    if not jxl['build'].startswith('research_reduced_') or not jxl['build'].endswith('_2') or odm['build_number']!=4:
        raise ScaffoldError('Unexpected reduced JXL or ODM build identity')
    names=('odm-research-pillow-jxl-plugin','odm-fast-research','renderdem','libarchive','libspatialite','libjxl')
    summary={n:{k:records[n].get(k) for k in ('version','build','sha256','license')} for n in names}
    print('::notice::ODM-JXL-INTEGRATION '+json.dumps({'count':len(records),'packages':summary},sort_keys=True,separators=(',',':')),flush=True)
print('::notice::Private reduced-JXL ODM source build, relocated lock replay and Seneca raster passed; outputs discarded',flush=True)
