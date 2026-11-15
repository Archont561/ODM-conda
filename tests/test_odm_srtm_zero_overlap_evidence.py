import json
from pathlib import Path


def test_srtm_overlap_evidence_has_scope_and_provenance():
    root = Path(__file__).resolve().parents[1]
    evidence = json.loads((root / 'research/odm-srtm-zero-overlap-evidence.json').read_text())
    assert evidence['result']['overlap_zero_pixels'] == 31530
    assert evidence['result']['zero_pixels'] == 64042
    assert evidence['result']['positive_pixels'] == 474
    assert evidence['result']['max_abs_error'] == 0
    assert evidence['replay']['count'] == 436 and evidence['replay']['no_source_overlay']
    assert 'same input' in evidence['limitations'] and 'not been independently verified' in evidence['source']['repository_claim']
