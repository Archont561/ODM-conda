import json
from pathlib import Path


def test_artifact_replay_evidence_is_bounded_and_scoped():
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'research/odm-temporary-artifact-replay-evidence.json').read_text())
    assert data['artifact_id']==14083906866
    assert data['manifest_sha256']=='81da120940a5236657854b51b9713aae0e40dbd11199a51859197837e21c3c7b'
    assert len(data['local_packages'])==15 and data['inventory_package_count']==432
    assert data['fixture_results']['formats']==['las','laz','hdf','icebridge']
    assert data['fixture_results']['point_count']==3
    assert 'no final release' in data['scope']
