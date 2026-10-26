from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from common import ScaffoldError
from release_guard import check_git


class GitGuardTests(unittest.TestCase):
    def test_release_tag_must_match_clean_head(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def git(*args):
                subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)

            git("init", "-b", "main")
            (root / "tracked").write_text("one")
            git("add", "tracked")
            git("-c", "user.name=Packaging unit test", "-c", "user.email=unit-test@example.invalid", "commit", "-m", "first")
            git("tag", "component-v1-b0")
            check_git("component-v1-b0", root)
            (root / "untracked").write_text("not clean")
            with self.assertRaisesRegex(ScaffoldError, "clean"):
                check_git("component-v1-b0", root)
            (root / "untracked").unlink()
            (root / "tracked").write_text("two")
            git("add", "tracked")
            git("-c", "user.name=Packaging unit test", "-c", "user.email=unit-test@example.invalid", "commit", "-m", "second")
            with self.assertRaisesRegex(ScaffoldError, "exact"):
                check_git("component-v1-b0", root)


if __name__ == "__main__":
    unittest.main()
