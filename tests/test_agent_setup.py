from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_agents import check_agent_setup, frontmatter
from common import ROOT, ScaffoldError, config, repository_files
from lint import check_hook_policy, check_workflow_policy
from lint_python import check_python


class AgentSetupTests(unittest.TestCase):
    def fixture(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        for name in ("AGENTS.md", "README.md", "LICENSE", "pixi.toml", "pixi.lock", ".gitignore", "package.json", "bun.lock", "skills-lock.json"):
            shutil.copy2(ROOT / name, root / name)
        for name in ("backlog", ".agents", ".github", "recipes", ".config"):
            shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns(".cache", "node_modules", "__pycache__"))
        return root

    def set_task_dependencies(self, root: Path, number: int, dependencies: list[str]) -> None:
        path = next((root / "backlog" / "tasks").glob(f"task-{number} - *.md"))
        metadata, body = frontmatter(path)
        metadata["dependencies"] = dependencies
        path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---" + body)

    def test_repository_has_cli_owned_backlog_and_pinned_skills(self):
        counts = check_agent_setup()
        self.assertGreaterEqual(counts["tasks"], 16)
        self.assertEqual(counts["managed_skills"], 3)
        self.assertEqual(counts["local_skills"], 4)

    def test_missing_task_dependencies_are_rejected(self):
        root = self.fixture()
        self.set_task_dependencies(root, 1, ["TASK-9999"])
        with self.assertRaisesRegex(ScaffoldError, "Unknown dependency"):
            check_agent_setup(root)

    def test_unknown_milestone_references_are_rejected(self):
        root = self.fixture()
        path = next((root / "backlog/tasks").glob("task-1 - *.md"))
        metadata, body = frontmatter(path)
        metadata["milestone"] = "m-missing"
        path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---" + body)
        with self.assertRaisesRegex(ScaffoldError, "Unknown milestone"):
            check_agent_setup(root)

    def test_sprints_require_concrete_work_dependencies(self):
        root = self.fixture()
        path = next(path for path in (root / "backlog/tasks").glob("*.md") if "sprint" in frontmatter(path)[0].get("labels", []))
        metadata, body = frontmatter(path)
        metadata["dependencies"] = []
        path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---" + body)
        with self.assertRaisesRegex(ScaffoldError, "concrete work dependencies"):
            check_agent_setup(root)

    def test_completed_sprints_cannot_hide_unfinished_dependencies(self):
        root = self.fixture()
        path = next(path for path in (root / "backlog/tasks").glob("*.md") if "sprint" in frontmatter(path)[0].get("labels", []))
        metadata, body = frontmatter(path)
        metadata["status"] = "Done"
        path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---" + body)
        dependency = metadata["dependencies"][0]
        dependency_path = next(path for path in (root / "backlog/tasks").glob("*.md") if frontmatter(path)[0]["id"] == dependency)
        metadata, body = frontmatter(dependency_path)
        metadata["status"] = "To Do"
        dependency_path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---" + body)
        with self.assertRaisesRegex(ScaffoldError, "unfinished dependencies"):
            check_agent_setup(root)

    def test_package_milestones_are_source_with_one_sprint_each(self):
        counts = check_agent_setup()
        self.assertGreaterEqual(counts["milestones"], 13)
        self.assertEqual(counts["sprints"], counts["milestones"])
        files = {path.relative_to(ROOT).as_posix() for path in repository_files()}
        milestones = list((ROOT / "backlog/milestones").glob("*.md"))
        self.assertGreaterEqual(len(milestones), 13)
        for path in milestones:
            self.assertIn(path.relative_to(ROOT).as_posix(), files)

    def test_cyclic_task_dependencies_are_rejected(self):
        root = self.fixture()
        self.set_task_dependencies(root, 1, ["TASK-2"])
        self.set_task_dependencies(root, 2, ["TASK-1"])
        with self.assertRaisesRegex(ScaffoldError, "cycle"):
            check_agent_setup(root)

    def test_automatic_remote_task_operations_are_opt_in(self):
        root = self.fixture()
        path = root / "backlog/config.yml"
        data = yaml.safe_load(path.read_text())
        data["remote_operations"] = True
        path.write_text(yaml.safe_dump(data))
        with self.assertRaisesRegex(ScaffoldError, "remote_operations"):
            check_agent_setup(root)

    def test_parallel_json_roadmap_is_rejected(self):
        root = self.fixture()
        path = root / "recipes" / "components.json"
        data = json.loads(path.read_text())
        data["roadmap"] = []
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ScaffoldError, "Use Backlog"):
            check_agent_setup(root)

    def test_managed_skill_refs_cannot_float(self):
        root = self.fixture()
        path = root / "skills-lock.json"
        data = json.loads(path.read_text())
        data["skills"]["refactor"]["ref"] = "main"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ScaffoldError, "not immutable"):
            check_agent_setup(root)

    def test_managed_source_license_is_required(self):
        root = self.fixture()
        (root / ".agents/licenses/github-awesome-copilot-MIT.txt").unlink()
        with self.assertRaisesRegex(ScaffoldError, "notice"):
            check_agent_setup(root)

    def test_backlog_and_skills_are_source_but_dependencies_are_not(self):
        root = self.fixture()
        for name in ("backlog/.cache/state", ".agents/node_modules/tool/index.js", "backlog/.env.secret", "backlog/local.yml", ".agents/__pycache__/cache.pyc"):
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("not maintained source")
        files = {path.relative_to(root).as_posix() for path in repository_files(root)}
        self.assertIn("AGENTS.md", files)
        self.assertIn("bun.lock", files)
        self.assertIn("skills-lock.json", files)
        self.assertIn(".agents/skills/tdd/SKILL.md", files)
        self.assertIn("backlog/config.yml", files)
        self.assertTrue(any(path.startswith("backlog/tasks/") for path in files))
        self.assertFalse(any("node_modules" in path or "__pycache__" in path or ".cache/" in path or ".env.secret" in path or path == "backlog/local.yml" for path in files))

    def test_movable_configuration_is_required_source_in_subfolders(self):
        files = {path.relative_to(ROOT).as_posix() for path in repository_files()}
        relocated = {
            "components.json": "recipes/components.json",
            "lefthook.yml": ".config/lefthook.yml",
            "CONTRIBUTING.md": ".github/CONTRIBUTING.md",
        }
        for old, new in relocated.items():
            self.assertIn(new, files)
            self.assertNotIn(old, files)
            self.assertFalse((ROOT / old).exists())
        root = self.fixture()
        (root / ".config" / "lefthook-local.yml").write_text("pre-commit: {}\n")
        files = {path.relative_to(root).as_posix() for path in repository_files(root)}
        self.assertNotIn(".config/lefthook-local.yml", files)
        (root / "recipes" / "components.json").unlink()
        with self.assertRaises(FileNotFoundError):
            config(root)
        with self.assertRaisesRegex(ScaffoldError, "recipes/components.json"):
            repository_files(root)

    def test_shared_variants_are_recipe_source_without_root_inventory(self):
        files = {path.relative_to(ROOT).as_posix() for path in repository_files()}
        self.assertIn("recipes/variants.yaml", files)
        self.assertNotIn("variants.yaml", files)
        self.assertNotIn("THIRD_PARTY.md", files)
        self.assertFalse((ROOT / "variants.yaml").exists())
        self.assertFalse((ROOT / "THIRD_PARTY.md").exists())
        root = self.fixture()
        (root / "recipes" / "variants.yaml").unlink()
        with self.assertRaisesRegex(ScaffoldError, "recipes/variants.yaml"):
            repository_files(root)

    def test_legacy_manual_docs_are_not_packaging_source(self):
        root = self.fixture()
        legacy = root / "docs" / "obsolete.md"
        legacy.parent.mkdir()
        legacy.write_text("An obsolete parallel manual document")
        files = {path.relative_to(root).as_posix() for path in repository_files(root)}
        self.assertNotIn("docs/obsolete.md", files)
        self.assertTrue(any(path.startswith("backlog/docs/") for path in files))

    def test_generated_archives_are_not_packaging_source(self):
        root = self.fixture()
        exports = {
            "backlog/exports/scaffold.zip", "backlog/exports/tool.conda",
            "backlog/exports/source.tar.gz", "backlog/exports/source.tar.bz2",
        }
        for name in exports:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b"generated artifact")
        files = {path.relative_to(root).as_posix() for path in repository_files(root)}
        self.assertTrue(exports.isdisjoint(files), exports & files)

    def test_git_ignores_exports_without_hiding_backlog_or_locks(self):
        root = self.fixture()
        subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=root, check=True)
        ignored = {
            "scaffold.zip", "docs/obsolete.md", "output/linux-64/tool.conda",
            "reports/audit-tool.json", "source-bundles/source-tool.tar.gz",
            "release-artifacts/SHA256SUMS", "artifacts/audit.json",
            ".odm-scaffold-research/note.txt", ".pixi/envs/default/state",
            "node_modules/tool/index.js", ".cache/local-state", ".config/lefthook-local.yml",
        }
        maintained = {
            "backlog/config.yml", "backlog/docs/guides/guide.md",
            "backlog/tasks/task-example.md", ".agents/skills/session/SKILL.md",
            "LICENSE", "README.md", "pixi.lock", "bun.lock", "skills-lock.json",
            "package.json", "recipes/tool/recipe.yaml", "recipes/variants.yaml",
            "recipes/components.json", ".config/lefthook.yml", ".config/convco.yml", ".github/CONTRIBUTING.md",
            "backlog/milestones/m-0 - dem2points.md",
        }
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "--stdin"], cwd=root,
            input="\n".join(sorted(ignored | maintained)) + "\n",
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(set(result.stdout.splitlines()), ignored)

    def test_required_source_cannot_be_an_escaping_symlink(self):
        root = self.fixture()
        (root / "LICENSE").unlink()
        (root / "LICENSE").symlink_to(ROOT / "LICENSE")
        with self.assertRaisesRegex(ScaffoldError, "symlink"):
            repository_files(root)

    def test_lefthook_auto_discovers_nested_config_without_an_override(self):
        root = self.fixture()
        self.assertFalse((root / "lefthook.yml").exists())
        subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=root, check=True)
        binary = shutil.which("lefthook")
        self.assertIsNotNone(binary, "Run unit tests through the locked Pixi environment")
        env = os.environ.copy()
        env.pop("LEFTHOOK_CONFIG", None)
        env.pop("LEFTHOOK", None)
        result = subprocess.run(
            [binary, "dump"], cwd=root, env=env, check=True,
            capture_output=True, text=True,
        )
        hooks = yaml.safe_load(result.stdout)
        self.assertTrue({"pre-commit", "commit-msg", "pre-push"} <= set(hooks))
        self.assertEqual(hooks["commit-msg"]["jobs"][0]["run"], "pixi run commit-lint < {1}")

    def test_pre_push_cannot_be_filtered_by_changed_files(self):
        root = self.fixture()
        path = root / ".config" / "lefthook.yml"
        hooks = yaml.safe_load(path.read_text())
        hooks["pre-push"]["jobs"][0]["glob"] = "*.py"
        path.write_text(yaml.safe_dump(hooks))
        with self.assertRaisesRegex(ScaffoldError, "filter"):
            check_hook_policy(root)

    def test_main_ci_runs_must_not_cancel_different_commits(self):
        root = self.fixture()
        path = root / ".github/workflows/ci.yml"
        data = yaml.safe_load(path.read_text())
        data["concurrency"]["group"] = "checks-${{ github.ref }}"
        path.write_text(yaml.safe_dump(data))
        with self.assertRaisesRegex(ScaffoldError, "SHA-distinct"):
            check_workflow_policy(root)

    def test_project_shell_cannot_replace_thin_uncredentialed_steps(self):
        root = self.fixture()
        path = root / ".github/workflows/build.yml"
        data = yaml.safe_load(path.read_text())
        data["jobs"]["build"]["steps"].append({"run": "python scripts/build.py\necho done"})
        path.write_text(yaml.safe_dump(data))
        with self.assertRaisesRegex(ScaffoldError, "one-line Pixi"):
            check_workflow_policy(root)

    def test_python_syntax_check_reports_bad_staged_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "bad.py").write_text("def broken(:\n")
            with self.assertRaisesRegex(ScaffoldError, "Python syntax"):
                check_python(["bad.py"], root)

    def test_python_syntax_check_handles_deleted_staged_files(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(check_python(["deleted.py"], Path(directory)), 0)


if __name__ == "__main__":
    unittest.main()
