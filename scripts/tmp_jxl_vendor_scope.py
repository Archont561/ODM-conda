import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml
from common import ROOT, sha256
from prepare_jxl_reduced_research import prepare
from private_odm_bundle import build_recipe, download_sdist

EXCLUDED=['cc-1.2.27','cmake-0.1.54','crunchy-0.2.4','jpegxl-src-0.11.2','portable-atomic-1.11.1','shlex-1.3.0']
with tempfile.TemporaryDirectory(prefix='jxl-prune-trial-') as tmp:
    root=Path(tmp); data=yaml.safe_load((ROOT/'research/recipes/python-source-research/pillow-jxl-plugin.yaml').read_text())['source']
    sdist=root/'source.tar.gz'; download_sdist(data['url'],data['sha256'],sdist)
    prepared=prepare(sdist,root/'prepared'); source=prepared/'source'; vendor=source/'vendor'
    env=os.environ.copy(); env['CARGO_HOME']=str(root/'empty-cargo-home'); env['CARGO_NET_OFFLINE']='true'
    def metadata():
        return subprocess.run(['cargo','metadata','--format-version','1','--locked','--offline'],cwd=source,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    baseline=metadata(); assert baseline.returncode==0, baseline.stderr
    probe=root/'probe-jpegxl-src'; (vendor/'jpegxl-src-0.11.2').rename(probe)
    missing=metadata(); print('::notice::JXL-MISSING '+json.dumps({'exit':missing.returncode,'stderr':missing.stderr[-1200:]},separators=(',',':')),flush=True)
    assert missing.returncode!=0
    probe.rename(vendor/'jpegxl-src-0.11.2')
    for name in EXCLUDED:
        crate=vendor/name; meta=json.loads((crate/'.cargo-checksum.json').read_text())
        manifest=crate/'Cargo.toml'; digest=sha256(manifest); assert meta['files']['Cargo.toml']==digest
        content=manifest.read_bytes(); package=meta['package']; shutil.rmtree(crate); crate.mkdir(); (crate/'Cargo.toml').write_bytes(content)
        (crate/'.cargo-checksum.json').write_text(json.dumps({'package':package,'files':{'Cargo.toml':digest}}))
    reduced=metadata(); print('::notice::JXL-MANIFEST-ONLY '+json.dumps({'exit':reduced.returncode,'stderr':reduced.stderr[-1200:]},separators=(',',':')),flush=True)
    assert reduced.returncode==0
    recipe=prepared/'recipe/recipe.yaml'; text=recipe.read_text(); marker='number: 2\n  string: research_reduced_${{ hash }}_2'; assert text.count(marker)==1
    recipe.write_text(text.replace(marker,'number: 3\n  string: research_vendor_scope_${{ hash }}_3'))
    package=build_recipe(recipe,'odm-research-pillow-jxl-plugin',root/'build')
    print('::notice::JXL-SCOPE-RESULT '+json.dumps({'trimmed_crates':EXCLUDED,'package':package.name,'sha256':sha256(package)},separators=(',',':')),flush=True)
