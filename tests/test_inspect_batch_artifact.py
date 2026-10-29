import hashlib
import json
import tarfile
import zipfile

import pytest

from common import ScaffoldError
import inspect_batch_artifact as inspection
from source_bundle import add_bytes


def test_zip_rejects_duplicate_basenames_and_traversal(tmp_path, monkeypatch):
    path = tmp_path / 'artifact.zip'
    for names in [('a/x', 'b/x'), ('../bad',)]:
        with zipfile.ZipFile(path, 'w') as archive:
            for name in names:
                archive.writestr(name, 'data')
        monkeypatch.setattr(inspection, 'ZIP_SHA', hashlib.sha256(path.read_bytes()).hexdigest())
        with pytest.raises(ScaffoldError):
            inspection.extract(path, tmp_path / 'out')


def test_source_manifest_rejects_mismatched_hash(tmp_path, monkeypatch):
    path = tmp_path / 'source.tar.gz'
    component = {'version': '1', 'build_number': 0, 'source': {}}
    monkeypatch.setattr(inspection, 'REVISION', 'r')
    manifest = {'component': 'demo', 'version': '1', 'build_number': 0, 'upstream': {},
                'packaging_commit': 'r', 'files': {'upstream/data': '0' * 64}}
    with tarfile.open(path, 'w:gz') as archive:
        add_bytes(archive, 'SOURCE-MANIFEST.json', json.dumps(manifest).encode())
        add_bytes(archive, 'README-SOURCE.txt', b'x')
        add_bytes(archive, 'upstream/data', b'not-matching')
    with pytest.raises(ScaffoldError, match='digest mismatch'):
        inspection.inspect_source(path, 'demo', component)
