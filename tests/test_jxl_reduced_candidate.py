import hashlib
import io
import json
import tarfile

import pytest


def make_source(path, changed=False, extra=False):
    files = {
        'test/images/README.md': b'readme',
        'test/images/a.png': b'image-a',
        'test/images/nested/b.jxl': b'image-b',
        'src/lib.rs': b'fn main() {}',
        'LICENSE': b'license',
    }
    if changed:
        files['test/images/a.png'] = b'changed'
    if extra:
        files['test/images/unknown.jpg'] = b'unknown'
    with tarfile.open(path, 'w:gz') as tar:
        for name, content in files.items():
            item = tarfile.TarInfo('project/'+name)
            item.size = len(content)
            item.mode = 0o644
            tar.addfile(item, io.BytesIO(content))
    return files


def pin(monkeypatch, source):
    import jxl_reduced_candidate as mod
    monkeypatch.setattr(mod, 'SOURCE_SHA256', hashlib.sha256(source.read_bytes()).hexdigest())
    monkeypatch.setattr(mod, 'README_SHA256', hashlib.sha256(b'readme').hexdigest())
    monkeypatch.setattr(mod, 'EXCLUDED', {'a.png': hashlib.sha256(b'image-a').hexdigest(), 'nested/b.jxl': hashlib.sha256(b'image-b').hexdigest()})
    return mod


def test_candidate_is_deterministic_private_and_excludes_only_known_images(tmp_path, monkeypatch):
    source=tmp_path/'source.tar.gz'; make_source(source); mod=pin(monkeypatch, source)
    one=tmp_path/'one.tar.gz'; two=tmp_path/'two.tar.gz'
    manifest=mod.make_candidate(source,one)
    assert mod.make_candidate(source,two) == manifest
    assert one.read_bytes() == two.read_bytes()
    assert one.stat().st_mode & 0o777 == 0o600
    with tarfile.open(one) as tar:
        names=set(tar.getnames())
        assert 'source/test/images/README.md' in names
        assert 'source/src/lib.rs' in names
        assert 'source/test/images/a.png' not in names
        data=json.load(tar.extractfile('source/CANDIDATE-MANIFEST.json'))
        assert len(data['excluded_files']) == 2
        assert data['scope'] == 'local-research-only'
    with pytest.raises(mod.ScaffoldError,match='existing'):
        mod.make_candidate(source,one)


@pytest.mark.parametrize('changed,extra', [(True, False), (False, True)])
def test_candidate_rejects_changed_or_unknown_assets_without_output(tmp_path, monkeypatch, changed, extra):
    source=tmp_path/'source.tar.gz'; make_source(source, changed=changed, extra=extra); mod=pin(monkeypatch,source)
    dest=tmp_path/'result.tar.gz'
    with pytest.raises(mod.ScaffoldError,match='set or digest'):
        mod.make_candidate(source,dest)
    assert not dest.exists()


def test_candidate_rejects_untrusted_archive_and_repo_destination(tmp_path, monkeypatch):
    source=tmp_path/'source.tar.gz'; make_source(source); mod=pin(monkeypatch,source)
    monkeypatch.setattr(mod, 'ROOT', tmp_path)
    with pytest.raises(mod.ScaffoldError,match='destination'):
        mod.make_candidate(source,tmp_path/'result.tar.gz')
    source.write_bytes(b'changed')
    with pytest.raises(mod.ScaffoldError,match='source archive'):
        mod.make_candidate(source,tmp_path/'result.tar.gz')
