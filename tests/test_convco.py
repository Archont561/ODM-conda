from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from common import ROOT, repository_files


class ConvcoTests(unittest.TestCase):
    def definition(self, task: str) -> str:
        tools = tomllib.loads((ROOT / "pixi.toml").read_text())
        return tools["tasks"][task]

    def git_environment(self) -> dict[str, str]:
        env = os.environ.copy()
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_PREFIX", "GIT_COMMON_DIR"):
            env.pop(key, None)
        return env

    def git_fixture(self, include_policy: bool = True) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=root, env=self.git_environment(), check=True)
        if include_policy:
            (root / ".config").mkdir()
            shutil.copy2(ROOT / ".config/convco.yml", root / ".config/convco.yml")
        return root

    def run_task(self, task: str, root: Path, message: str | None = None, revisions: tuple[str, ...] = ()) -> subprocess.CompletedProcess[str]:
        # The checked-in task definition is a small POSIX-compatible && expression.
        # Keep range arguments positional/quoted rather than interpolating shell text.
        return subprocess.run(
            ["sh", "-c", self.definition(task) + ' "$@"', "convco-policy-test", *revisions],
            cwd=root, env=self.git_environment(), input=message, text=True, capture_output=True,
        )

    def test_stdin_and_history_explicitly_share_shipped_policy(self):
        prefix = ["test", "-f", ".config/convco.yml", "&&", "convco", "check", "--config", ".config/convco.yml"]
        self.assertEqual(shlex.split(self.definition("commit-lint")), prefix + ["--from-stdin"])
        self.assertEqual(shlex.split(self.definition("commits")), prefix)
        files = {path.relative_to(ROOT).as_posix() for path in repository_files()}
        self.assertIn(".config/convco.yml", files)
        self.assertFalse((ROOT / ".versionrc").exists())
        self.assertFalse((ROOT / ".convco").exists())

    def test_stdin_accepts_reviewed_types_and_scopes(self):
        root = self.git_fixture()
        messages = (
            "feat(packaging): add explicit commit policy",
            "fix(build/linux): preserve the shared scope syntax",
            "chore(deps_py): maintain the locked tooling",
            "ci: verify the complete workflow",
            "feat(packaging)!: change the packaging interface",
        )
        for message in messages:
            with self.subTest(message=message):
                result = self.run_task("commit-lint", root, message + "\n")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_stdin_rejects_unknown_types_and_partial_bad_scopes(self):
        root = self.git_fixture()
        messages = (
            "custom(packaging): unknown type must not pass",
            "feat(bad scope): do not accept a valid substring",
            "feat(../bad): dotted traversal-like scope is invalid",
            "not a conventional commit message",
        )
        for message in messages:
            with self.subTest(message=message):
                result = self.run_task("commit-lint", root, message + "\n")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_missing_policy_fails_closed(self):
        root = self.git_fixture(include_policy=False)
        subprocess.run(
            ["git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=Policy Test", "-c", "user.email=policy@example.invalid", "commit", "--allow-empty", "--quiet", "-m", "fix: seed a valid disposable policy fixture"],
            cwd=root, env=self.git_environment(), check=True,
        )
        for task in ("commit-lint", "commits"):
            with self.subTest(task=task):
                result = self.run_task(task, root, "fix: a valid message cannot bypass missing policy\n" if task == "commit-lint" else None)
                self.assertNotEqual(result.returncode, 0)

    def test_real_git_ranges_use_the_same_policy(self):
        root = self.git_fixture()
        git = ["git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=Policy Test", "-c", "user.email=policy@example.invalid"]

        def invoke(*args: str) -> str:
            return subprocess.check_output(git + list(args), cwd=root, env=self.git_environment(), text=True).strip()

        invoke("commit", "--allow-empty", "--quiet", "-m", "chore: initialize a disposable history fixture")
        base = invoke("rev-parse", "HEAD")
        invoke("commit", "--allow-empty", "--quiet", "-m", "fix(policy): check a valid scoped history range")
        head = invoke("rev-parse", "HEAD")
        result = self.run_task("commits", root, revisions=(f"{base}..{head}",))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        invoke("commit", "--allow-empty", "--quiet", "-m", "feat(bad scope): reject this nonconforming history entry")
        head = invoke("rev-parse", "HEAD")
        result = self.run_task("commits", root, revisions=(f"{base}..{head}",))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
