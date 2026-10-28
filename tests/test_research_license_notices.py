"""Research builds carry exact identified notices without claiming completeness."""
import hashlib

import pytest

from common import ScaffoldError
from research_license_notices import copy_notices, verify_notices


def test_notice_copy_and_verify_fail_closed(tmp_path):
    raw = b'known notice\n'
    source, target = tmp_path / 'source', tmp_path / 'licenses'
    source.mkdir()
    (source / 'COPYING').write_bytes(raw)
    spec = {'third-party.txt': (source / 'COPYING', hashlib.sha256(raw).hexdigest())}
    target.mkdir()
    copy_notices(spec, target)
    assert (target / 'third-party.txt').read_bytes() == raw
    verify_notices({'third-party.txt': raw}, {'third-party.txt': hashlib.sha256(raw).hexdigest()})
    for files in ({}, {'third-party.txt': b'altered'}):
        with pytest.raises(ScaffoldError, match='notice'):
            verify_notices(files, {'third-party.txt': hashlib.sha256(raw).hexdigest()})
    (source / 'COPYING').write_bytes(b'altered')
    with pytest.raises(ScaffoldError, match='notice'):
        copy_notices(spec, target)
    (source / 'COPYING').unlink()
    (source / 'COPYING').symlink_to('/etc/passwd')
    with pytest.raises(ScaffoldError, match='notice'):
        copy_notices(spec, target)


def test_openmvs_package_requires_each_notice(monkeypatch):
    import audit_open_research as audit

    raw = b'OpenMVS third-party notice'
    digest = hashlib.sha256(raw).hexdigest()
    monkeypatch.setattr(audit, 'OPENMVS_NOTICES', {'vcg.txt': ('vcg/LICENSE', digest)})
    share = 'share/odm-conda/openmvs-odm/'
    licenses = 'share/licenses/openmvs-odm/'
    payload = {share + name: b'x' for name in ('SOURCE.txt', 'functional_test.py',
        'openmvs_synthetic_fixture.py', 'openmvs_pointcloud_fixture.py', 'texrecon_fixture.py')}
    payload.update({licenses + 'upstream-LICENSE.txt': b'x', licenses + 'packaging-MIT.txt': b'x',
                    licenses + 'vcg.txt': raw, 'bin/ReconstructMesh': b'\x7fELFbinary'})
    audit.verify_payload('openmvs-odm', payload)
    for value in (None, b'tampered'):
        if value is None:
            payload.pop(licenses + 'vcg.txt', None)
        else:
            payload[licenses + 'vcg.txt'] = value
        with pytest.raises(ScaffoldError, match='notice'):
            audit.verify_payload('openmvs-odm', payload)


def test_committed_psutil_notice_is_byte_pinned():
    from common import ROOT
    from research_license_notices import PSUTIL_NOTICE_SHA256

    notice = ROOT / 'research/notices/psutil-2021-BSD-3-Clause.txt'
    assert hashlib.sha256(notice.read_bytes()).hexdigest() == PSUTIL_NOTICE_SHA256
