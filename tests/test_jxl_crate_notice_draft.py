import hashlib
import json

import pytest

from common import ScaffoldError


def fixture(tmp_path, monkeypatch):
    import jxl_crate_notice_draft as mod
    vendor=tmp_path/'vendor'; crate=vendor/'example-1.0'; (crate/'nested').mkdir(parents=True)
    (crate/'LICENSE').write_bytes(b'root notice'); (crate/'nested/LICENSE').write_bytes(b'nested notice')
    digest=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    (crate/'.cargo-checksum.json').write_text(json.dumps({'package':'a'*64,'files':{}}))
    inventory=tmp_path/'inventory.json'; inventory.write_text(json.dumps({'crates':[{'name':'example','version':'1.0','sha256':'a'*64,'notice_sha256':{'LICENSE':digest(crate/'LICENSE')}}]}))
    monkeypatch.setattr(mod,'INVENTORY',inventory); monkeypatch.setattr(mod,'INVENTORY_SHA256',digest(inventory)); monkeypatch.setattr(mod,'COUNT',1)
    monkeypatch.setattr(mod,'NESTED',{'example-1.0/nested/LICENSE':digest(crate/'nested/LICENSE')})
    return mod,vendor,crate


def test_private_notice_draft_is_pinned_and_repeatable(tmp_path,monkeypatch):
    mod,vendor,crate=fixture(tmp_path,monkeypatch)
    one=tmp_path/'one'; two=tmp_path/'two'
    result=mod.stage(vendor,one); assert result==mod.stage(vendor,two)
    assert (one/'example-1.0/LICENSE').read_bytes()==b'root notice'
    assert len(result['files'])==2 and (one/'MANIFEST.json').read_bytes()==(two/'MANIFEST.json').read_bytes()
    with pytest.raises(ScaffoldError,match='Unsafe'): mod.stage(vendor,one)


@pytest.mark.parametrize('change',['missing','tamper','checksum','extra','symlink'])
def test_draft_rejects_unsafe_or_modified_inputs(tmp_path,monkeypatch,change):
    mod,vendor,crate=fixture(tmp_path,monkeypatch)
    if change=='missing': (crate/'LICENSE').unlink()
    if change=='tamper': (crate/'nested/LICENSE').write_bytes(b'changed')
    if change=='checksum': (crate/'.cargo-checksum.json').write_text('{"package":"wrong"}')
    if change=='extra': (vendor/'extra').mkdir()
    if change=='symlink':
        path=crate/'nested/LICENSE'; path.unlink(); path.symlink_to(crate/'LICENSE')
    dest=tmp_path/'out'
    with pytest.raises(ScaffoldError): mod.stage(vendor,dest)
    assert not dest.exists()
