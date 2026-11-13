"""Validate recorded trial metadata, not the hosted execution or rights."""
import json
from pathlib import Path


def test_published_integration_records_exact_three_approved_identities():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'research/odm-published-component-integration.json').read_text())
    assert data['schema_version'] == 1
    assert 'not a release solve' in data['scope']
    records = {p['name']: (p['build'], p['sha256']) for p in data['records']}
    assert records == {
        'fpcfilter': ('h873e7db_1', '8d3949bf9fdb570e30afbcd91174ee5f80e9b8cd06525a26899642bc5ed1e679'),
        'dem2points': ('h873e7db_2', 'd7876edf091b2990e1b9325e0f6cd0ae2a4e863ab5499edacf267e5d3fd4996f'),
        'fastrasterfilter': ('h873e7db_2', '2738b09958d6b57360065ca5e68b1bcbe96a6f5c727cd0e3cdba1f8b018096c4'),
    }
    assert data['total_inventory_count'] == 432
