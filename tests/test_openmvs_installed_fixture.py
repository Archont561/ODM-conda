from pathlib import Path

import pytest


def test_installed_openmvs_fixture_rejects_success_without_results(tmp_path):
    from functional_test import test_openmvs

    fixture = tmp_path / 'fixture.py'
    fixture.write_text('pass\n', encoding='utf-8')
    with pytest.raises(AssertionError, match='Missing OpenMVS fixture evidence'):
        test_openmvs(Path('/bin/true'), tmp_path, fixture)


def test_installed_openmvs_fixture_rejects_missing_script(tmp_path):
    from functional_test import test_openmvs

    with pytest.raises(AssertionError, match='Missing OpenMVS fixture'):
        test_openmvs(Path('/bin/true'), tmp_path, tmp_path / 'missing.py')


def test_production_builder_copies_all_installed_fixture_dependencies(tmp_path):
    import ast
    from common import ROOT

    tree = ast.parse((ROOT / 'scripts/build_component.py').read_text())
    fixtures = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and isinstance(node.target, ast.Name) and node.target.id == 'fixture':
            if isinstance(node.iter, ast.Tuple):
                fixtures.update(item.value for item in node.iter.elts if isinstance(item, ast.Constant))
    assert {'openmvs_synthetic_fixture.py', 'openmvs_pointcloud_fixture.py',
            'openmvs_fixture.py', 'texrecon_fixture.py'} <= fixtures
