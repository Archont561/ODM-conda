import hashlib
import json


def test_comparison_distinguishes_payload_and_conda_metadata(monkeypatch):
    import compare_openmvs_notices as compare
    monkeypatch.setattr(compare, 'verify_index', lambda name, index: None)
    monkeypatch.setattr(compare, 'verify_payload', lambda name, payload: None)
    digest = hashlib.sha256(b'notice').hexdigest()
    inventory = {'reduced_tree_sha256':'tree', 'notice_name_candidates':[{'path':'LICENSE','sha256':digest}, {'path':'missing','sha256':'0'*64}]}
    info = {'info/index.json':json.dumps({}).encode(), 'info/licenses/lic.txt':b'notice'}
    payload = {'share/licenses/openmvs-odm/upstream.txt':b'notice'}
    result = compare.compare(info, payload, inventory)
    assert result['candidates'][0]['payload_matches'] == ['share/licenses/openmvs-odm/upstream.txt']
    assert result['candidates'][0]['metadata_matches'] == ['info/licenses/lic.txt']
    assert not result['candidates'][1]['payload_matches']
