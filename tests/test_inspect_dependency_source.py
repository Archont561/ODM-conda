import hashlib
import io
import tarfile

import pytest

import inspect_dependency_source as probe
from common import ScaffoldError


@pytest.mark.parametrize('compression', ['gz', 'bz2', 'xz'])
def test_supported_archives(tmp_path, compression):
    path = tmp_path / 'source.tar'
    with tarfile.open(path, 'w:' + compression) as tar:
        member = tarfile.TarInfo('upstream/COPYING')
        member.size = 4
        tar.addfile(member, io.BytesIO(b'test'))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    report = probe.inspect(path, digest, 'upstream')
    assert report['archive']['file_count'] == 1
    assert report['archive']['notice_name_candidates'] == ['COPYING']
    assert report['archive']['files']['COPYING']['sha256'] == hashlib.sha256(b'test').hexdigest()
    with pytest.raises(ScaffoldError, match='mismatched'):
        probe.inspect(path, '0' * 64, 'upstream')


def test_invalid_arguments_and_links(tmp_path):
    path = tmp_path / 'source.tar.gz'
    with tarfile.open(path, 'w:gz') as tar:
        member = tarfile.TarInfo('upstream/link')
        member.type = tarfile.SYMTYPE
        member.linkname = 'target'
        tar.addfile(member)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ScaffoldError, match='Unsupported'):
        probe.inspect(path, digest, 'upstream')
    with pytest.raises(ScaffoldError, match='SHA256'):
        probe.inspect(path, 'bad', 'upstream')
    with pytest.raises(ScaffoldError, match='root'):
        probe.inspect(path, digest, '../upstream')
