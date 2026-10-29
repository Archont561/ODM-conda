"""Research recipes must remain outside published components and workflow artifacts."""
import hashlib
import shutil
import subprocess

import pytest
import yaml

from common import ROOT, config


def test_open_research_recipes_have_sources_builds_and_installed_tests():
    for name, expected_sources in [('openmvs-odm', 3), ('opensfm-odm', 3)]:
        recipe = yaml.safe_load((ROOT / 'research/recipes' / name / 'recipe.yaml').read_text())
        assert recipe['package']['name'] == name
        assert len(recipe['source']) == expected_sources
        assert all(item.get('url', '').startswith(('https://codeload.github.com/', 'https://files.pythonhosted.org/')) and item.get('sha256') for item in recipe['source'])
        if name == 'opensfm-odm':
            assert recipe['source'][2]['sha256'] == '95fe9ba737edea8e5737fb9ddda7031d7ca62fd53f53c1c4e95195f3c7d801fd'
            assert {'rasterio', 'rawpy'} <= set(recipe['requirements']['run'])
        else:
            assert 'libboost-devel >=1.90,<1.91' in recipe['requirements']['host']
        assert recipe['build']['script']['file'].endswith('build_open_research.py')
        assert recipe['requirements']['build'] and recipe['requirements']['host'] and recipe['requirements']['run']
        assert any('script' in test for test in recipe['tests'])
        assert name not in config()['components']
        assert recipe['about']['license'] == 'LicenseRef-Unreviewed'
    patches = {
        'openmvs-odm/patches/0001-reconstruct-only.patch': '2dc920d550119443bb8d079911b0cdfc4cc747eb916a48a01e09ebdaf6a2c96a',
        'openmvs-odm/patches/0002-visibility-check.patch': '74f36291ca9254b2fe32c600c7e939827859aa1d07f73a976217961d39624c90',
        'openmvs-odm/patches/0003-boost-header-only-system.patch': '17b72610b3b803cd2a5002eb2a68c48fdcf55597d41b7fcb113634e833b18830',
        'openmvs-odm/patches/0004-ply-view-indices.patch': '4dbaa9e4fa186ce80f6c3f220c67a89bf80fea347bf798bd64a80fc096f03d6d',
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



def test_research_workflow_records_selected_component_safely():
    workflow = (ROOT / '.github/workflows/build-open-research.yml').read_text()
    assert 'run-name: "Local-only research: ${{ inputs.component }}"' in workflow
    assert 'RESEARCH_COMPONENT: ${{ inputs.component }}' in workflow
    assert 'pixi run python scripts/record_open_research_component.py' in workflow


@pytest.mark.parametrize('component', ['openmvs', 'opensfm', 'all'])
def test_research_component_annotation(component, tmp_path, capsys):
    from record_open_research_component import record_component

    summary = tmp_path / 'summary.md'
    record_component(component, summary)
    assert f'::notice title=Selected research component::{component}' in capsys.readouterr().out
    assert summary.read_text() == f'### Selected research component\n\n`{component}`\n'


def test_research_component_annotation_rejects_injection(tmp_path, capsys):
    from common import ScaffoldError
    from record_open_research_component import record_component

    summary = tmp_path / 'summary.md'
    with pytest.raises(ScaffoldError, match='Invalid research component'):
        record_component('openmvs\n::error::injected', summary)
    assert not summary.exists()
    assert not capsys.readouterr().out


@pytest.mark.parametrize('name', ['openmvs-odm', 'opensfm-odm'])
def test_research_audit_tracks_recipe_identity_and_critical_dependencies(name):
    from audit_open_research import verify_index

    recipe = yaml.safe_load((ROOT / 'research/recipes' / name / 'recipe.yaml').read_text())
    index = {'name': name, 'version': recipe['package']['version'],
             'build_number': recipe['build']['number'], 'subdir': 'linux-64',
             'depends': recipe['requirements']['run']}
    verify_index(name, index)


def test_research_all_runs_both_and_rejects_unknown(monkeypatch):
    import run_open_research as research
    from common import ScaffoldError

    seen = []
    monkeypatch.setattr(research, 'run_component', seen.append)
    monkeypatch.setenv('RESEARCH_COMPONENT', 'all')
    research.main()
    assert seen == ['openmvs', 'opensfm']
    monkeypatch.setenv('RESEARCH_COMPONENT', 'all\nopensfm')
    with pytest.raises(ScaffoldError):
        research.main()


def test_opensfm_research_uses_pdal_compatible_gflags_abi():
    import yaml
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    recipe = yaml.safe_load((root / 'research/recipes/opensfm-odm/recipe.yaml').read_text())
    assert recipe['build']['number'] == 2
    for scope in ('host', 'run'):
        assert 'gflags >=2.2.2,<2.3' in recipe['requirements'][scope]
