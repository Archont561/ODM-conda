import json
from pathlib import Path


def test_zero_elevation_packaged_evidence_scope():
    root = Path(__file__).resolve().parents[1]
    evidence = json.loads((root / 'research/odm-zero-elevation-package-evidence.json').read_text())
    assert evidence['replay']['count'] == 436
    assert evidence['replay']['odm_package'].endswith('_6.conda')
    assert evidence['replay']['no_binary_overlay'] and evidence['replay']['no_source_overlay']
    for result in evidence['zero_fixture'].values():
        assert result == {'nodata_pixels': 28, 'valid_zero_pixels': 36}
    assert evidence['distance_fixture']['max_weighted_error'] == 0
    assert 'not a real dataset' in evidence['limitations'].lower()
