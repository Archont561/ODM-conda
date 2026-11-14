import os
from pathlib import Path

import pytest
import yaml

from common import ScaffoldError
from build_odm_dense_research import install
from odm_dense_research_launcher import validate_args


def test_dense_research_installer_and_relocation(tmp_path):
    source = tmp_path/'source'; source.mkdir()
    (source/'run.py').write_text('pass\n'); (source/'VERSION').write_text('3.6.2\n')
    (source/'opendm').mkdir(); (source/'opendm/context.py').write_text('ODM_CONDA_LOCAL_PREFIX')
    prefix = tmp_path/'prefix'; prefix.mkdir(); install(source, prefix)
    assert (prefix/'share/odm-conda/odm-dense-research/app/LOCAL-ONLY.txt').is_file()
    launcher = prefix/'bin/odm-dense-research'
    assert os.access(launcher, os.X_OK) and str(prefix) not in launcher.read_text()
    with pytest.raises(ScaffoldError, match='exists'):
        install(source, prefix)


def test_scope_rejections():
    validate_args(['--help'])
    for flag in ('--dtm', '--fast-orthophoto', '--split=100', '--pc-classify', '--sm-cluster'):
        with pytest.raises(ScaffoldError, match='outside'):
            validate_args([flag])


def test_dense_recipe_dependency_contract():
    root = Path(__file__).resolve().parents[1]
    recipe = yaml.safe_load((root/'research/recipes/odm-dense-research/recipe.yaml').read_text())
    assert recipe['package']['name'] == 'odm-dense-research'
    deps = recipe['requirements']['run']
    assert 'openmvs-dense-research ==0.0.0.dev20260827 research_cpucompat_*_3' in deps
    assert 'dem2mesh ==0.0.0.dev20231207 research_*_1' in deps
    assert not any(dep.startswith('openmvs-tetraflow-research') for dep in deps)
    assert recipe['about']['license'] == 'LicenseRef-Unreviewed'
