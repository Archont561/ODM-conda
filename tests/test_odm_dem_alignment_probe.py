"""Optional pinned-source research test; see research/odm-alignment-http-evidence.md."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def test_alignment_probe_observations():
    source = os.environ.get('ODM_TEST_SOURCE')
    if not source:
        pytest.skip('ODM_TEST_SOURCE must point to verified pinned ODM source')
    pytest.importorskip('numpy')
    pytest.importorskip('scipy')
    pytest.importorskip('rasterio')
    script = Path(__file__).resolve().parents[1] / 'scripts/odm_dem_alignment_probe.py'
    proc = subprocess.run([sys.executable, str(script), source], text=True, capture_output=True, check=True)
    observations = json.loads(proc.stdout)
    assert [item.get('different_pixels') for item in observations] == [0, 0, 0, 176, 0, 0]
    zero_case = observations[3]
    assert zero_case['expected_valid'] == 660 and zero_case['output_valid'] == 484
