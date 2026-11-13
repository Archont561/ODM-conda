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


def test_payload_evidence_matches_recorded_source_rpms():
    evidence = json.loads((ROOT / 'research/tetraflow-sysroot-rpm-evidence.json').read_text())
    signatures = json.loads((ROOT / 'research/tetraflow-sysroot-signature-evidence.json').read_text())
    payloads = json.loads((ROOT / 'research/tetraflow-srpm-payload-evidence.json').read_text())['source_rpms']
    expected = {r['filename']: r['observed_sha256'] for r in evidence['source_rpm_checks']}
    assert {p['source_rpm']: p['source_rpm_sha256'] for p in payloads} == expected
    listed = {r['name']: r for r in signatures['rpm_checks']}
    for payload in payloads:
        assert payload['file_count'] == listed[payload['source_rpm']]['file_count']
        assert payload['patch_count'] == listed[payload['source_rpm']]['patch_count']
        assert set(payload['specs']) == set(listed[payload['source_rpm']]['spec_files'])


def test_batch_review_references_prior_payload_and_trial():
    payloads = json.loads((ROOT / 'research/tetraflow-srpm-payload-evidence.json').read_text())['source_rpms']
    batch = json.loads((ROOT / 'research/tetraflow-batch-review-evidence.json').read_text())
    by_name = {p['source_rpm']: p for p in payloads}
    assert len(batch['specs']) == 2
    for spec in batch['specs']:
        source = by_name[spec['source_rpm']]
        assert spec['spec_sha256'] in {s['sha256'] for s in source['specs'].values()}
        for patch in spec['patch_samples']:
            assert patch['sha256'] == source['sample_patches'][patch['name']]['sha256']
        for archive in spec['nested_archives']:
            assert archive['sha256'] == source['archives'][archive['name']]['sha256']
    assert batch['linkage']['selected_binary_inputs'] == batch['linkage']['previous_trial_selected_inputs']
    assert 'libc.so.6' in batch['linkage']['needed']
