#!/usr/bin/env python3
"""Offline structural checks for sources, recipes, toolchain, and publishing CI."""
from __future__ import annotations

import re
import shlex
import tomllib
from pathlib import Path

import yaml

from common import CHECKS, NAME_RE, ROOT, ScaffoldError, config, fail_cli, relative_path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ScaffoldError(message)


def check_repository(root: Path = ROOT) -> int:
    data = config(root)
    require(data.get("schema_version") == 1, "Unknown manifest schema")
    distribution = data["distribution"]
    require(distribution["platform"] == "linux-64", "Only linux-64 is implemented; do not advertise other platforms")
    require(bool(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", distribution["repository"])), "Invalid GitHub repository")
    require(bool(re.fullmatch(r"[a-z0-9-]+/[a-z0-9-]+", distribution["channel"])), "Use a canonical namespace/channel reference")
    require(bool(re.fullmatch(r"[0-9a-f]{40}", distribution["reference_odm"]["commit"])), "Reference ODM revision is not immutable")
    implemented = set()
    for name, component in data["components"].items():
        require(NAME_RE.fullmatch(name) is not None, f"Invalid package name: {name}")
        require(isinstance(component["version"], str) and re.fullmatch(r"[0-9][A-Za-z0-9.+_-]*", component["version"]) is not None, "Unsafe or invalid version")
        require(type(component["build_number"]) is int and component["build_number"] >= 0, "Invalid build number")
        require(set(component["release_checks"]) == set(CHECKS), f"Missing release checks for {name}")
        require(all(type(value) is bool for value in component["release_checks"].values()), "Release checks must be booleans, not strings")
        source = component["source"]
        require(re.fullmatch(r"[0-9a-f]{40}", source["commit"]) is not None, f"Unpinned source for {name}")
        require(re.fullmatch(r"[0-9a-f]{64}", source["sha256"]) is not None, f"Missing SHA256 for {name}")
        require(source["url"].startswith("https://codeload.github.com/") and source["url"].endswith("/" + source["commit"]), f"Use an immutable source archive for {name}")
        require(source["additional_sources"] == [], "External source graphs are not yet implemented; extend source bundling before enabling them")
        require(source.get("disabled_build_trees") == (["test"] if name == "fpcfilter" else []), "Unexpected disabled source tree; review source completeness explicitly")
        recipe_path = relative_path(root, component["recipe"])
        require(recipe_path.is_file(), f"Missing recipe: {recipe_path}")
        implemented.add(recipe_path)
        recipe = yaml.safe_load(recipe_path.read_text(encoding="utf-8"))
        require(recipe.get("schema_version") == 1, f"Wrong recipe schema for {name}")
        for key, expected in (("name", name), ("version", component["version"]), ("upstream_commit", source["commit"]), ("source_sha256", source["sha256"])):
            require(recipe["context"].get(key) == expected, f"Manifest/recipe context mismatch: {name}.{key}")
        require(recipe["source"]["url"] == source["url"], f"Source URL mismatch: {name}")
        require(recipe["source"]["sha256"] == "${{ source_sha256 }}", "Recipe must check its archive checksum")
        require(recipe["build"]["number"] == component["build_number"], f"Build-number mismatch for {name}")
        require(recipe["build"]["skip"] == 'target_platform != "linux-64"', "A recipe must skip unsupported platforms")
        script = recipe["build"]["script"]
        require((recipe_path.parent / script["file"]).resolve() == root / "scripts" / "build_component.py", "Unexpected build script")
        require(script["interpreter"] == "python", "Build script requires Python")
        require(recipe["about"]["license"] == component["license"], f"License mismatch for {name}")
        expected_notices = {".conda-notices/" + notice["target"] for notice in component["notices"]} | {".conda-notices/packaging-MIT.txt"}
        require(set(recipe["about"]["license_file"]) == expected_notices, f"Incomplete recipe notices for {name}")
        for notice in component["notices"]:
            relative_path(root, notice["source"])
            require(Path(notice["target"]).name == notice["target"], "Notice target must be a filename")
            require(notice["kind"] in ("verbatim", "first-comment"), "Unknown notice extraction mode")
        build = recipe["requirements"]["build"]
        require("${{ compiler('cxx') }}" in build and "${{ stdlib('c') }}" in build, "Use toolchain macros so ABI/runtime run_exports propagate")
        require(len(recipe.get("tests", [])) >= 2, f"Missing content/functional tests: {name}")
        require("noarch" not in recipe["build"], "Native component packages cannot be noarch")
    discovered = {path.resolve() for path in (root / "recipes").glob("*/recipe.yaml")}
    require(discovered == implemented, "Undeclared or missing recipes; planned tasks must not silently become buildable")
    tools = tomllib.loads((root / "pixi.toml").read_text())
    require(tools["workspace"]["platforms"] == ["linux-64"], "Do not claim untested platforms")
    require(tools["workspace"]["channels"] == ["conda-forge"], "Keep tooling dependencies on conda-forge only")
    require(tools["dependencies"]["rattler-build"] == "==" + data["tools"]["rattler_build"], "Pin the rattler-build tool version")
    require((root / "pixi.lock").is_file(), "Generate and commit pixi.lock")
    variants = yaml.safe_load((root / "recipes" / "variants.yaml").read_text())
    require(variants["cxx_compiler_version"] == ["14"] and variants["c_stdlib_version"] == ["2.28"], "Unexpected toolchain baseline; update policy/tests when changing it")

    check_workflow_policy(root)
    check_hook_policy(root)
    return len(implemented)


def check_workflow_policy(root: Path = ROOT) -> None:
    distribution = config(root)["distribution"]
    tools = tomllib.loads((root / "pixi.toml").read_text())
    workflows = root / ".github" / "workflows"
    workflow_paths = sorted([*workflows.glob("*.yml"), *workflows.glob("*.yaml")])
    for path in workflow_paths:
        document = yaml.safe_load(path.read_text())
        triggers = document.get("on", document.get(True, {}))  # YAML 1.1 treats 'on' as a bool.
        require("pull_request_target" not in triggers, "Never execute PR code with pull_request_target")
        require(document.get("permissions") == {"contents": "read"}, "Workflow default permissions must be contents: read")
        for job_name, job in document["jobs"].items():
            if job.get("permissions", {}).get("id-token") == "write":
                require(path.name == "release.yml" and job_name == "publish", "Only the isolated publish job may request OIDC")
            for step in job.get("steps", []):
                if "uses" in step:
                    require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[0-9a-f]{40}", step["uses"]) is not None, f"Action must be pinned to a full commit: {step['uses']}")
    release = yaml.safe_load((workflows / "release.yml").read_text())
    publisher = release["jobs"]["publish"]
    require(publisher["environment"] == distribution["github_environment"], "GitHub environment differs from publishing policy")
    require(all(not step.get("uses", "").startswith("actions/checkout@") for step in publisher["steps"]), "Publish job must not check out repository code")
    publisher_text = "\n".join(step.get("run", "") for step in publisher["steps"])
    require("--channel " + distribution["channel"] in publisher_text, "Wrong Prefix channel")
    require("--clobber" not in publisher_text and "--skip-existing" not in publisher_text, "Do not silently replace or skip immutable release artifacts")
    require("--generate-attestation" in publisher_text, "Keep publishing provenance enabled")
    ci = yaml.safe_load((workflows / "ci.yml").read_text())
    group = ci["concurrency"]["group"]
    require("github.sha" in group and "pull_request" in group, "PR runs may cancel by ref; main commits must have SHA-distinct check groups")
    require(release["concurrency"]["cancel-in-progress"] is False, "Do not cancel an active release")
    require("tag_name" not in release["concurrency"]["group"], "Serialize component releases rather than only identical tags")
    for path in workflow_paths:
        document = yaml.safe_load(path.read_text())
        for job_name, job in document["jobs"].items():
            if path.name == "release.yml" and job_name == "publish":
                continue  # Reviewed credential-isolated shell is intentional, not project code.
            runs = [step["run"] for step in job.get("steps", []) if "run" in step]
            require("pixi run check" in runs, f"Use the common cheap gate: {path.name}/{job_name}")
            require(all("\n" not in run and run.startswith("pixi run ") for run in runs), f"Keep uncredentialed workflow orchestration in one-line Pixi tasks: {path.name}/{job_name}")
            for step in job.get("steps", []):
                if step.get("uses", "").startswith("prefix-dev/setup-pixi@"):
                    require(step["with"].get("pixi-version") == "v" + config(root)["tools"]["pixi"], "Pin the expected Pixi client")
                    require(step["with"].get("locked") is True, "CI must install the committed Pixi lock")
    command = shlex.split(tools["tasks"]["workflows"])
    require(command[:3] == ["actionlint", "-shellcheck", "shellcheck"], "Require Actionlint with an explicit ShellCheck dependency")
    require({root / name for name in command[3:]} == set(workflow_paths), "Actionlint must cover every workflow explicitly, including source ZIPs without Git")


def check_hook_policy(root: Path = ROOT) -> None:
    tools = tomllib.loads((root / "pixi.toml").read_text())
    for name in ("convco", "lefthook", "actionlint", "shellcheck", "taplo"):
        require(bool(re.fullmatch(r"==[0-9]+\.[0-9]+\.[0-9]+", tools["dependencies"][name])), f"Pin direct hook/lint tool {name} exactly")
    require(tools["tasks"]["commit-lint"] == "test -f .config/convco.yml && convco check --config .config/convco.yml --from-stdin", "Commit-msg must lint stdin with the explicit shared policy")
    require(tools["tasks"]["commits"] == "test -f .config/convco.yml && convco check --config .config/convco.yml", "PR history must use the same Convco policy")
    policy = yaml.safe_load((root / ".config" / "convco.yml").read_text())
    owner, repository = config(root)["distribution"]["repository"].split("/", 1)
    require((policy.get("host"), policy.get("owner"), policy.get("repository")) == ("https://github.com", owner, repository), "Convco links must identify this packaging repository")
    kinds = policy.get("types", [])
    expected_types = {"feat", "fix", "perf", "refactor", "docs", "build", "ci", "test", "chore", "style"}
    require(len(kinds) == len(expected_types) and {kind.get("type") for kind in kinds} == expected_types, "Keep the reviewed Conventional Commit type set explicit")
    require(all(bool(kind.get("section")) and type(kind.get("hidden")) is bool for kind in kinds), "Specify changelog sections and visibility explicitly")
    require(policy.get("scopeRegex") == "^[[:alnum:]]+(?:[-_/][[:alnum:]]+)*$", "Anchor scope matching to reject partial invalid scopes")
    require(not (set(policy) & {"preMajor", "initialBumpVersion", "treatMajorZeroAsStable", "releaseCommitMessageFormat"}), "Native component version and release policy do not belong in Convco")
    hooks = yaml.safe_load((root / ".config" / "lefthook.yml").read_text())
    require(hooks["min_version"] == tools["dependencies"]["lefthook"][2:], "Align Lefthook's config floor and selected version")
    require(hooks["pre-commit"].get("parallel") is True, "Keep staged parser/formatter hooks fast")
    require(hooks["commit-msg"]["jobs"][0]["run"] == "pixi run commit-lint < {1}", "Conventional Commit hook must read the proposed message file")
    push = hooks["pre-push"]
    require(push.get("piped") is True and not push.get("parallel"), "Pre-push must run sequentially and fail fast")
    require(all(not (set(job) & {"glob", "files", "only", "skip"}) for job in push["jobs"]), "Do not filter away pre-push gates on empty/deletion-only diffs")
    require([job["run"] for job in push["jobs"]] == ["pixi run static", "pixi run unit", "pixi run agent-check", "pixi run render"], "Hooks must reuse the shared cheap gates, not silently add native publishing")


def main() -> None:
    count = check_repository()
    print(f"PASS: {count} component recipes, immutable sources, notices, toolchain and guarded workflows")


if __name__ == "__main__":
    fail_cli(main)
