import json
from pathlib import Path


def test_real_data_zero_evidence_distinguishes_intervention():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / 'research/odm-real-data-zero-evidence.json').read_text())
    assert data['zero_intervention']['patch_pixels'] == 64
    assert data['zero_intervention']['preserved_zero_pixels'] == 64
    assert data['zero_intervention']['original_patch_range'][0] > 200
    assert data['pipeline']['images'] == 35 and data['pipeline']['submodels'] == 2
    assert data['pipeline']['direct_app_scope_bypass']
    assert data['replay']['no_source_overlay'] and data['replay']['no_binary_overlay']
    assert 'deliberately injected' in data['limitations']
