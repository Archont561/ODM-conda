from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import tomllib
from pathlib import Path

import pytest

from common import ROOT, repository_files


def definition(task: str) -> str:
    tools = tomllib.loads((ROOT / "pixi.toml").read_text())
    return tools["tasks"][task]


def git_environment() -> dict[str, str]:
    env = os.environ.copy()
    for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX", "GIT_COMMON_DIR"):
        env.pop(key, None)
    return env


def git_fixture(root: Path, include_policy: bool = True) -> Path:
    subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=root, env=git_environment(), check=True)
    if include_policy:
        (root / ".config").mkdir()
        shutil.copy2(ROOT / ".config/convco.yml", root / ".config/convco.yml")
    return root


def run_task(task: str, root: Path, message: str | None = None, revisions: tuple[str, ...] = ()) -> subprocess.CompletedProcess[str]:
    # The checked-in task definition is a small POSIX-compatible && expression.
    # Keep range arguments positional/quoted rather than interpolating shell text.
    return subprocess.run(
        ["sh", "-c", definition(task) + ' "$@"', "convco-policy-test", *revisions],
        cwd=root, env=git_environment(), input=message, text=True, capture_output=True,
    )


def test_stdin_and_history_explicitly_share_shipped_policy():
    prefix = ["test", "-f", ".config/convco.yml", "&&", "convco", "check", "--config", ".config/convco.yml"]
    assert shlex.split(definition("commit-lint")) == prefix + ["--from-stdin"]
    assert shlex.split(definition("commits")) == prefix
    files = {path.relative_to(ROOT).as_posix() for path in repository_files()}
    assert ".config/convco.yml" in files
    assert not (ROOT / ".versionrc").exists()
    assert not (ROOT / ".convco").exists()


@pytest.mark.parametrize("message", [
    "feat(packaging): add explicit commit policy",
    "fix(build/linux): preserve the shared scope syntax",
    "chore(deps_py): maintain the locked tooling",
    "ci: verify the complete workflow",
    "feat(packaging)!: change the packaging interface",
])
def test_stdin_accepts_reviewed_types_and_scopes(tmp_path, message):
    root = git_fixture(tmp_path)
    result = run_task("commit-lint", root, message + "\n")
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("message", [
    "custom(packaging): unknown type must not pass",
    "feat(bad scope): do not accept a valid substring",
    "feat(../bad): dotted traversal-like scope is invalid",
    "not a conventional commit message",
])
def test_stdin_rejects_unknown_types_and_partial_bad_scopes(tmp_path, message):
    root = git_fixture(tmp_path)
    result = run_task("commit-lint", root, message + "\n")
    assert result.returncode == 1, result.stdout + result.stderr


@pytest.mark.parametrize("task", ["commit-lint", "commits"])
def test_missing_policy_fails_closed(tmp_path, task):
    root = git_fixture(tmp_path, include_policy=False)
    subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=Policy Test", "-c", "user.email=policy@example.invalid", "commit", "--allow-empty", "--quiet", "-m", "fix: seed a valid disposable policy fixture"],
        cwd=root, env=git_environment(), check=True,
    )
    result = run_task(task, root, "fix: a valid message cannot bypass missing policy\n" if task == "commit-lint" else None)
    assert result.returncode != 0


def test_real_git_ranges_use_the_same_policy(tmp_path):
    root = git_fixture(tmp_path)
    git = ["git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=Policy Test", "-c", "user.email=policy@example.invalid"]

    def invoke(*args: str) -> str:
        return subprocess.check_output(git + list(args), cwd=root, env=git_environment(), text=True).strip()

    invoke("commit", "--allow-empty", "--quiet", "-m", "chore: initialize a disposable history fixture")
    base = invoke("rev-parse", "HEAD")
    invoke("commit", "--allow-empty", "--quiet", "-m", "fix(policy): check a valid scoped history range")
    head = invoke("rev-parse", "HEAD")
    result = run_task("commits", root, revisions=(f"{base}..{head}",))
    assert result.returncode == 0, result.stdout + result.stderr
    invoke("commit", "--allow-empty", "--quiet", "-m", "feat(bad scope): reject this nonconforming history entry")
    head = invoke("rev-parse", "HEAD")
    result = run_task("commits", root, revisions=(f"{base}..{head}",))
    assert result.returncode == 1, result.stdout + result.stderr
