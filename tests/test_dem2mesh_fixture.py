from pathlib import Path

import pytest

from functional_test import test_dem2mesh as run_dem2mesh_fixture


def test_dem2mesh_fixture_rejects_no_output(tmp_path):
    with pytest.raises((AssertionError, FileNotFoundError)):
        run_dem2mesh_fixture(Path('/bin/true'), tmp_path)
