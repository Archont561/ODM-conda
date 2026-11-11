import json
import tempfile
import yaml
from pathlib import Path
from common import ROOT, sha256
from package_archive import read_package
from prepare_jxl_reduced_research import prepare, CANDIDATE_SHA256, FIXTURE
from private_odm_bundle import build_recipe, download_sdist

with tempfile.TemporaryDirectory(prefix='jxl-scoped-validation-') as tmp:
    root=Path(tmp)
    recipe=ROOT/'research/recipes/python-source-research/pillow-jxl-plugin.yaml'
    source_info=yaml.safe_load(recipe.read_text())['source']; archive=root/'source.tar.gz'
    download_sdist(source_info['url'],source_info['sha256'],archive)
    prepared=prepare(archive,root/'prepared')
    package=build_recipe(prepared/'recipe/recipe.yaml','odm-research-pillow-jxl-plugin',root/'build')
    info,payload=read_package(package)
    index=json.loads(info['info/index.json']); assert index['build'].startswith('research_reduced_') and index['build_number']==2
    assert not any('/test/images/' in path for path in payload)
    print('::notice::JXL-SCOPED '+json.dumps({'package':package.name,'sha256':sha256(package),'candidate_sha256':CANDIDATE_SHA256,'fixture_sha256':sha256(FIXTURE),'payload_count':len(payload),'license':json.loads(info['info/about.json']).get('license')},separators=(',',':'),sort_keys=True),flush=True)
