import json
import pytest
from common import ScaffoldError, sha256


def test_inventory_reports_mismatch_missing_and_filename_candidates(tmp_path, monkeypatch):
    import openmvs_notice_inventory as inventory
    root = tmp_path / 'tree'
    root.mkdir()
    (root / 'LICENSE').write_text('license')
    (root / 'changed.h').write_text('new')
    baseline = tmp_path / 'baseline.json'
    baseline.write_text(json.dumps({'entries': [
        {'path': 'LICENSE', 'sha256': sha256(root / 'LICENSE')},
        {'path': 'changed.h', 'sha256': '0' * 64},
        {'path': 'missing.h', 'sha256': '0' * 64}]}))
    monkeypatch.setattr(inventory, 'fingerprint_tree', lambda tree: inventory.EXPECTED_REDUCED_TREE)
    result = inventory.inventory(root, baseline)
    assert result['baseline_matched'] == 1
    assert result['baseline_missing'] == ['missing.h']
    assert result['baseline_changed'][0]['path'] == 'changed.h'
    assert result['notice_name_candidates'][0]['path'] == 'LICENSE'
    monkeypatch.setattr(inventory, 'fingerprint_tree', lambda tree: (0, 'wrong'))
    with pytest.raises(ScaffoldError, match='fingerprint'):
        inventory.inventory(root, baseline)
