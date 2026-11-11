import json
import tempfile
from pathlib import Path
import yaml
from common import ROOT, sha256
from private_odm_bundle import download_sdist
from prepare_jxl_reduced_research import prepare
with tempfile.TemporaryDirectory(prefix='jxl-notices-') as tmp:
    root=Path(tmp); info=yaml.safe_load((ROOT/'research/recipes/python-source-research/pillow-jxl-plugin.yaml').read_text())['source']
    archive=root/'src.tar.gz'; download_sdist(info['url'],info['sha256'],archive); tree=prepare(archive,root/'prepared')/'source/vendor/pyo3-0.25.1/pyo3-runtime'
    names=['LICENSE-APACHE','LICENSE-MIT']; print('::notice::PYO3-NESTED '+json.dumps({p:sha256(tree/p) for p in names},sort_keys=True,separators=(',',':')),flush=True)
