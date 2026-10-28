from pathlib import Path

import pytest


def test_installed_texrecon_fixture_rejects_success_without_results(tmp_path):
    from functional_test import test_texturing

    fixture = tmp_path / 'fixture.py'
    fixture.write_text('pass\n', encoding='utf-8')
    with pytest.raises(AssertionError, match='Missing texrecon fixture evidence'):
        test_texturing(Path('/bin/true'), tmp_path, fixture)


def test_installed_texrecon_fixture_rejects_missing_script(tmp_path):
    from functional_test import test_texturing

    with pytest.raises(AssertionError, match='Missing texrecon fixture'):
        test_texturing(Path('/bin/true'), tmp_path, tmp_path / 'missing.py')
