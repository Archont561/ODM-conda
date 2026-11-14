import json
from pathlib import Path


def test_failure_evidence_remains_bounded():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'research/odm-split-failure-isolation.json').read_text())
    assert data['image_count'] == 35
    assert 'errno 40' in data['unmodified_run']['result']
    assert 'temporary source modification' in data['strip_child_option_experiment']['source_overlay']
    assert data['pdal_merge_experiment']['lasmerge_in_path'] is False
    assert 'zero-byte' in data['pdal_merge_experiment']['result']
    assert 'No merge was validated' in data['scope']
