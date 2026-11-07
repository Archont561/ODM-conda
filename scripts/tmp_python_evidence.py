import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
import yaml
from common import ROOT, sha256
from package_archive import read_package
from private_odm_bundle import build_recipe, download_sdist
from prepare_jxl_source import prepare

name = os.environ['COMPONENT']
allowed = {'codem', 'pillow-jxl-plugin', 'pygltflib', 'pyodm', 'pysolar'}
assert name in allowed
with tempfile.TemporaryDirectory(prefix='python-research-') as temp:
    root = Path(temp)
    recipe = ROOT/'research/recipes/python-source-research'/f'{name}.yaml'
    if name == 'pillow-jxl-plugin':
        data = yaml.safe_load(recipe.read_text())['source']
        source = root/'source.tar.gz'
        download_sdist(data['url'], data['sha256'], source)
        prepare(source,root/'prepared')
        recipe = root/'prepared/recipe/recipe.yaml'
    package = build_recipe(recipe, 'odm-research-'+name, root/'build')
    info, payload = read_package(package)
    about = json.loads(info['info/about.json'])
    index = json.loads(info['info/index.json'])
    notices = {path:hashlib.sha256(data).hexdigest() for path,data in (info|payload).items() if re.search(r'(^|/)(licen[sc]e|copying|notice)([./_-]|$)',path,re.I)}
    python_metadata = {path:hashlib.sha256(data).hexdigest() for path,data in payload.items() if '.dist-info/' in path and ('LICENSE' in path.upper() or path.endswith('/METADATA'))}
    result={'name':name,'package':package.name,'sha256':sha256(package),'license':about.get('license'),'depends':index.get('depends'),'notice_files':notices,'python_metadata':python_metadata,'payload_count':len(payload)}
    print('::notice::PYTHON-RESEARCH '+json.dumps(result,sort_keys=True,separators=(',',':')),flush=True)
