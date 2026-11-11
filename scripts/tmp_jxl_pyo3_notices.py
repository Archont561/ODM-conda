import json
import tempfile
import urllib.request
from pathlib import Path
import yaml
from common import ROOT, sha256
from jxl_crate_notice_draft import stage
from private_odm_bundle import download_sdist
from prepare_jxl_reduced_research import prepare
from prepare_jxl_vendor_scope import CRATE_SHA256, prepare as scoped

with tempfile.TemporaryDirectory(prefix='jxl-notices-') as tmp:
    root=Path(tmp); info=yaml.safe_load((ROOT/'research/recipes/python-source-research/pillow-jxl-plugin.yaml').read_text())['source']
    archive=root/'src.tar.gz'; download_sdist(info['url'],info['sha256'],archive); prepared=prepare(archive,root/'prepared')
    crate=root/'jpegxl-src.crate'
    with urllib.request.urlopen('https://static.crates.io/crates/jpegxl-src/jpegxl-src-0.11.2.crate',timeout=90) as response: crate.write_bytes(response.read(100000000))
    assert sha256(crate)==CRATE_SHA256
    scoped(prepared,crate,root/'scope'); vendor=root/'scope/source/vendor'
    first=stage(vendor,root/'first'); second=stage(vendor,root/'second')
    assert first==second and sha256(root/'first/MANIFEST.json')==sha256(root/'second/MANIFEST.json')
    print('::notice::CRATE-NOTICE-DRAFT '+json.dumps({'count':len(first['files']),'manifest_sha256':sha256(root/'first/MANIFEST.json'),'crate_count':40},separators=(',',':')),flush=True)
