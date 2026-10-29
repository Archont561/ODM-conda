import hashlib
import io
import json
import tarfile
import zipfile

import pytest

from common import ScaffoldError
import inspect_poisson_artifact as inspection


def test_artifact_zip_is_pinned_exact_and_rejects_unsafe_entries(tmp_path, monkeypatch):
    path = tmp_path / 'artifact.zip'
    with zipfile.ZipFile(path, 'w') as archive:
        for filename in (inspection.PACKAGE, inspection.SOURCE, inspection.REPORT):
            archive.writestr('prefix/' + filename, filename)
    monkeypatch.setattr(inspection, 'ZIP_SHA', hashlib.sha256(path.read_bytes()).hexdigest())
    result = inspection.unpack_pinned_zip(path, tmp_path / 'out')
    assert result[inspection.PACKAGE].read_text() == inspection.PACKAGE
    with zipfile.ZipFile(path, 'a') as archive:
        archive.writestr('../oops', 'no')
    with pytest.raises(ScaffoldError, match='digest'):
        inspection.unpack_pinned_zip(path, tmp_path / 'out')
    monkeypatch.setattr(inspection, 'ZIP_SHA', hashlib.sha256(path.read_bytes()).hexdigest())
    with pytest.raises(ScaffoldError, match='Unsafe'):
        inspection.unpack_pinned_zip(path, tmp_path / 'out')


def test_source_bundle_manifest_checks_packaging_bytes(tmp_path, monkeypatch):
    path = tmp_path / 'source.tar.gz'
    names = ['packaging/recipes/poissonrecon-odm/patches/0001-system-libpng.patch',
             'packaging/scripts/poisson_linkage.py', 'packaging/scripts/poisson_png_smoke.cpp']
    values = {name: name.encode() for name in names}
    manifest = {'component': 'poissonrecon-odm', 'build_number': 2,
                'packaging_commit': '3ffabd94f2b1858b662e8ec66541fe5ac05fe3d5',
                'files': {name: hashlib.sha256(data).hexdigest() for name, data in values.items()}}
    values['SOURCE-MANIFEST.json'] = json.dumps(manifest).encode()
    with tarfile.open(path, 'w:gz') as archive:
        for name, data in values.items():
            item = tarfile.TarInfo(name)
            item.size = len(data)
            archive.addfile(item, io.BytesIO(data))
    monkeypatch.setattr(inspection, 'SOURCE_SHA', hashlib.sha256(path.read_bytes()).hexdigest())
    result = inspection.inspect_source(path)
    assert result['manifest_files_verified'] == 3
    assert result['patch_sha256'] == hashlib.sha256(names[0].encode()).hexdigest()
    path.write_bytes(path.read_bytes() + b'changed')
    with pytest.raises(ScaffoldError, match='SHA256'):
        inspection.inspect_source(path)
