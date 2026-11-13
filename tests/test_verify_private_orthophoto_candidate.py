import hashlib
import io
import json
import tarfile
from pathlib import Path

import pytest
from common import ScaffoldError, sha256
import verify_private_orthophoto_candidate as check


def digest(data):
    return hashlib.sha256(data).hexdigest()


def fixture(tmp_path, monkeypatch):
    root=tmp_path/'handoff'; root.mkdir(); (root/'package').mkdir(); (root/'source').mkdir()
    build='candidate_opencv413_ab12_3'; version='0.0.0.dev20250225'
    package=root/'package'/f'odm-orthophoto-{version}-{build}.conda'; package.write_bytes(b'binary')
    upstream=b'upstream source'
    component={'build_number':3, 'release_checks':{'publishable':False,'license_reviewed':False,'source_completeness_reviewed':False,'native_validation_passed':False}, 'source':{'sha256':digest(upstream)}}
    cfg=json.dumps({'components':{'odm-orthophoto':component}}).encode()
    recipe=b'build:\n  number: 3\n  string: candidate_opencv413_${{ hash }}_3\n  - libopencv >=4.13,<4.14\n  - libopencv >=4.13,<4.14\n'
    contents={'packaging/recipes/components.json':cfg,'packaging/recipes/odm-orthophoto/recipe.yaml':recipe,'upstream/source.tar.gz':upstream}
    manifest={'schema_version':1,'component':'odm-orthophoto','version':version,'build_number':3,'upstream':component['source'],'files':{name:digest(value) for name,value in contents.items()}}
    contents['SOURCE-MANIFEST.json']=json.dumps(manifest).encode(); contents['README-SOURCE.txt']=b'readme'
    archive=root/'source'/'source.tar.gz'
    with tarfile.open(archive,'w:gz') as tar:
        for name,value in contents.items():
            entry=tarfile.TarInfo(name);entry.size=len(value);tar.addfile(entry,io.BytesIO(value))
    receipt={'schema_version':1,'package':{'filename':package.name,'sha256':sha256(package)},'source_bundle':{'filename':archive.name,'sha256':sha256(archive)},'staged_recipe_sha256':digest(recipe),'staged_manifest_sha256':digest(cfg)}
    (root/'receipt.json').write_text(json.dumps(receipt))
    index={'name':'odm-orthophoto','version':version,'build_number':3,'build':build,'depends':['libopencv >=4.13,<4.14']}
    monkeypatch.setattr(check,'read_package',lambda _: ({'info/index.json':json.dumps(index)},{}))
    monkeypatch.setattr(check,'audit',lambda n,c,p,root: {'sha256':sha256(p),'result':'passed'})
    return root,package,index


def test_verify_anchor_package_and_source(tmp_path, monkeypatch):
    root,package,index=fixture(tmp_path,monkeypatch)
    result=check.verify(root,sha256(root/'receipt.json'))
    assert result['result']=='passed' and result['source_manifest_entries']==3
    assert 'not integration' in result['scope']
    with pytest.raises(ScaffoldError,match='Receipt'): check.verify(root,'0'*64)
    package.write_bytes(b'tampered')
    with pytest.raises(ScaffoldError,match='checksum'): check.verify(root,sha256(root/'receipt.json'))


def test_verify_rejects_wrong_abi_or_extra_files(tmp_path, monkeypatch):
    root,package,index=fixture(tmp_path,monkeypatch)
    index['depends']=['libopencv >=4.12,<4.13']
    with pytest.raises(ScaffoldError,match='OpenCV'): check.verify(root,sha256(root/'receipt.json'))
    index['depends']=['libopencv >=4.13,<4.14']
    (root/'source'/'extra').write_text('extra')
    with pytest.raises(ScaffoldError,match='Unexpected files'): check.verify(root,sha256(root/'receipt.json'))
