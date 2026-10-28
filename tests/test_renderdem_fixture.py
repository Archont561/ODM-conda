from pathlib import Path

import pytest

from functional_test import test_renderdem as run_renderdem_fixture


def test_renderdem_fixture_rejects_missing_output(tmp_path):
    with pytest.raises((AssertionError, FileNotFoundError)):
        run_renderdem_fixture(Path('/bin/true'), tmp_path)
