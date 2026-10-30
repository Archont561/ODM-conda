import json
import pytest
from common import ScaffoldError
from inventory_conda_environment import inventory


def test_inventory_sanitizes_url_and_reports_missing_metadata(tmp_path):
    meta=tmp_path/'conda-meta'; meta.mkdir()
    (meta/'pkg.json').write_text(json.dumps({'name':'pkg','version':'1','build':'0','url':'https://user:secret@example.com/a.conda?token=secret','sha256':'abc','files':['share/licenses/pkg/LICENSE','bin/x']}))
    p=inventory(tmp_path)['packages'][0]
    assert p['binary_package_url']=='https://example.com/a.conda'
    assert p['license'] is None and p['notice_paths']==['share/licenses/pkg/LICENSE']
    (meta/'bad.json').write_text('{}')
    with pytest.raises(ScaffoldError): inventory(tmp_path)


def test_local_package_hash_is_optional_and_refuses_changed_or_missing_files(tmp_path):
    import hashlib
    meta=tmp_path/'conda-meta'; meta.mkdir()
    packages=tmp_path/'packages'; packages.mkdir()
    binary=packages/'pkg-1-0.conda'; binary.write_bytes(b'binary')
    record={'name':'pkg','version':'1','build':'0','url':'file:///private/place/pkg-1-0.conda'}
    path=meta/'pkg.json'; path.write_text(json.dumps(record))
    assert inventory(tmp_path)['packages'][0]['local_binary_sha256'] is None
    item=inventory(tmp_path,packages)['packages'][0]
    assert item['binary_package_url']=='local-file:pkg-1-0.conda'
    assert item['local_binary_sha256']==hashlib.sha256(b'binary').hexdigest()
    record['sha256']='bad'; path.write_text(json.dumps(record))
    with pytest.raises(ScaffoldError,match='digest mismatch'): inventory(tmp_path,packages)
    record.pop('sha256'); path.write_text(json.dumps(record)); binary.unlink()
    with pytest.raises(ScaffoldError,match='Missing or unsafe'): inventory(tmp_path,packages)
    binary.symlink_to(path)
    with pytest.raises(ScaffoldError,match='Missing or unsafe'): inventory(tmp_path,packages)
