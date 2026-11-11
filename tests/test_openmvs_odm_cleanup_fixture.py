from pathlib import Path
from types import SimpleNamespace

import pytest

from openmvs_odm_cleanup_fixture import check


def test_cleanup_fixture_runs_odm_command_and_checks_output(tmp_path, monkeypatch):
    calls = []
    checked = []

    def run(command, *, cwd, text, capture_output, timeout):
        calls.append(command)
        (cwd / 'mesh.ply').write_text('stub')
        return SimpleNamespace(returncode=0, stdout='', stderr='')

    monkeypatch.setattr('openmvs_odm_cleanup_fixture.subprocess.run', run)
    monkeypatch.setattr('openmvs_odm_cleanup_fixture.validate_mesh', checked.append)
    check(Path('/private/ReconstructMesh'), tmp_path, '20')
    assert calls[0][calls[0].index('--archive-type') + 1] == '3'
    assert calls[0][calls[0].index('--target-face-num') + 1] == '8'
    assert calls[0][calls[0].index('--remove-spurious') + 1] == '20'
    assert checked == [tmp_path / 'mesh.ply']


def test_cleanup_fixture_rejects_failure(tmp_path, monkeypatch):
    monkeypatch.setattr('openmvs_odm_cleanup_fixture.subprocess.run',
                        lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout='', stderr='failed'))
    with pytest.raises(AssertionError, match='ODM cleanup failed'):
        check(Path('/private/ReconstructMesh'), tmp_path, '0')
