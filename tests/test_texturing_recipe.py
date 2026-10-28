import subprocess
import sys

from common import ROOT, config


def test_texturing_recipe_is_registered_and_renders():
    component = config()['components']['mvs-texturing-odm']
    assert component['executable'] == 'texrecon'
    assert all(value is False for value in component['release_checks'].values())
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/build.py'), '--component', 'mvs-texturing-odm', '--render-only'],
                            cwd=ROOT, text=True, capture_output=True, timeout=60)
    assert result.returncode == 0, result.stderr
    assert 'Render: mvs-texturing-odm' in result.stdout


def test_texturing_recipe_lint_rejects_changed_target_and_patch(tmp_path):
    import shutil

    import pytest
    import yaml
    from common import ScaffoldError, repository_files
    from lint import check_repository

    for item in repository_files():
        target = tmp_path / item.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, target)
    assert check_repository(tmp_path) == 8
    path = tmp_path / 'recipes/mvs-texturing-odm/recipe.yaml'
    original = path.read_text(encoding='utf-8')
    recipe = yaml.safe_load(original)
    recipe['source'][1]['target_directory'] = 'other/location'
    path.write_text(yaml.safe_dump(recipe, sort_keys=False), encoding='utf-8')
    with pytest.raises(ScaffoldError, match='exact reviewed graph'):
        check_repository(tmp_path)
    path.write_text(original, encoding='utf-8')
    patch = path.parent / 'patches/0002-mve-baseline.patch'
    patch.write_bytes(patch.read_bytes() + b'\n')
    with pytest.raises(ScaffoldError, match='patch checksum'):
        check_repository(tmp_path)


def test_texturing_recipe_has_zlib_development_headers_for_cmake():
    import yaml

    recipe = yaml.safe_load((ROOT / 'recipes/mvs-texturing-odm/recipe.yaml').read_text(encoding='utf-8'))
    # FindPNG also invokes FindZLIB: libzlib is runtime-only and lacks the
    # unversioned library and headers needed in the isolated host environment.
    assert 'zlib' in recipe['requirements']['host']
