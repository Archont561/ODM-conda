from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from check_agents import check_agent_setup, frontmatter
from common import ROOT, ScaffoldError, config, repository_files
from lint import check_hook_policy, check_workflow_policy
from lint_python import check_python


@pytest.fixture()
def repo_copy(tmp_path) -> Path:
    """A writable full copy of the repository for destructive agent-setup tests."""
    root = tmp_path / "checkout"
    root.mkdir()
    for name in ("AGENTS.md", "README.md", "LICENSE", "pixi.toml", "pixi.lock", "pixi-sandbox.toml", "restore.sh", ".gitattributes", ".gitignore", "package.json", "bun.lock", "skills-lock.json"):
        shutil.copy2(ROOT / name, root / name)
    for name in ("backlog", ".agents", ".github", "recipes", ".config"):
        shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns(".cache", "node_modules", "__pycache__"))
    return root


def set_task_dependencies(root: Path, number: int, dependencies: list[str]) -> None:
    path = next((root / "backlog" / "tasks").glob(f"task-{number} - *.md"))
    metadata, body = frontmatter(path)
    metadata["dependencies"] = dependencies
    path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---" + body)


def rewrite_frontmatter(path: Path, **changes) -> dict:
    metadata, body = frontmatter(path)
    metadata.update(changes)
    path.write_text("---\n" + yaml.safe_dump(metadata, sort_keys=False) + "---" + body)
    return metadata


def sprint_task(root: Path) -> Path:
    return next(path for path in (root / "backlog/tasks").glob("*.md") if "sprint" in frontmatter(path)[0].get("labels", []))


def test_repository_has_cli_owned_backlog_and_pinned_skills():
    counts = check_agent_setup()
    assert counts["tasks"] >= 16
    assert counts["managed_skills"] == 3
    assert counts["local_skills"] == 4


def test_missing_task_dependencies_are_rejected(repo_copy):
    set_task_dependencies(repo_copy, 1, ["TASK-9999"])
    with pytest.raises(ScaffoldError, match="Unknown dependency"):
        check_agent_setup(repo_copy)


def test_unknown_milestone_references_are_rejected(repo_copy):
    path = next((repo_copy / "backlog/tasks").glob("task-1 - *.md"))
    rewrite_frontmatter(path, milestone="m-missing")
    with pytest.raises(ScaffoldError, match="Unknown milestone"):
        check_agent_setup(repo_copy)


def test_sprints_require_concrete_work_dependencies(repo_copy):
    rewrite_frontmatter(sprint_task(repo_copy), dependencies=[])
    with pytest.raises(ScaffoldError, match="concrete work dependencies"):
        check_agent_setup(repo_copy)


def test_completed_sprints_cannot_hide_unfinished_dependencies(repo_copy):
    metadata = rewrite_frontmatter(sprint_task(repo_copy), status="Done")
    dependency = metadata["dependencies"][0]
    dependency_path = next(path for path in (repo_copy / "backlog/tasks").glob("*.md") if frontmatter(path)[0]["id"] == dependency)
    rewrite_frontmatter(dependency_path, status="To Do")
    with pytest.raises(ScaffoldError, match="unfinished dependencies"):
        check_agent_setup(repo_copy)


def test_package_milestones_are_source_with_one_sprint_each():
    counts = check_agent_setup()
    assert counts["milestones"] >= 13
    assert counts["sprints"] == counts["milestones"]
    files = {path.relative_to(ROOT).as_posix() for path in repository_files()}
    milestones = list((ROOT / "backlog/milestones").glob("*.md"))
    assert len(milestones) >= 13
    for path in milestones:
        assert path.relative_to(ROOT).as_posix() in files


def test_cyclic_task_dependencies_are_rejected(repo_copy):
    set_task_dependencies(repo_copy, 1, ["TASK-2"])
    set_task_dependencies(repo_copy, 2, ["TASK-1"])
    with pytest.raises(ScaffoldError, match="cycle"):
        check_agent_setup(repo_copy)


def test_automatic_remote_task_operations_are_opt_in(repo_copy):
    path = repo_copy / "backlog/config.yml"
    data = yaml.safe_load(path.read_text())
    data["remote_operations"] = True
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ScaffoldError, match="remote_operations"):
        check_agent_setup(repo_copy)


