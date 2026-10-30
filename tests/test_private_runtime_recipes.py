"""Private wheel repacks and research identities must stay explicit."""
import json
import re

import yaml
from common import ROOT


def test_five_private_wheels_are_hash_pinned_and_not_source_build_claims():
    path = ROOT / 'research/recipes/python-wheel-research'
    versions = {'pyodm': '1.5.12', 'pysolar': '0.13', 'pillow-jxl-plugin': '1.3.4',
                'pygltflib': '1.16.5', 'codem': '0.26.1'}
    assert {p.stem for p in path.glob('*.yaml')} == set(versions)
    snapshot = json.loads((ROOT/'research/odm-private-lock-replay-inventory.json').read_text())
    previous = {p['name']: p for p in snapshot['pypi_lock_records']}
    for name, version in versions.items():
        text = (path / (name + '.yaml')).read_text()
        data = yaml.safe_load(text)
        assert 'repackages the exact upstream wheel, not a source build' in text
        assert data['package'] == {'name': 'odm-research-' + name, 'version': version}
        assert data['source']['url'].startswith('https://files.pythonhosted.org/')
        assert data['source']['url'].endswith('.whl')
        assert re.fullmatch('[a-f0-9]{64}', data['source']['sha256'])
        assert previous[name]['version'] == version
        assert previous[name]['sha256'] == data['source']['sha256']
        assert previous[name]['binary_url'] == data['source']['url']
        assert data['build']['string'].startswith('research_')
        assert data['about']['license'] == 'LicenseRef-Unreviewed'


def test_odm_requires_private_identities_and_all_wheel_repackages():
    data = yaml.safe_load((ROOT/'research/recipes/odm-fast-research/recipe.yaml').read_text())
    deps = data['requirements']['run']
    for name in ('pyodm', 'pysolar', 'pillow-jxl-plugin', 'pygltflib', 'codem'):
        assert any(x.startswith('odm-research-' + name + ' ') for x in deps)
    for name in ('opensfm-scoped-odm', 'openmvs-odm', 'poissonrecon-odm', 'odm-orthophoto'):
        assert any(x.startswith(name + ' ') and x.endswith(' research_*') for x in deps)


def test_pure_python_candidates_use_the_exact_pypi_source_archives():
    expected = {
        'pyodm': 'd0433182ac6d5587786391c91d0eeafe0d78c71d618336af78964620dafe87c4',
        'pysolar': '05913740694e4bb2af8412de3fa278c0435b3b15b2975c8e38625fc4eed1fd6c',
        'pygltflib': '1f15740d5a7aaf71a5083e285af6b361184958e255659132f4ba8fe4f3d21ea9',
        'codem': 'e5e0f31c0da46f6087ad38e988d0c4351282d67c05f325f96c63a24f76c8dec6',
    }
    for name, digest in expected.items():
        recipe = yaml.safe_load((ROOT/'research/recipes/python-source-research'/(name+'.yaml')).read_text())
        assert recipe['source']['url'].startswith('https://files.pythonhosted.org/')
        assert recipe['source']['url'].endswith('.tar.gz')
        assert recipe['source']['sha256'] == digest
        assert recipe['build']['number'] == 1
        assert '--no-index' in recipe['build']['script']['content']
        assert '--no-build-isolation' in recipe['build']['script']['content']
