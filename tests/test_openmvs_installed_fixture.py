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
