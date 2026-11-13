import hashlib
import io
import json
import tarfile
from pathlib import Path

import pytest

from inventory_odm_full_scope import MARKERS, ROOT, read_inventory


def make_archive(path, members):
    with tarfile.open(path, 'w:gz') as tar:
        for name, body in members:
            payload = body.encode()
            info = tarfile.TarInfo(ROOT + name)
            info.size = len(payload)
            tar.addfile(info, io.BytesIO(payload))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def valid_members():
    files = {'requirements.txt': '# comment\nrawpy==0.25.0\npyodm==1.5.12\n'}
    for path, marker in MARKERS.values():
        files[path] = files.get(path, '') + marker + '\n'
    return list(files.items())


def test_inventory_and_hash_verification(tmp_path):
    archive = tmp_path/'source.tar.gz'
    digest = make_archive(archive, valid_members())
    result = read_inventory(archive, digest)
    assert result['requirements'][0] == {'name': 'rawpy', 'version': '0.25.0'}
    assert set(result['feature_markers']) == set(MARKERS)
    with pytest.raises(ValueError, match='SHA256'):
        read_inventory(archive, '0'*64)


def test_rejects_duplicates_missing_markers_and_invalid_requirements(tmp_path):
    archive = tmp_path/'source.tar.gz'
    cases = [valid_members()+[('requirements.txt', 'rawpy==0.25.0')],
             valid_members()[:-1],
             [('requirements.txt', 'rawpy>=1')]+valid_members()[1:]]
    for members in cases:
        digest = make_archive(archive, members)
        with pytest.raises(ValueError):
            read_inventory(archive, digest)


def test_recorded_inventory_has_full_feature_markers():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'research/odm-full-scope-source-inventory.json').read_text())
    assert set(data['feature_markers']) == set(MARKERS)
    assert {'rawpy', 'pyodm', 'codem'} <= {x['name'] for x in data['requirements']}
    assert 'not runtime' in data['scope']
