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


def test_workflow_has_boolean_checkboxes_for_every_implemented_component():
    from common import config
    data = yaml.safe_load((ROOT / '.github/workflows/build.yml').read_text())
    dispatch = data.get('on', data.get(True))['workflow_dispatch']['inputs']
    names = {name.replace('-', '_'): name for name in config()['components']}
    assert set(dispatch) == set(names)
    assert all(item['type'] == 'boolean' and item['default'] is False for item in dispatch.values())
    job = data['jobs']['build']
    for input_name in names:
        key = 'SELECT_' + input_name.upper()
        assert job['env'][key] == '${{ inputs.' + input_name + ' }}'
    commands = [step.get('run') for step in job['steps']]
    assert 'pixi run build --workflow-checkboxes' in commands
    for task in ('test', 'audit', 'sources'):
        assert f'pixi run {task} --component "$COMPONENT"' in commands


def run_checkbox_selection(tmp_path, selected, *, invalid=None):
    import os
    from common import config
    env = os.environ.copy()
    for name in config()['components']:
        key = 'SELECT_' + name.replace('-', '_').upper()
        env[key] = 'true' if name in selected else 'false'
    if invalid:
        for key, value in invalid.items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value
    envfile = tmp_path / 'github-env'
    env['GITHUB_ENV'] = str(envfile)
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/build.py'), '--render-only', '--workflow-checkboxes'],
                            cwd=ROOT, env=env, text=True, capture_output=True, timeout=60)
    return result, envfile


def test_checkbox_selection_builds_only_checked_recipes(tmp_path):
    result, envfile = run_checkbox_selection(tmp_path, {'dem2mesh', 'renderdem'})
    assert result.returncode == 0, result.stderr
    assert {line for line in result.stdout.splitlines() if line.startswith('Render: ')} == {
        'Render: dem2mesh', 'Render: renderdem'}
    assert envfile.read_text().strip() == 'COMPONENT=dem2mesh,renderdem'


def test_no_checkboxes_defaults_to_all(tmp_path):
    from common import config
    result, envfile = run_checkbox_selection(tmp_path, set())
    assert result.returncode == 0, result.stderr
    assert envfile.read_text().strip() == 'COMPONENT=all'
    rendered = {line.removeprefix('Render: ') for line in result.stdout.splitlines() if line.startswith('Render: ')}
    assert rendered == set(config()['components'])


def test_invalid_checkbox_value_fails_before_rendering(tmp_path):
    for value in ('bad', 'true\nCOMPONENT=all', None):
        result, envfile = run_checkbox_selection(tmp_path, set(), invalid={'SELECT_DEM2MESH': value})
        assert result.returncode != 0
        assert 'Render: ' not in result.stdout
        assert not envfile.exists()
