from __future__ import annotations

import subprocess

import pytest

from common import ScaffoldError
from release_guard import check_git


def test_release_tag_must_match_clean_head(tmp_path):
    def git(*args):
        subprocess.run(["git", *args], cwd=tmp_path, check=True, capture_output=True)

    git("init", "-b", "main")
    (tmp_path / "tracked").write_text("one")
    git("add", "tracked")
    git("-c", "user.name=Packaging unit test", "-c", "user.email=unit-test@example.invalid", "commit", "-m", "first")
    git("tag", "component-v1-b0")
    check_git("component-v1-b0", tmp_path)
    (tmp_path / "untracked").write_text("not clean")
    with pytest.raises(ScaffoldError, match="clean"):
        check_git("component-v1-b0", tmp_path)
    (tmp_path / "untracked").unlink()
    (tmp_path / "tracked").write_text("two")
    git("add", "tracked")
    git("-c", "user.name=Packaging unit test", "-c", "user.email=unit-test@example.invalid", "commit", "-m", "second")
    with pytest.raises(ScaffoldError, match="exact"):
        check_git("component-v1-b0", tmp_path)
