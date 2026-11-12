import hashlib
import io
import json
import tarfile
from pathlib import Path

import pytest

import tetraflow_source_receipt as receipt
from common import ScaffoldError


def archive(path, members):
    with tarfile.open(path, 'w:gz') as tar:
        for name, content, kind in members:
            info = tarfile.TarInfo(name)
            if kind == 'symlink':
                info.type = tarfile.SYMTYPE
                info.linkname = 'target'
                tar.addfile(info)
            else:
                info.size = len(content)
                tar.addfile(info, io.BytesIO(content))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(tmp_path, monkeypatch):
    root = tmp_path / 'checkout'; root.mkdir()
    for name in receipt.INPUTS:
        path = root / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(name)
    first = tmp_path / 'one.tgz'; second = tmp_path / 'two.tgz'
    a = archive(first, [('a/LICENSE', b'license', 'file'), ('a/code.cpp', b'code', 'file')])
    b = archive(second, [('b/COPYING', b'text', 'file')])
    monkeypatch.setattr(receipt, 'ARCHIVES', {'openmvs.tar.gz': (a, 'a'), 'eigen.tar.gz': (b, 'b')})
    return root, first, second


def test_stage_verify_and_detect_mutation(tmp_path, monkeypatch):
    root, first, second = inputs(tmp_path, monkeypatch)
    output = tmp_path / 'receipt'
    digest = receipt.stage(first, second, output, root=root)
    report = receipt.verify(output, digest)
    assert report['archives']['openmvs.tar.gz']['file_count'] == 2
    assert report['archives']['openmvs.tar.gz']['notice_name_candidates'] == ['LICENSE']
    assert len(report['receipt_files']) == 2 + len(receipt.INPUTS)
    (output / 'packaging/LICENSE').write_text('changed')
    with pytest.raises(ScaffoldError, match='checksum'):
        receipt.verify(output, digest)
    with pytest.raises(ScaffoldError, match='manifest'):
        receipt.verify(output, '0' * 64)


def test_extra_file_and_symlink_rejected(tmp_path, monkeypatch):
    root, first, second = inputs(tmp_path, monkeypatch)
    output = tmp_path / 'receipt'
    digest = receipt.stage(first, second, output, root=root)
    (output / 'extra').write_text('x')
    with pytest.raises(ScaffoldError, match='Unexpected or missing'):
        receipt.verify(output, digest)
    (output / 'extra').unlink()
    (output / 'link').symlink_to(output / 'receipt.json')
    with pytest.raises(ScaffoldError, match='symlink'):
        receipt.verify(output, digest)


@pytest.mark.parametrize('member', [('../escape', b'x', 'file'), ('a/../escape', b'x', 'file'),
                                    ('a/link', b'', 'symlink')])
def test_reject_unsafe_tar(tmp_path, member):
    path = tmp_path / 'bad.tgz'
    digest = archive(path, [member])
    with pytest.raises(ScaffoldError):
        receipt.inspect_archive(path, digest, 'a')


def test_reject_duplicate_and_restricted_paths(tmp_path, monkeypatch):
    path = tmp_path / 'duplicate.tgz'
    digest = archive(path, [('a/file', b'x', 'file'), ('a/file', b'y', 'file')])
    with pytest.raises(ScaffoldError, match='duplicate'):
        receipt.inspect_archive(path, digest, 'a')
    root, first, second = inputs(tmp_path, monkeypatch)
    digest = archive(first, [('a/libs/Math/IBFS/file', b'x', 'file')])
    monkeypatch.setattr(receipt, 'ARCHIVES', {'openmvs.tar.gz': (digest, 'a'), 'eigen.tar.gz': receipt.ARCHIVES['eigen.tar.gz']})
    with pytest.raises(ScaffoldError, match='Restricted directory'):
        receipt.stage(first, second, tmp_path / 'receipt', root=root)
    assert not (tmp_path / 'receipt').exists()


def test_destination_must_be_new_and_private(tmp_path, monkeypatch):
    root, first, second = inputs(tmp_path, monkeypatch)
    with pytest.raises(ScaffoldError, match='overlap'):
        receipt.stage(first, second, root / 'output', root=root)
    with pytest.raises(ScaffoldError, match='new'):
        receipt.stage(first, second, root, root=root)
    first.write_bytes(b'changed')
    with pytest.raises(ScaffoldError, match='mismatched'):
        receipt.stage(first, second, tmp_path / 'receipt', root=root)


def test_receipt_verifier_does_not_write_bytecode(tmp_path, monkeypatch):
    import shutil
    import subprocess
    import sys
    from common import ROOT

    root, first, second = inputs(tmp_path, monkeypatch)
    # Real copied module code has the production hashes, so test it separately
    # with an invalid manifest: importing common must not create a cache.
    script_dir = tmp_path / 'isolated'; script_dir.mkdir()
    for name in ('tetraflow_source_receipt.py', 'common.py'):
        shutil.copyfile(ROOT / 'scripts' / name, script_dir / name)
    result = subprocess.run([sys.executable, str(script_dir / 'tetraflow_source_receipt.py'),
                             'verify', '--receipt', str(tmp_path / 'missing'), '--manifest-sha256', '0' * 64],
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert not (script_dir / '__pycache__').exists()
