"""Exercise the public multi-component build selector without building packages."""
import subprocess
import sys

import yaml

from common import ROOT


def render(selection):
    return subprocess.run([sys.executable, str(ROOT / 'scripts/build.py'), '--render-only',
                           '--component', selection], cwd=ROOT, text=True, capture_output=True, timeout=60)


def test_render_selected_recipes_in_requested_order():
    result = render('renderdem, dem2mesh')
    assert result.returncode == 0, result.stderr
    assert [line for line in result.stdout.splitlines() if line.startswith('Render: ')] == [
        'Render: renderdem', 'Render: dem2mesh']


def test_single_component_and_all_remain_available():
    single = render('dem2mesh')
    assert single.returncode == 0, single.stderr
    assert [line for line in single.stdout.splitlines() if line.startswith('Render: ')] == ['Render: dem2mesh']
    all_recipes = render('all')
    assert all_recipes.returncode == 0, all_recipes.stderr
    names = [line.removeprefix('Render: ') for line in all_recipes.stdout.splitlines() if line.startswith('Render: ')]
    from common import config
    assert set(names) == set(config()['components'])


def test_release_staging_still_rejects_multiple_components(tmp_path):
    destination = tmp_path / 'release'
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/stage_release.py'),
                             '--component', 'dem2mesh,renderdem', '--destination', str(destination)],
                            cwd=ROOT, text=True, capture_output=True, timeout=30)
    assert result.returncode != 0
    assert "exactly one component" in result.stderr
    assert not destination.exists()


def test_invalid_selection_is_rejected_before_any_recipe_is_rendered():
    for selection in ('', 'dem2mesh,no-such-recipe', 'dem2mesh,', 'all,dem2mesh',
                      'dem2mesh,dem2mesh', 'dem2mesh,$(touch unsafe)'):
        result = render(selection)
        assert result.returncode != 0, selection
        assert 'Render: ' not in result.stdout, selection


def test_workflow_passes_same_input_to_each_validation_stage():
    data = yaml.safe_load((ROOT / '.github/workflows/build.yml').read_text())
    dispatch = data.get('on', data.get(True))['workflow_dispatch']['inputs']['component']
    assert dispatch['type'] == 'string'
    assert dispatch['default'] == 'all'
    job = data['jobs']['build']
    assert job['env']['COMPONENT'] == '${{ inputs.component }}'
    for task in ('build', 'test', 'audit', 'sources'):
        assert f'pixi run {task} --component "$COMPONENT"' in [step.get('run') for step in job['steps']]
