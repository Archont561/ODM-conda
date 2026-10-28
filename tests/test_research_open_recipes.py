"""Research recipes must remain outside published components and workflow artifacts."""
import hashlib
import shutil
import subprocess

import pytest
import yaml

from common import ROOT, config


def test_open_research_recipes_have_sources_builds_and_installed_tests():
    for name, expected_sources in [('openmvs-odm', 3), ('opensfm-odm', 2)]:
        recipe = yaml.safe_load((ROOT / 'research/recipes' / name / 'recipe.yaml').read_text())
        assert recipe['package']['name'] == name
        assert len(recipe['source']) == expected_sources
        assert all(item.get('url', '').startswith('https://codeload.github.com/') and item.get('sha256') for item in recipe['source'])
        assert recipe['build']['script']['file'].endswith('build_open_research.py')
        assert recipe['requirements']['build'] and recipe['requirements']['host'] and recipe['requirements']['run']
        assert any('script' in test for test in recipe['tests'])
        assert name not in config()['components']
        assert recipe['about']['license'] == 'LicenseRef-Unreviewed'
    patches = {
        'openmvs-odm/patches/0001-reconstruct-only.patch': '2dc920d550119443bb8d079911b0cdfc4cc747eb916a48a01e09ebdaf6a2c96a',
        'openmvs-odm/patches/0002-visibility-check.patch': '74f36291ca9254b2fe32c600c7e939827859aa1d07f73a976217961d39624c90',
        'opensfm-odm/patches/0001-ceres-config.patch': '1cbf2c8044e0281368c8802205f14816fc3b635fb419a7d8fa3570603fdfd773',
    }
    for path, digest in patches.items():
        assert hashlib.sha256((ROOT / 'research/recipes' / path).read_bytes()).hexdigest() == digest


@pytest.mark.parametrize('name', ['openmvs-odm', 'opensfm-odm'])
def test_research_recipe_renders_with_locked_rattler(name):
    binary = shutil.which('rattler-build')
    if binary is None:
        pytest.skip('rattler-build is not installed')
    result = subprocess.run([binary, 'build', '--recipe', str(ROOT / 'research/recipes' / name / 'recipe.yaml'),
                             '--target-platform', 'linux-64', '--variant-config', str(ROOT / 'recipes/variants.yaml'),
                             '--render-only'], cwd=ROOT, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr


def test_research_workflow_never_uploads_artifacts():
    workflow = (ROOT / '.github/workflows/build-open-research.yml').read_text()
    assert 'workflow_dispatch:' in workflow
    assert 'upload-artifact' not in workflow
    assert 'source_bundle.py' not in workflow
    assert 'pixi run python scripts/run_open_research.py' in workflow