def test_parallel_json_roadmap_is_rejected(repo_copy):
    path = repo_copy / "recipes" / "components.json"
    data = json.loads(path.read_text())
    data["roadmap"] = []
    path.write_text(json.dumps(data))
    with pytest.raises(ScaffoldError, match="Use Backlog"):
        check_agent_setup(repo_copy)


def test_managed_skill_refs_cannot_float(repo_copy):
    path = repo_copy / "skills-lock.json"
    data = json.loads(path.read_text())
    data["skills"]["refactor"]["ref"] = "main"
    path.write_text(json.dumps(data))
    with pytest.raises(ScaffoldError, match="not immutable"):
        check_agent_setup(repo_copy)


def test_managed_source_license_is_required(repo_copy):
    (repo_copy / ".agents/licenses/github-awesome-copilot-MIT.txt").unlink()
    with pytest.raises(ScaffoldError, match="notice"):
        check_agent_setup(repo_copy)


def test_backlog_and_skills_are_source_but_dependencies_are_not(repo_copy):
    for name in ("backlog/.cache/state", ".agents/node_modules/tool/index.js", "backlog/.env.secret", "backlog/local.yml", ".agents/__pycache__/cache.pyc"):
        path = repo_copy / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("not maintained source")
    files = {path.relative_to(repo_copy).as_posix() for path in repository_files(repo_copy)}
    assert "AGENTS.md" in files
    assert "bun.lock" in files
    assert "skills-lock.json" in files
    assert "pixi-sandbox.toml" in files
    assert "restore.sh" in files
    assert ".gitattributes" in files
    assert ".agents/skills/tdd/SKILL.md" in files
    assert "backlog/config.yml" in files
    assert any(path.startswith("backlog/tasks/") for path in files)
    assert not any("node_modules" in path or "__pycache__" in path or ".cache/" in path or ".env.secret" in path or path == "backlog/local.yml" for path in files)


def test_movable_configuration_is_required_source_in_subfolders(repo_copy):
    files = {path.relative_to(ROOT).as_posix() for path in repository_files()}
    relocated = {
        "components.json": "recipes/components.json",
        "lefthook.yml": ".config/lefthook.yml",
        "CONTRIBUTING.md": ".github/CONTRIBUTING.md",
    }
    for old, new in relocated.items():
        assert new in files
        assert old not in files
        assert not (ROOT / old).exists()
    (repo_copy / ".config" / "lefthook-local.yml").write_text("pre-commit: {}\n")
    files = {path.relative_to(repo_copy).as_posix() for path in repository_files(repo_copy)}
    assert ".config/lefthook-local.yml" not in files
    (repo_copy / "recipes" / "components.json").unlink()
    with pytest.raises(FileNotFoundError):
        config(repo_copy)
    with pytest.raises(ScaffoldError, match="recipes/components.json"):
        repository_files(repo_copy)


def test_shared_variants_are_recipe_source_without_root_inventory(repo_copy):
    files = {path.relative_to(ROOT).as_posix() for path in repository_files()}
    assert "recipes/variants.yaml" in files
    assert "variants.yaml" not in files
    assert "THIRD_PARTY.md" not in files
    assert not (ROOT / "variants.yaml").exists()
    assert not (ROOT / "THIRD_PARTY.md").exists()
    (repo_copy / "recipes" / "variants.yaml").unlink()
    with pytest.raises(ScaffoldError, match="recipes/variants.yaml"):
        repository_files(repo_copy)


def test_legacy_manual_docs_are_not_packaging_source(repo_copy):
    legacy = repo_copy / "docs" / "obsolete.md"
    legacy.parent.mkdir()
    legacy.write_text("An obsolete parallel manual document")
    files = {path.relative_to(repo_copy).as_posix() for path in repository_files(repo_copy)}
    assert "docs/obsolete.md" not in files
    assert any(path.startswith("backlog/docs/") for path in files)


def test_generated_archives_are_not_packaging_source(repo_copy):
    exports = {
        "backlog/exports/scaffold.zip", "backlog/exports/tool.conda",
        "backlog/exports/source.tar.gz", "backlog/exports/source.tar.bz2",
    }
    for name in exports:
        path = repo_copy / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"generated artifact")
    files = {path.relative_to(repo_copy).as_posix() for path in repository_files(repo_copy)}
    assert exports.isdisjoint(files), exports & files


