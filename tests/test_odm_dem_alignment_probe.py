"""Optional verified-source regression; see research/odm-alignment-http-evidence.md."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


def test_zero_elevation_patch_with_installer(tmp_path):
    source = os.environ.get('ODM_TEST_SOURCE')
    if not source:
        pytest.skip('ODM_TEST_SOURCE must point to verified pinned ODM source')
    pytest.importorskip('numpy')
    pytest.importorskip('scipy')
    pytest.importorskip('rasterio')
    root = Path(__file__).resolve().parents[1]
    script = root / 'scripts/odm_dem_alignment_probe.py'
    def probe(app):
        proc = subprocess.run([sys.executable, str(script), str(app)], text=True, capture_output=True, check=True)
        return json.loads(proc.stdout)
    baseline = probe(source)
    assert [item.get('different_pixels') for item in baseline] == [0, 0, 0, 176, 112, 0, 0, 484]
    copied = tmp_path / 'source'
    shutil.copytree(source, copied)
    patches = root / 'research/recipes/odm-dense-research/patches'
    for patch in sorted(patches.glob('*.patch')):
        subprocess.run(['patch', '-p1', '-i', str(patch)], cwd=copied, check=True, capture_output=True)
    from build_odm_dense_research import install
    prefix = tmp_path / 'installed'; prefix.mkdir()
    install(copied, prefix)
    installed_app = prefix / 'share/odm-conda/odm-dense-research/app'
    fixed = probe(installed_app)
    assert [item.get('different_pixels') for item in fixed] == [0] * 8
    assert fixed[3]['expected_valid'] == fixed[3]['output_valid'] == 660
    assert fixed[4]['expected_valid'] == fixed[4]['output_valid'] == 660
    assert fixed[6]['expected_valid'] == fixed[6]['output_valid'] == 484
    assert fixed[7]['case'] == 'interpolation_zero'
    assert fixed[7]['output_valid'] == 484 and fixed[7]['center_value'] == 0
