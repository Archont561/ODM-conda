"""Consistency checks for bounded hosted compatibility evidence."""
import json
from pathlib import Path


def test_orthophoto_evidence_records_conflicting_ranges():
    root = Path(__file__).resolve().parents[1]
    evidence = json.loads((root/'research/odm-published-orthophoto-compatibility.json').read_text())
    assert evidence['sha256'] == 'c64be4380202cfe6e41cc41ac4ec171d25f2ceaaf45b666a21a2250f3b6ae614'
    assert evidence['retest_passed'] is True and evidence['solver_exit_code'] != 0
    assert evidence['declared_opencv'] == ['libopencv >=4.12,<4.13', 'libopencv >=4.12.0,<4.12.1.0a0']
    assert evidence['tetraflow_host_opencv'] == 'libopencv >=4.13,<4.14'
