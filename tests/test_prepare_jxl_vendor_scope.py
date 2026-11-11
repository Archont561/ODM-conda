import hashlib
import io
import json
import tarfile

import pytest

from common import ScaffoldError
from source_graph import unpack_archive


def fixture(tmp_path, monkeypatch):
    import prepare_jxl_vendor_scope as mod
    content={'Cargo.toml': b'contents', 'LICENSE': b'license', 'libjxl/data': b'data'}
    archive=tmp_path/'original.crate'
    with tarfile.open(archive,'w:gz') as tar:
        for name, data in content.items():
            entry=tarfile.TarInfo('crate/'+name); entry.size=len(data); tar.addfile(entry,io.BytesIO(data))
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    monkeypatch.setattr(mod, 'CRATE_SHA256', digest)
    monkeypatch.setattr(mod, 'REMOVED_COUNT', 1)
    monkeypatch.setattr(mod, 'RETAINED_COUNT', 2)
    tree=tmp_path/'prepared'; vendor=tree/'source/vendor'/mod.CRATE; vendor.mkdir(parents=True)
    hashes={name:hashlib.sha256(data).hexdigest() for name,data in content.items()}
    for name, data in content.items():
        path=vendor/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(data)
    (vendor/'.cargo-checksum.json').write_text(json.dumps({'files':hashes,'package':digest}))
    recipe=tree/'recipe/recipe.yaml'; recipe.parent.mkdir()
    recipe.write_text('source:\n  path: '+json.dumps(str((tree/'source').resolve()))+'\nbuild:\n  number: 2\n  string: research_reduced_${{ hash }}_2\n')
    return mod, archive, tree, vendor


def test_scope_transform_is_deterministic_and_archives_portably(tmp_path, monkeypatch):
    mod, crate, tree, _=fixture(tmp_path,monkeypatch)
    a=tmp_path/'a'; b=tmp_path/'b'
    first=mod.prepare(tree,crate,a); second=mod.prepare(tree,crate,b)
    assert first==second and set(first['removed'])=={'libjxl/data'}
    assert (a/'source/vendor'/mod.CRATE/'LICENSE').read_bytes()==b'license'
    assert not (a/'source/vendor'/mod.CRATE/'libjxl').exists()
    assert 'path: ../source' in (a/'recipe/recipe.yaml').read_text()
    assert 'research_vendor_scope_${{ hash }}_3' in (a/'recipe/recipe.yaml').read_text()
    one=tmp_path/'one.tar.gz'; two=tmp_path/'two.tar.gz'
    mod.archive(a,one); mod.archive(b,two)
    assert one.read_bytes()==two.read_bytes()
    extracted=tmp_path/'received'; extracted.mkdir(); unpack_archive(one,extracted)
    assert json.loads((extracted/'VENDOR-SCOPE-MANIFEST.json').read_text())==first
    with pytest.raises(ScaffoldError,match='existing'):
        mod.archive(a,one)


@pytest.mark.parametrize('change', ['crate', 'file', 'metadata', 'extra', 'link', 'recipe'])
def test_rejects_modified_inputs_without_leaving_destination(tmp_path, monkeypatch, change):
    mod, crate, tree, vendor=fixture(tmp_path,monkeypatch)
    if change=='crate': crate.write_bytes(b'wrong')
    if change=='file': (vendor/'LICENSE').write_text('modified')
    if change=='metadata': (vendor/'.cargo-checksum.json').write_text('{"files":{},"package":"wrong"}')
    if change=='extra': (vendor/'unexpected').write_text('unexpected')
    if change=='link': (vendor/'link').symlink_to('LICENSE')
    if change=='recipe': (tree/'recipe/recipe.yaml').write_text('unexpected')
    target=tmp_path/'result'
    with pytest.raises(ScaffoldError): mod.prepare(tree,crate,target)
    assert not target.exists()
