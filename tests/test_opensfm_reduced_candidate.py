import io
import json
import tarfile
from pathlib import Path

import pytest
from common import ScaffoldError, sha256


def source_fixture(path, assets):
    with tarfile.open(path, 'w:gz') as archive:
        for name, data in [('opensfm/dataset.py', b'source'), *assets.items()]:
            member = tarfile.TarInfo('upstream/' + name)
            member.size = len(data)
            archive.addfile(member, io.BytesIO(data))


def test_candidate_is_reproducible_and_records_omissions(tmp_path, monkeypatch):
    import opensfm_reduced_candidate as candidate
    import hashlib
    assets = {'opensfm/data/a': b'a', 'opensfm/data/b': b'b', 'opensfm/data/c': b'c'}
    monkeypatch.setattr(candidate, 'EXCLUDED_ASSETS', {name.removeprefix('opensfm/'): hashlib.sha256(data).hexdigest() for name, data in assets.items()})
    source = tmp_path / 'original.tar.gz'
    source_fixture(source, assets)
    monkeypatch.setattr(candidate, 'PINNED_SHA256', sha256(source))
    one, two = tmp_path / 'one.tar.gz', tmp_path / 'two.tar.gz'
    candidate.make_candidate(source, one)
    candidate.make_candidate(source, two)
    assert one.read_bytes() == two.read_bytes()
    with tarfile.open(one) as archive:
        assert 'source/opensfm/dataset.py' in archive.getnames()
        assert not any('source/' + name in archive.getnames() for name in assets)
        manifest = json.load(archive.extractfile('source/CANDIDATE-MANIFEST.json'))
        assert len(manifest['excluded_files']) == 3
        assert manifest['files']['opensfm/dataset.py']['sha256'] == hashlib.sha256(b'source').hexdigest()


def test_candidate_fails_closed_on_asset_change(tmp_path, monkeypatch):
    import opensfm_reduced_candidate as candidate
    source = tmp_path / 'original.tar.gz'
    source_fixture(source, {'opensfm/data/a': b'changed'})
    monkeypatch.setattr(candidate, 'PINNED_SHA256', sha256(source))
    monkeypatch.setattr(candidate, 'EXCLUDED_ASSETS', {'data/a': '0' * 64})
    with pytest.raises(ScaffoldError, match='asset'):
        candidate.make_candidate(source, tmp_path / 'out.tar.gz')
    assert not (tmp_path / 'out.tar.gz').exists()
