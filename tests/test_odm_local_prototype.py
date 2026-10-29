"""The experimental ODM adapter must not run with missing prefix tools."""
from pathlib import Path
import pytest


def test_preflight_lists_missing_tools_in_explicit_prefix(tmp_path):
    from odm_local_prototype import PrototypeError, check_prefix

    with pytest.raises(PrototypeError, match='missing.*opensfm'):
        check_prefix(tmp_path)


def test_preflight_rejects_tool_escaping_prefix(tmp_path):
    from odm_local_prototype import PrototypeError, REQUIRED_TOOLS, check_prefix

    bindir = tmp_path / 'bin'
    bindir.mkdir()
    for name in REQUIRED_TOOLS:
        target = bindir / name
        target.write_text('#!/bin/sh\nexit 0\n')
        target.chmod(0o755)
    (bindir / 'opensfm').unlink()
    (bindir / 'opensfm').symlink_to('/bin/true')
    with pytest.raises(PrototypeError, match='outside'):
        check_prefix(tmp_path)


def test_run_rejects_non_fast_and_out_of_scope_before_execution(tmp_path, monkeypatch):
    import odm_local_prototype as prototype

    (tmp_path / 'LOCAL-ONLY.txt').touch()
    (tmp_path / 'run.py').touch()
    monkeypatch.setattr(prototype, 'check_prefix', lambda _: pytest.fail('must not start'))
    with pytest.raises(prototype.PrototypeError, match='fast-orthophoto'):
        prototype.run_local(tmp_path, tmp_path, ['dataset'])
    with pytest.raises(prototype.PrototypeError, match='outside'):
        prototype.run_local(tmp_path, tmp_path, ['--fast-orthophoto', '--pc-classify'])


def test_archive_hash_rejected_before_extract(tmp_path):
    from odm_local_prototype import PrototypeError, prepare

    source = tmp_path / 'wrong.tar.gz'
    source.write_bytes(b'not the ODM archive')
    with pytest.raises(PrototypeError, match='SHA256'):
        prepare(source, tmp_path / 'app')
    assert not (tmp_path / 'app').exists()


def test_tool_paths_relocate_with_prefix(tmp_path):
    from odm_local_prototype import REQUIRED_TOOLS, check_prefix

    prefix = tmp_path / 'one'
    bindir = prefix / 'bin'
    bindir.mkdir(parents=True)
    for name in REQUIRED_TOOLS:
        target = bindir / name
        target.write_text('#!/bin/sh\nexit 0\n')
        target.chmod(0o755)
    check_prefix(prefix)
    moved = tmp_path / 'another prefix'
    prefix.rename(moved)
    check_prefix(moved)
    with pytest.raises(Exception, match='not a directory'):
        check_prefix(prefix)


def test_import_probe_reports_failure(tmp_path, monkeypatch):
    import subprocess
    import odm_local_prototype as prototype

    def fail_probe(command, **kwargs):
        assert command[0] == str(tmp_path / 'bin/python')
        return subprocess.CompletedProcess(command, 1, '', 'missing module')

    monkeypatch.setattr(prototype.subprocess, 'run', fail_probe)
    with pytest.raises(prototype.PrototypeError, match='missing module'):
        prototype.check_imports(tmp_path)


def test_run_invokes_prefix_python_without_ambient_pythonpath(tmp_path, monkeypatch):
    import subprocess
    import odm_local_prototype as prototype

    (tmp_path / 'LOCAL-ONLY.txt').touch()
    (tmp_path / 'run.py').touch()
    monkeypatch.setenv('PYTHONPATH', '/wrong/place')
    monkeypatch.setenv('PROJ_DATA', '/wrong/proj')
    monkeypatch.setenv('PROJ_LIB', '/wrong/proj')
    monkeypatch.setattr(prototype, 'check_prefix', lambda _: None)
    monkeypatch.setattr(prototype, 'check_imports', lambda _: None)

    def run(command, env):
        assert command == [str(tmp_path / 'bin/python'), '-s', '-E', str(tmp_path / 'run.py'),
                           '--fast-orthophoto', 'dataset']
        assert 'PYTHONPATH' not in env
        assert env['ODM_CONDA_LOCAL_PREFIX'] == str(tmp_path)
        assert env['PROJ_DATA'] == str(tmp_path / 'share/proj')
        assert env['PROJ_LIB'] == str(tmp_path / 'share/proj')
        return subprocess.CompletedProcess(command, 17)

    monkeypatch.setattr(prototype.subprocess, 'run', run)
    assert prototype.run_local(tmp_path, tmp_path, ['--fast-orthophoto', 'dataset']) == 17
