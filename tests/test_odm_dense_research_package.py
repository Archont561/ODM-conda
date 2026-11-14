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
    (source/'opendm').mkdir(); (source/'opendm/context.py').write_text('ODM_CONDA_LOCAL_PREFIX'); (source/'opendm/ai.py').write_text('ODM_CONDA_MODEL_ROOT')
    prefix = tmp_path/'prefix'; prefix.mkdir(); install(source, prefix)
    assert (prefix/'share/odm-conda/odm-dense-research/app/LOCAL-ONLY.txt').is_file()
    launcher = prefix/'bin/odm-dense-research'
    assert os.access(launcher, os.X_OK) and str(prefix) not in launcher.read_text()
    with pytest.raises(ScaffoldError, match='exists'):
        install(source, prefix)


def test_scope_rejections():
    validate_args(['--help'])
    for flag in ('--dtm', '--fast-orthophoto', '--split=100', '--split-image-groups=groups.txt', '--sm-cluster'):
        with pytest.raises(ScaffoldError, match='outside'):
            validate_args([flag])


def test_dense_recipe_dependency_contract():
    root = Path(__file__).resolve().parents[1]
    recipe = yaml.safe_load((root/'research/recipes/odm-dense-research/recipe.yaml').read_text())
    assert recipe['package']['name'] == 'odm-dense-research'
    deps = recipe['requirements']['run']
    assert 'openmvs-dense-research ==0.0.0.dev20260827 research_cpucompat_*_3' in deps
    assert 'dem2mesh ==0.0.0.dev20231207 research_*_1' in deps
    assert 'openpointclass-research ==0.0.0.dev20250823 research_*_1' in deps
    assert not any(dep.startswith('openmvs-tetraflow-research') for dep in deps)
    assert recipe['about']['license'] == 'LicenseRef-Unreviewed'


def test_dense_integration_evidence_and_patch():
    import json
    from common import sha256
    root = Path(__file__).resolve().parents[1]
    patch = root/'research/recipes/openmvs-dense-research/patches/odm-dense-ply.patch'
    assert sha256(patch) == '124c2cefce29a7f78875e2b3928ac8d46da2c34b96d098b648924f99adc8d660'
    data = json.loads((root/'research/odm-dense-package-integration-evidence.json').read_text())
    assert data['no_binary_overlay'] and data['relocated_locked_replay']
    assert data['images'] == 35 and data['package_count'] == 435
    assert data['standalone_dense_points'] == 27942
    assert 'skip-3dmodel' in data['pipeline'] and 'not full ODM' in data['scope']
    assert len(data['packages']) == 3 and 'discarded' in data['retention']


def test_classification_requires_anchored_external_model(tmp_path, monkeypatch):
    import hashlib
    import odm_dense_research_launcher as launcher

    model = tmp_path/'openpointclass/v1_0_0/model.bin'
    model.parent.mkdir(parents=True)
    model.write_bytes(b'fixture only')
    monkeypatch.setattr(launcher, 'MODEL_SHA256', hashlib.sha256(b'fixture only').hexdigest())
    assert launcher.checked_model_root(str(tmp_path)) == tmp_path.resolve()
    model.write_bytes(b'unexpected')
    with pytest.raises(ScaffoldError, match='hash mismatch'):
        launcher.checked_model_root(str(tmp_path))
    with pytest.raises(ScaffoldError, match='absolute'):
        launcher.checked_model_root('relative')
    model.unlink(); model.symlink_to('/etc/passwd')
    with pytest.raises(ScaffoldError, match='unsafe'):
        launcher.checked_model_root(str(tmp_path))
