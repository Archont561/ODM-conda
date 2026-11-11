import json
import tempfile
import urllib.request
from pathlib import Path
from common import ROOT, rattler, run, sha256

records=json.loads((ROOT/'research/pillow-jxl-native-package-evidence.json').read_text())['packages']
record=next(x for x in records if x['name']=='libjxl')
inventory=json.loads((ROOT/'research/odm-alternate-candidate-2026-11-07/conda-inventory.json').read_text())['packages']
entry=next(x for x in inventory if x['name']=='libjxl')
with tempfile.TemporaryDirectory(prefix='jxl-native-rebuild-') as tmp:
    root=Path(tmp); original=root/'original.conda'
    with urllib.request.urlopen(entry['binary_package_url'],timeout=90) as response: original.write_bytes(response.read(100000000))
    assert sha256(original)==record['sha256']
    output=root/'output'; run([rattler(),'rebuild','--package-file',str(original),'--output-dir',str(output),'--log-style','plain'])
    packages=list((output/'linux-64').glob('libjxl-*.conda')); assert len(packages)==1,packages
    run([rattler(),'test','--package-file',str(packages[0]),'--channel','conda-forge','--channel-priority','strict','--output-dir',str(root/'retest'),'--log-style','plain'])
    print('::notice::JXL-NATIVE-REBUILD '+json.dumps({'original_sha256':record['sha256'],'package':packages[0].name,'sha256':sha256(packages[0])},separators=(',',':')),flush=True)
