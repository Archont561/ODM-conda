"""Guard the shape of metadata-only trial evidence, not the hosted build itself."""
import json
import re
from pathlib import Path


def test_trial_metadata_is_bounded_and_unambiguously_research_only():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'research/odm-tetraflow-private-trial-identities.json').read_text())
    assert data['schema_version'] == 1
    assert 'not release selection' in data['scope']
    assert data['inventory_record_count'] == 438
    packages = data['local_packages']
    assert len(packages) == data['package_count'] == 15
    assert len({p['filename'] for p in packages}) == 15
    assert all(p['filename'].endswith('.conda') and '/' not in p['filename'] for p in packages)
    assert all(re.fullmatch(r'[a-f0-9]{64}', p['sha256']) for p in packages)
    assert all(re.fullmatch(r'[a-f0-9]{64}', data[k]) for k in ('lock_sha256','manifest_sha256','inventory_sha256'))