def test_git_ignores_exports_without_hiding_backlog_or_locks(repo_copy):
    subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=repo_copy, check=True)
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
        "package.json", "recipes/tool/recipe.yaml", "recipes/variants.yaml", ".pixi/config.toml",
        "recipes/components.json", ".config/lefthook.yml", ".config/convco.yml", ".github/CONTRIBUTING.md",
        "backlog/milestones/m-0 - dem2points.md",
    }
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "--stdin"], cwd=repo_copy,
        input="\n".join(sorted(ignored | maintained)) + "\n",
        capture_output=True, text=True, check=True,
    )
    assert set(result.stdout.splitlines()) == ignored


def test_required_source_cannot_be_an_escaping_symlink(repo_copy):
    (repo_copy / "LICENSE").unlink()
    (repo_copy / "LICENSE").symlink_to(ROOT / "LICENSE")
    with pytest.raises(ScaffoldError, match="symlink"):
        repository_files(repo_copy)


def test_lefthook_auto_discovers_nested_config_without_an_override(repo_copy):
    assert not (repo_copy / "lefthook.yml").exists()
    subprocess.run(["git", "init", "--quiet", "-b", "main"], cwd=repo_copy, check=True)
    binary = shutil.which("lefthook")
    assert binary is not None, "Run unit tests through the locked Pixi environment"
    env = os.environ.copy()
    env.pop("LEFTHOOK_CONFIG", None)
    env.pop("LEFTHOOK", None)
    result = subprocess.run(
        [binary, "dump"], cwd=repo_copy, env=env, check=True,
        capture_output=True, text=True,
    )
    hooks = yaml.safe_load(result.stdout)
    assert {"pre-commit", "commit-msg", "pre-push"} <= set(hooks)
    assert hooks["commit-msg"]["jobs"][0]["run"] == "pixi run commit-lint < {1}"


def test_pre_push_cannot_be_filtered_by_changed_files(repo_copy):
    path = repo_copy / ".config" / "lefthook.yml"
    hooks = yaml.safe_load(path.read_text())
    hooks["pre-push"]["jobs"][0]["glob"] = "*.py"
    path.write_text(yaml.safe_dump(hooks))
    with pytest.raises(ScaffoldError, match="filter"):
        check_hook_policy(repo_copy)


def test_main_ci_runs_must_not_cancel_different_commits(repo_copy):
    path = repo_copy / ".github/workflows/ci.yml"
    data = yaml.safe_load(path.read_text())
    data["concurrency"]["group"] = "checks-${{ github.ref }}"
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ScaffoldError, match="SHA-distinct"):
        check_workflow_policy(repo_copy)


def test_sandbox_publisher_is_main_only(repo_copy):
    path = repo_copy / ".github/workflows/publish-sandbox.yml"
    document = yaml.safe_load(path.read_text())
    triggers = document.get("on", document.get(True, {}))
    triggers["pull_request"] = {}
    path.write_text(yaml.safe_dump(document, sort_keys=False))
    with pytest.raises(ScaffoldError, match="Never publish a sandbox from pull request code"):
        check_workflow_policy(repo_copy)


def test_sandbox_relock_can_only_commit_the_lockfile(repo_copy):
    path = repo_copy / ".github/workflows/relock.yml"
    document = yaml.safe_load(path.read_text())
    auto_commit = next(step for step in document["jobs"]["relock"]["steps"] if step.get("uses", "").startswith("stefanzweifel/git-auto-commit-action@"))
    auto_commit["with"]["file_pattern"] = "**/*"
    path.write_text(yaml.safe_dump(document, sort_keys=False))
    with pytest.raises(ScaffoldError, match="Automatic relock may commit only pixi.lock"):
        check_workflow_policy(repo_copy)


def test_project_shell_cannot_replace_thin_uncredentialed_steps(repo_copy):
    path = repo_copy / ".github/workflows/build.yml"
    data = yaml.safe_load(path.read_text())
    data["jobs"]["build"]["steps"].append({"run": "python scripts/build.py\necho done"})
    path.write_text(yaml.safe_dump(data))
    with pytest.raises(ScaffoldError, match="one-line Pixi"):
        check_workflow_policy(repo_copy)


def test_python_syntax_check_reports_bad_staged_file(tmp_path):
    (tmp_path / "bad.py").write_text("def broken(:\n")
    with pytest.raises(ScaffoldError, match="Python syntax"):
        check_python(["bad.py"], tmp_path)


def test_python_syntax_check_handles_deleted_staged_files(tmp_path):
    assert check_python(["deleted.py"], tmp_path) == 0
