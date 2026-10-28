import hashlib

import pytest

from common import ScaffoldError
import audit_open_research as audit


def test_vmem_payload_is_required_and_exact(tmp_path, monkeypatch):
    raw, license_text = b'vmem source', b'vmem license'
    monkeypatch.setattr(audit, 'VMEM_FILES', {'__init__.py': hashlib.sha256(raw).hexdigest()})
    monkeypatch.setattr(audit, 'VMEM_LICENSE_SHA256', hashlib.sha256(license_text).hexdigest())
    monkeypatch.setattr(audit, 'ASSETS', {})
    monkeypatch.setattr(audit, 'OPENSFM_NOTICES', {})
    monkeypatch.setattr(audit, 'PSUTIL_NOTICE_SHA256', hashlib.sha256(b'psutil notice').hexdigest())
    root = 'lib/python3.12/site-packages/'
    share = 'share/odm-conda/opensfm-odm/'
    licenses = 'share/licenses/opensfm-odm/'
    payload = {share + x: b'x' for x in ('SOURCE.txt', 'opensfm_main.py', 'opensfm_fixture.py', 'opensfm_assets_fixture.py')}
    payload.update({licenses + x: b'x' for x in ('upstream-LICENSE.txt', 'packaging-MIT.txt')})
    payload.update({'bin/opensfm': b'x', 'bin/opensfm_run_all': b'x',
                    licenses + 'vmem-LICENSE.txt': license_text, licenses + 'psutil-BSD-3-Clause.txt': b'psutil notice',
                    root + 'vmem/__init__.py': raw})
    for name in ('pygeo', 'pygeometry', 'pyrobust', 'pybundle', 'pyfeatures', 'pydense', 'pysfm', 'pymap'):
        payload[root + f'opensfm/{name}.test.so'] = b'\x7fELFbinary'
    audit.verify_payload('opensfm-odm', payload)
    del payload[licenses + 'psutil-BSD-3-Clause.txt']
    with pytest.raises(ScaffoldError, match='notice'):
        audit.verify_payload('opensfm-odm', payload)
    payload[licenses + 'psutil-BSD-3-Clause.txt'] = b'tampered'
    with pytest.raises(ScaffoldError, match='notice'):
        audit.verify_payload('opensfm-odm', payload)
    payload[licenses + 'psutil-BSD-3-Clause.txt'] = b'psutil notice'
    payload[root + 'vmem/__init__.py'] = b'modified'
    with pytest.raises(ScaffoldError, match='vmem file'):
        audit.verify_payload('opensfm-odm', payload)
