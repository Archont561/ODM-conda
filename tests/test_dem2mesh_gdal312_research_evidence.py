import json
from pathlib import Path


def test_research_evidence_has_one_added_identity_and_scope():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'research/odm-dem2mesh-gdal312-research-evidence.json').read_text())
    assert data['baseline_inventory_count'] == 432
    assert data['new_inventory_count'] == 433
    assert data['removed'] == [] and len(data['added']) == 1
    assert data['added'][0][0] == 'dem2mesh'
    assert data['added'][0][3] == data['candidate_sha256']
    assert 'libgdal-core >=3.12.2,<3.12.3' in data['depends']
    assert 'no rights' in data['scope'] and 'discarded' in data['retention']
