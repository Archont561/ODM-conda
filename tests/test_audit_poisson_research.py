import json
import pytest
from common import ScaffoldError


def test_research_provenance_is_verified_without_changing_production(monkeypatch):
    import audit_poisson_research as audit
    digest = '1' * 64
    component = {'version': '13.8', 'build_number': 3, 'license': 'x', 'executable': 'PoissonRecon', 'notices': []}
    monkeypatch.setattr(audit, 'config', lambda: {'components': {audit.NAME: component}})
    info = {'info/index.json': json.dumps({'name': audit.NAME, 'version': '13.8', 'build_number': 3, 'subdir': 'linux-64', 'depends': ['__glibc', 'libgcc', 'libstdcxx', 'libpng', 'libjpeg-turbo', 'libzlib', 'libgomp']}).encode(), 'info/about.json': b'{"license":"x"}', 'info/licenses/IJG-6b-README.txt': b'mock'}
    payload = {'bin/PoissonRecon': b'elf', audit.PREFIX+'SOURCE.txt': ('LOCAL RESEARCH ONLY ' + digest + ' ' + audit.PINNED_SHA256 + ' original not included No corresponding-source offer').encode(), audit.PREFIX+'upstream.json': json.dumps({'scope':'local-research-only','candidate_sha256':digest,'original_archive_sha256':audit.PINNED_SHA256,'excluded_file_count':59,'warning':'No complete corresponding-source offer or license clearance. The original archive was fetched but is not included.'}).encode(), audit.PREFIX+'functional_test.py': b'', audit.PREFIX+'link-evidence.json':b'', 'share/licenses/poissonrecon-odm/packaging-MIT.txt':b'', 'share/licenses/poissonrecon-odm/IJG-6b-README.txt':b'mock'}
    # Avoid inventing a matching IJG fixture: isolate the exact notice digest in this unit test.
    import hashlib
    real = hashlib.sha256
    class Result:
        def hexdigest(self): return '4cf9c190f184019b61c36bcc49d4a24ffeb2a838c6f1690d6c4db14cfb2d0478'
    monkeypatch.setattr(audit.hashlib, 'sha256', lambda data: Result() if data == b'mock' else real(data))
    audit.verify_metadata(info, payload, digest)
    with pytest.raises(ScaffoldError, match='provenance'):
        audit.verify_metadata(info, payload, '2'*64)
    payload['etc/passwd'] = b''
    with pytest.raises(ScaffoldError, match='Unexpected'):
        audit.verify_metadata(info, payload, digest)
