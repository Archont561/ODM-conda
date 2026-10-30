"""Private source builds and research identities must stay explicit."""
import yaml
from common import ROOT


def test_odm_requires_private_identities_and_all_source_builds():
    data = yaml.safe_load((ROOT/'research/recipes/odm-fast-research/recipe.yaml').read_text())
    deps = data['requirements']['run']
    for name in ('pyodm', 'pysolar', 'pillow-jxl-plugin', 'pygltflib', 'codem'):
        assert any(x.startswith('odm-research-' + name + ' ') and x.endswith(' research_*_1') for x in deps)
    for name in ('opensfm-scoped-odm', 'openmvs-odm', 'poissonrecon-odm', 'odm-orthophoto'):
        assert any(x.startswith(name + ' ') and x.endswith(' research_*') for x in deps)


def test_pure_python_candidates_use_the_exact_pypi_source_archives():
    expected = {
        'pyodm': 'd0433182ac6d5587786391c91d0eeafe0d78c71d618336af78964620dafe87c4',
        'pysolar': '05913740694e4bb2af8412de3fa278c0435b3b15b2975c8e38625fc4eed1fd6c',
        'pygltflib': '1f15740d5a7aaf71a5083e285af6b361184958e255659132f4ba8fe4f3d21ea9',
        'codem': 'e5e0f31c0da46f6087ad38e988d0c4351282d67c05f325f96c63a24f76c8dec6',
        'pillow-jxl-plugin': '8ea589fc559ea7c5dfccb42af4d8148f5db508f5f4d4518328bab5a31fcb268e',
    }
    for name, digest in expected.items():
        recipe = yaml.safe_load((ROOT/'research/recipes/python-source-research'/(name+'.yaml')).read_text())
        assert recipe['source']['url'].startswith('https://files.pythonhosted.org/')
        assert recipe['source']['url'].endswith('.tar.gz')
        assert recipe['source']['sha256'] == digest
        assert recipe['build']['number'] == 1
        assert '--no-index' in recipe['build']['script']['content']
        if name == 'pillow-jxl-plugin':
            assert "'--offline'" in recipe['build']['script']['content']
            assert "'--auditwheel', 'skip'" in recipe['build']['script']['content']
        assert '--no-build-isolation' in recipe['build']['script']['content']
