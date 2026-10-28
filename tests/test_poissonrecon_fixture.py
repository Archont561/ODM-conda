from pathlib import Path

import pytest

from functional_test import test_poissonrecon as run_poisson_fixture


def test_poisson_fixture_rejects_missing_output(tmp_path):
    with pytest.raises((AssertionError, FileNotFoundError)):
        run_poisson_fixture(Path('/bin/true'), tmp_path)
