import json
from pathlib import Path


def test_counterfactual_evidence_records_limits():
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'research/odm-raster-counterfactual-evidence.json').read_text())
    report=data['report']
    assert report['coverage_pixels']==1024
    assert report['dem_overlap_value']==150 and report['cutline_value']==195
    assert report['ortho_order_changed_pixels']==512
    assert report['ortho_max_adjacent_step']==50 and report['dem_max_adjacent_step']==50
    assert 'not actual georeferencing accuracy' in data['limitations']
    assert data['replay']['no_source_overlay'] and data['replay']['no_binary_overlay']
