import hashlib

import pytest

import audit_tetraflow_research as audit
from common import ROOT, ScaffoldError


def good_index():
    return {'name': audit.NAME, 'version': '0.0.0.dev20260827', 'build_number': 1,
            'build': 'research_ab123_1', 'subdir': 'linux-64', 'license': 'LicenseRef-Unreviewed',
            'depends': ['libboost >=1.90,<1.91', 'libopencv >=4.13,<4.14', 'libjxl >=0.11,<0.12',
                        'tbb', 'mpfr', 'gmp', 'libgomp', 'python >=3.12,<3.13']}


def test_package_index_identity_and_jxl_constraint():
    audit.verify_index(good_index())
    for index in (good_index() | {'license': 'AGPL-3.0-only'},
                  good_index() | {'build': 'public_1'},
                  good_index() | {'build_number': 2},
                  good_index() | {'depends': [x for x in good_index()['depends'] if not x.startswith('libjxl')]},
                  good_index() | {'depends': [x.replace('>=0.11,<0.12', '>=0.12') for x in good_index()['depends']]}):
        with pytest.raises(ScaffoldError):
            audit.verify_index(index)


def test_package_payload_and_selected_notices(monkeypatch):
    notices = [b'notice1', b'notice2']
    monkeypatch.setattr(audit, 'NOTICE_HASHES', frozenset(hashlib.sha256(x).hexdigest() for x in notices))
    info = {f'info/licenses/{i}': data for i, data in enumerate(notices)}
    payload = {'bin/ReconstructMesh': b'\x7fELFdummy', audit.SHARE + 'SOURCE.txt':
               b'PRIVATE RESEARCH ONLY: rights and ODM compatibility unreviewed.\n'}
    payload.update({audit.SHARE + name: (ROOT / 'scripts' / name).read_bytes() for name in audit.FIXTURES})
    audit.verify_contents(info, payload)
    for bad in (payload | {'bin/extra': b'x'}, payload | {'bin/ReconstructMesh': b'bad'},
                payload | {audit.SHARE + audit.FIXTURES[0]: b'modified'}):
        with pytest.raises(ScaffoldError):
            audit.verify_contents(info, bad)
    with pytest.raises(ScaffoldError, match='notice'):
        audit.verify_contents({}, payload)
