import hashlib
from pathlib import Path

import pytest
import yaml

from common import ScaffoldError
from build_openpointclass_research import CMAKE_SHA256, prepare_cmake


def test_unreviewed_cmake_fails_closed(tmp_path):
    (tmp_path/'CMakeLists.txt').write_text('unreviewed')
    archive = tmp_path/'lib.a'; archive.touch()
    with pytest.raises(ScaffoldError, match='Unexpected'):
        prepare_cmake(tmp_path, archive)


def test_research_inputs_and_scope():
    root = Path(__file__).resolve().parents[1]
    recipe = yaml.safe_load((root/'research/recipes/openpointclass-research/recipe.yaml').read_text())
    assert recipe['about']['license'] == 'LicenseRef-Unreviewed'
    assert len(recipe['source']) == 4
    assert recipe['package']['name'] == 'openpointclass-research'
    assert len(CMAKE_SHA256) == 64 and hashlib.sha256(b'unknown').hexdigest() != CMAKE_SHA256


def test_classification_fixture_requires_changed_finite_points(tmp_path):
    from openpointclass_synthetic_fixture import check_output
    csvfile = tmp_path/'out.csv'
    csvfile.write_text('X,Y,Z,Classification\n1,2,3,1\n1,2,4,5\n')
    assert check_output(csvfile, 2)['classification_counts'] == {1: 1, 5: 1}
    csvfile.write_text('X,Y,Z,Classification\n1,2,nan,5\n')
    with pytest.raises(ValueError, match='Nonfinite'):
        check_output(csvfile, 1)
    csvfile.write_text('X,Y,Z,Classification\n1,2,3,1\n')
    with pytest.raises(ValueError, match='No points classified'):
        check_output(csvfile, 1)
