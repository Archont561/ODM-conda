"""Validation preflight must fail without installed executables."""
import pytest
from common import ScaffoldError
from validate_renderdem_laz import validate


def test_requires_renderdem_and_pdal(tmp_path):
    (tmp_path/'bin').mkdir()
    with pytest.raises(ScaffoldError, match='renderdem and the separate pdal CLI'):
        validate(tmp_path)
    (tmp_path/'bin/renderdem').write_text('')
    with pytest.raises(ScaffoldError, match='renderdem and the separate pdal CLI'):
        validate(tmp_path)
