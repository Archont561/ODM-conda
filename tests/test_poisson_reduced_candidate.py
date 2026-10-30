"""Local-only Poisson source candidate tests; no redistribution conclusion."""
import io
import json
import tarfile
from pathlib import Path

import pytest
from common import ScaffoldError


def fixture_archive(path: Path) -> None:
    with tarfile.open(path, 'w:gz') as archive:
        for name, data in [('Makefile', b'make'), ('Src/PoissonRecon.cpp', b'code'),
                           *[(f'JPEG/file{i}.c', f'jpeg{i}'.encode()) for i in range(59)]]:
            entry = tarfile.TarInfo('upstream/' + name)
            entry.size = len(data)
            archive.addfile(entry, io.BytesIO(data))


def test_reduced_candidate_is_deterministic_and_omits_vendored_jpeg(tmp_path, monkeypatch):
    import poisson_reduced_candidate as candidate
    from common import sha256
    source = tmp_path / 'source.tar.gz'
    fixture_archive(source)
    monkeypatch.setattr(candidate, 'PINNED_SHA256', sha256(source))
    monkeypatch.setattr(candidate, 'repository_files', lambda root: [root / 'recipe.yaml'])
    root = tmp_path / 'packaging'
    root.mkdir()
    (root / 'recipe.yaml').write_text('packaging')
    first, second = tmp_path / 'a.tar.gz', tmp_path / 'b.tar.gz'
    candidate.make_candidate(source, first, root=root)
    candidate.make_candidate(source, second, root=root)
    assert first.read_bytes() == second.read_bytes()
    with tarfile.open(first) as archive:
        names = archive.getnames()
        assert 'source/Makefile' in names and 'source/Src/PoissonRecon.cpp' in names
        assert 'source/JPEG' in names
        assert not any(name.startswith('source/JPEG/') for name in names)
        assert archive.extractfile('packaging/recipe.yaml').read() == b'packaging'
        manifest = json.load(archive.extractfile('CANDIDATE-MANIFEST.json'))
        assert manifest['excluded_file_count'] == 59
        assert manifest['scope'] == 'local-research-only'


def test_rejects_wrong_archive_and_existing_destination(tmp_path):
    import poisson_reduced_candidate as candidate
    source = tmp_path / 'source.tar.gz'
    fixture_archive(source)
    target = tmp_path / 'out.tar.gz'
    with pytest.raises(ScaffoldError, match='checksum'):
        candidate.make_candidate(source, target, root=tmp_path)
    assert not target.exists()
    target.write_bytes(b'keep')
    with pytest.raises(ScaffoldError, match='existing'):
        candidate.make_candidate(source, target, root=tmp_path)
    assert target.read_bytes() == b'keep'


def test_candidate_rejects_symlink_members_and_destination_inside_packaging(tmp_path, monkeypatch):
    import poisson_reduced_candidate as candidate
    from common import sha256
    source = tmp_path / 'unsafe.tar.gz'
    with tarfile.open(source, 'w:gz') as archive:
        link = tarfile.TarInfo('upstream/JPEG/escape')
        link.type = tarfile.SYMTYPE
        link.linkname = '../Makefile'
        archive.addfile(link)
    monkeypatch.setattr(candidate, 'PINNED_SHA256', sha256(source))
    packaging = tmp_path / 'packaging'
    packaging.mkdir()
    with pytest.raises(ScaffoldError, match='outside'):
        candidate.make_candidate(source, packaging / 'candidate.tar.gz', root=packaging)
    with pytest.raises(ScaffoldError, match='Unsupported'):
        candidate.make_candidate(source, tmp_path / 'candidate.tar.gz', root=packaging)
    assert not (tmp_path / 'candidate.tar.gz').exists()
