"""Check recorded metadata consistency, not original downloads or rights."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_sysroot_evidence_references_trial_and_named_sources():
    inventory_path = ROOT / 'research/tetraflow-build-input-inventory.json'
    evidence = json.loads((ROOT / 'research/tetraflow-sysroot-rpm-evidence.json').read_text())
    assert hashlib.sha256(inventory_path.read_bytes()).hexdigest() == evidence['inventory_sha256']
    trial = json.loads(inventory_path.read_text())
    build = {p['name']: p['sha256'] for p in trial['build']}
    assert evidence['sysroot_conda_sha256'] == build['sysroot_linux-64']
    assert evidence['kernel_headers_conda']['sha256'] == build['kernel-headers_linux-64']
    assert evidence['kernel_headers_conda']['sources_equal_sysroot'] is True
    binaries = evidence['binary_rpm_checks']
    sources = evidence['source_rpm_checks']
    assert len(binaries) == 8 and len(sources) == 2
    assert all(r['declared_sha256'] == r['verified_sha256'] for r in binaries)
    assert all(r['observed_sha256'] == r['repository_sha256'] for r in sources)
    assert {r['rpm_identity'].split('|')[-1] for r in binaries} == {r['filename'] for r in sources}


def test_signature_evidence_covers_recorded_rpms():
    evidence = json.loads((ROOT / 'research/tetraflow-sysroot-rpm-evidence.json').read_text())
    signatures = json.loads((ROOT / 'research/tetraflow-sysroot-signature-evidence.json').read_text())
    expected = {r['url'].rsplit('/', 1)[-1]: r['verified_sha256'] for r in evidence['binary_rpm_checks']}
    expected.update({r['filename']: r['observed_sha256'] for r in evidence['source_rpm_checks']})
    checks = signatures['rpm_checks']
    assert len(checks) == len(expected) == 10
    assert {r['name']: r['sha256'] for r in checks} == expected
    assert signatures['errors'] == []
    assert signatures['key']['fingerprints'][0] == '5E9B8F5617B5066CE92057C3488FCF7C3ABB34F8'
    assert all(any('Signature' in line and 'OK' in line for line in r['signature_lines']) for r in checks)
