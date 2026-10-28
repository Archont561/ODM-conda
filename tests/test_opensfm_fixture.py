"""The OpenSfM research fixture must not accept missing native bindings."""
import subprocess
import sys

from common import ROOT


def test_opensfm_fixture_rejects_missing_installation(tmp_path):
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/opensfm_fixture.py'), str(tmp_path)],
                            text=True, capture_output=True, timeout=30)
    assert result.returncode != 0
    assert 'OpenSfM native bindings' in result.stderr
