#!/usr/bin/env python3
"""Offline checks for Backlog ownership, skill provenance and isolated tooling.

Managed content hashes are checked by check_skills.mjs using the manager's actual
JavaScript localeCompare ordering, not an approximate Python collation.
"""
from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path
from typing import Any

import yaml

from common import ROOT, ScaffoldError, config, fail_cli, relative_path

LOCAL_SKILLS = {"session", "backlog", "odm-packaging", "release-review"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ScaffoldError(message)


def frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    require(len(parts) == 3 and not parts[0].strip(), f"Missing frontmatter: {path}")
    metadata = yaml.safe_load(parts[1])
    require(isinstance(metadata, dict), f"Invalid frontmatter: {path}")
    return metadata, parts[2]


def check_package_milestones(root: Path, tasks: dict[str, dict[str, Any]]) -> dict[str, int]:
    milestones: dict[str, dict[str, Any]] = {}
    active: set[str] = set()
    for folder in ("milestones", "archive/milestones"):
        for path in sorted((root / "backlog" / folder).glob("*.md")):
            milestone, _ = frontmatter(path)
            milestone_id = milestone.get("id", "")
            require(isinstance(milestone_id, str) and bool(re.fullmatch(r"m-\d+", milestone_id)), f"Invalid milestone ID: {path}")
            require(milestone_id not in milestones, f"Duplicate milestone ID: {milestone_id}")
            require(bool(milestone.get("title")), f"Missing milestone title: {milestone_id}")
            milestones[milestone_id] = milestone
            if folder == "milestones":
                active.add(milestone_id)

    sprints: dict[str, list[str]] = {milestone_id: [] for milestone_id in milestones}
    for task_id, task in tasks.items():
        milestone_id = task.get("milestone")
        if milestone_id:
            require(milestone_id in milestones, f"Unknown milestone {milestone_id} in {task_id}")
        if "sprint" not in task.get("labels", []):
            continue
        require(bool(milestone_id), f"Sprint {task_id} needs a milestone")
        dependencies = task.get("dependencies", [])
        require(bool(dependencies), f"Sprint {task_id} needs concrete work dependencies")
        require(any(tasks[dep].get("milestone") == milestone_id and "sprint" not in tasks[dep].get("labels", []) for dep in dependencies), f"Sprint {task_id} must depend on work in its own milestone")
        if task.get("status") == "Done":
            require(all(tasks[dep].get("status") == "Done" for dep in dependencies), f"Completed Sprint {task_id} has unfinished dependencies")
        sprints[milestone_id].append(task_id)
    for milestone_id in active:
        require(len(sprints[milestone_id]) == 1, f"Milestone {milestone_id} needs exactly one Sprint task")
    return {"milestones": len(milestones), "sprints": sum(map(len, sprints.values()))}


def check_agent_setup(root: Path = ROOT) -> dict[str, int]:
    require("roadmap" not in config(root), "Use Backlog, not recipes/components.json roadmap")
    require((root / "AGENTS.md").is_file(), "Missing agent routing")
    require(not (root / "docs").exists(), "Root docs/ is obsolete; maintain guides and evidence in backlog/docs")

    package = json.loads((root / "package.json").read_text())
    require(package.get("private") is True, "Repository JS tooling must not be publishable")
    require(package.get("packageManager") == "bun@1.3.11", "Pin the Bun package manager")
    require(package.get("devDependencies") == {"backlog.md": "1.53.0", "skills": "1.7.2"}, "Pin the reviewed Backlog and skills CLI versions exactly")
    require((root / "bun.lock").is_file(), "Commit the frozen Bun lock")
    tools = tomllib.loads((root / "pixi.toml").read_text())
    env = tools["environments"]["agent-tools"]
    require(env.get("no-default-feature") is True and env["features"] == ["agent-tools"], "Keep Bun isolated from packaging Python")
    require(tools["feature"]["agent-tools"]["dependencies"]["bun"] == "==1.3.11", "Pin the isolated Bun package")
    agent_tasks = tools["feature"]["agent-tools"]["tasks"]
    require(agent_tasks["bun-install"] == "bun install --frozen-lockfile --silent", "Freeze installs and keep structured CLI stdout clean")
    require(agent_tasks["bunx"] == {"depends-on": ["bun-install"], "cmd": "bun x --bun"}, "Use the installed Bun runtime and frozen local CLI dependencies")

    settings = yaml.safe_load((root / "backlog" / "config.yml").read_text())
    for setting in ("auto_commit", "remote_operations", "check_active_branches", "auto_open_browser"):
        require(settings.get(setting) is False, f"Backlog {setting} must remain disabled by default")
    statuses = settings["statuses"]
    require(settings["default_status"] in statuses, "Invalid default Backlog status")
    tasks: dict[str, dict[str, Any]] = {}
    for folder in ("tasks", "completed", "archive/tasks"):
        for path in sorted((root / "backlog" / folder).glob("*.md")):
            task, body = frontmatter(path)
            task_id = task.get("id", "")
            require(bool(re.fullmatch(r"TASK-\d+(?:\.\d+)*", task_id)), f"Invalid task ID: {path}")
            require(task_id not in tasks, f"Duplicate Backlog task ID: {task_id}")
            require(task.get("status") in statuses, f"Invalid Backlog status: {task_id}")
            require(bool(task.get("title")), f"Missing task title: {task_id}")
            require(bool(re.search(r"^- \[[ xX]\] #\d+ .+", body, re.MULTILINE)), f"Missing CLI acceptance criteria: {task_id}")
            deps = task.get("dependencies", [])
            require(isinstance(deps, list) and all(isinstance(dep, str) for dep in deps), f"Invalid dependencies: {task_id}")
            tasks[task_id] = task
    require(bool(tasks), "Seeded Backlog tasks are missing")
    for task_id, task in tasks.items():
        for dep in task.get("dependencies", []):
            require(dep in tasks, f"Unknown dependency {dep} in {task_id}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(task_id: str) -> None:
        require(task_id not in visiting, f"Backlog dependency cycle at {task_id}")
        if task_id in visited:
            return
        visiting.add(task_id)
        for dep in tasks[task_id].get("dependencies", []):
            visit(dep)
        visiting.remove(task_id)
        visited.add(task_id)

    for task_id in tasks:
        visit(task_id)

    hierarchy_counts = check_package_milestones(root, tasks)

    skill_root = root / ".agents" / "skills"
    installed = {path.parent.name for path in skill_root.glob("*/SKILL.md")}
    require(LOCAL_SKILLS <= installed, "Missing ODM-specific skills")
    lock = json.loads((root / "skills-lock.json").read_text())
    require(lock.get("version") == 1, "Unsupported skills lock schema")
    managed = lock["skills"]
    require({"tdd", "writing-for-agents", "refactor"} <= set(managed), "Missing reviewed managed skills")
    require(not (LOCAL_SKILLS & set(managed)), "Do not masquerade local skills as upstream-managed copies")
    require(set(managed) <= installed, "A locked managed skill is missing")
    licenses = json.loads((root / ".agents" / "licenses" / "manifest.json").read_text())["sources"]
    require("Archont561/pixi-sandbox" in licenses, "Preserve the adapted guidance license")
    for source, notice in licenses.items():
        require(bool(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", source)), "Invalid notice source")
        require(bool(re.fullmatch(r"[0-9a-f]{40}", notice.get("ref", ""))), "Pin imported notice source refs")
        require(notice.get("license") == "MIT", "Review checker policy before importing differently licensed guidance")
        notice_file = relative_path(root / ".agents" / "licenses", notice["file"])
        require(notice_file.is_file() and "Permission is hereby granted" in notice_file.read_text(), f"Missing imported MIT notice: {source}")
    for name in installed:
        metadata, _ = frontmatter(skill_root / name / "SKILL.md")
        require(metadata.get("name") == name and bool(metadata.get("description")), f"Invalid skill metadata: {name}")
    for name, entry in managed.items():
        require(entry.get("sourceType") == "github", f"Unreviewed managed source type: {name}")
        require(bool(re.fullmatch(r"[0-9a-f]{40}", entry.get("ref", ""))), f"Managed skill ref is not immutable: {name}")
        require(bool(re.fullmatch(r"[0-9a-f]{64}", entry.get("computedHash", ""))), f"Missing managed content hash: {name}")
        require(bool(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", entry.get("source", ""))), f"Invalid managed source: {name}")
        relative_path(root, entry["skillPath"])
        notice = licenses.get(entry["source"], {})
        require(notice.get("ref") == entry["ref"], f"Missing corresponding source license: {name}")
        notice_file = relative_path(root / ".agents" / "licenses", notice["file"])
        require(notice_file.is_file() and "Permission is hereby granted" in notice_file.read_text(), f"Missing imported MIT notice: {name}")
    require((root / ".agents" / "NOTICE.md").is_file(), "Missing imported-skill attribution")
    return {"tasks": len(tasks), **hierarchy_counts, "managed_skills": len(managed), "local_skills": len(installed - set(managed))}


def main() -> None:
    counts = check_agent_setup()
    print(f"PASS: {counts['tasks']} Backlog tasks, {counts['milestones']} milestones/{counts['sprints']} sprints, dependency graph, {counts['managed_skills']} pinned managed skills and {counts['local_skills']} local skills")


if __name__ == "__main__":
    fail_cli(main)
