#!/usr/bin/env python3
"""Offline structural checks for sources, recipes, toolchain, and publishing CI."""
from __future__ import annotations

import re
import shlex
import tomllib
from pathlib import Path

import yaml

from common import CHECKS, NAME_RE, ROOT, ScaffoldError, config, fail_cli, relative_path, sha256
from texturing_graph_policy import validate_texturing_graph, validate_texturing_patches


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
        if name == "mvs-texturing-odm":
            validate_texturing_graph(name, source)
            validate_texturing_patches(source, root)
        else:
            require(source["additional_sources"] == [], "External source graphs require explicit staging and bundling support")
        require(source.get("disabled_build_trees") == (["test"] if name == "fpcfilter" else []), "Unexpected disabled source tree; review source completeness explicitly")
        recipe_path = relative_path(root, component["recipe"])
        require(recipe_path.is_file(), f"Missing recipe: {recipe_path}")
        implemented.add(recipe_path)
        recipe = yaml.safe_load(recipe_path.read_text(encoding="utf-8"))
        require(recipe.get("schema_version") == 1, f"Wrong recipe schema for {name}")
        for key, expected in (("name", name), ("version", component["version"]), ("upstream_commit", source["commit"]), ("source_sha256", source["sha256"])):
            require(recipe["context"].get(key) == expected, f"Manifest/recipe context mismatch: {name}.{key}")
        if name == "mvs-texturing-odm":
            expected_sources = [{"url": source["url"], "sha256": "${{ source_sha256 }}", "patches": ["patches/0001-offline.patch"]}]
            for item in source['additional_sources']:
                entry = {"url": item['url'], "sha256": item['sha256'], "target_directory": item['path']}
                if item['name'] == 'mve':
                    entry['patches'] = ["patches/0002-mve-baseline.patch"]
                expected_sources.append(entry)
            require(recipe['source'] == expected_sources, "Texturing recipe must stage the exact reviewed graph")
            for filename, patch in zip(('patches/0001-offline.patch', 'patches/0002-mve-baseline.patch'), source['patches']):
                path = relative_path(recipe_path.parent, filename)
                require(path.is_file() and sha256(path) == patch['sha256'], f"Recipe patch checksum mismatch: {filename}")
        else:
            require(recipe["source"]["url"] == source["url"], f"Source URL mismatch: {name}")
            require(recipe["source"]["sha256"] == "${{ source_sha256 }}", "Recipe must check its archive checksum")
            if name == "poissonrecon-odm":
                patches = source.get("patches", [])
                expected_patches = ["patches/0001-system-libpng.patch", "patches/0002-ijg-readme.patch"]
                require(len(patches) == len(expected_patches) and recipe["source"].get("patches") == expected_patches, "PoissonRecon must apply the exact reviewed patches")
                for patch, filename in zip(patches, expected_patches):
                    expected_path = "recipes/poissonrecon-odm/" + filename
                    require(patch["file"] == expected_path and sha256(relative_path(root, expected_path)) == patch["sha256"], "PoissonRecon patch checksum mismatch")
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
            permissions = job.get("permissions", {})
            if permissions.get("id-token") == "write":
                require(path.name == "release.yml" and job_name == "publish", "Only the isolated Prefix publisher may request OIDC")
            if permissions.get("contents") == "write":
                require(
                    (path.name == "publish-sandbox.yml" and job_name in {"publish", "upgrade"})
                    or (path.name == "relock.yml" and job_name == "relock")
                    or (path.name == "release.yml" and job_name == "publish"),
                    f"Unexpected write-capable workflow job: {path.name}/{job_name}",
                )
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
        if path.name in {"publish-sandbox.yml", "relock.yml"}:
            continue  # These generated workflows have separate, explicit least-privilege policies below.
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
    check_sandbox_workflow_policy(root, workflow_paths)
    command = shlex.split(tools["tasks"]["workflows"])
    require(command[:3] == ["actionlint", "-shellcheck", "shellcheck"], "Require Actionlint with an explicit ShellCheck dependency")
    require({root / name for name in command[3:]} == set(workflow_paths), "Actionlint must cover every workflow explicitly, including source ZIPs without Git")


def check_sandbox_workflow_policy(root: Path, workflow_paths: list[Path]) -> None:
    workflows = root / ".github" / "workflows"
    names = {path.name for path in workflow_paths}
    require({"publish-sandbox.yml", "relock.yml"} <= names, "Keep both generated Pixi sandbox workflows under structural checks")
    sandbox = tomllib.loads((root / "pixi-sandbox.toml").read_text())
    require(sandbox.get("schema") == 1 and sandbox.get("branch_prefix") == "sandbox", "Use the reviewed Pixi sandbox schema and branch prefix")
    require(sandbox.get("cargo_vendor") is False, "This Python/Conda project must not publish a Cargo vendor tree")
    bundles = sandbox.get("bundle", [])
    require(len(bundles) == 1, "Publish one explicit developer bundle")
    bundle = bundles[0]
    require(bundle.get("name") == "developer", "Use the documented developer sandbox bundle name")
    require(bundle.get("environments") == ["default", "agent-tools", "odm-dev"], "Publish all locked project environments")
    require(bundle.get("platforms") == ["linux-64"], "Do not publish untested sandbox platforms")
    require(all(isinstance(sandbox.get("budgets", {}).get(key), int) and sandbox["budgets"][key] > 0 for key in ("max_blob_mib", "max_transport_mib", "max_repository_push_mib", "max_restore_required_mib")), "Set positive transport safety budgets")

    publish = yaml.safe_load((workflows / "publish-sandbox.yml").read_text())
    triggers = publish.get("on", publish.get(True, {}))
    require(triggers.get("push", {}).get("branches") == ["main"], "Sandbox transport publication must run from main only")
    require("pull_request" not in triggers and "pull_request_target" not in triggers, "Never publish a sandbox from pull request code")
    require(publish["permissions"] == {"contents": "read"}, "Keep sandbox workflow default permissions read-only")
    require(publish["concurrency"]["cancel-in-progress"] is False, "Do not cancel a sandbox branch publish mid-push")
    jobs = publish["jobs"]
    require({"plan", "publish", "upgrade"} <= set(jobs), "Keep planning, publishing and reviewed upgrade jobs separate")
    require(jobs["upgrade"].get("permissions") == {"contents": "write", "pull-requests": "write"}, "Scope workflow-upgrade permissions to its PR-producing job")
    require("secrets.PIXI_SANDBOX_UPGRADE_TOKEN || github.token" in "\\n".join(step.get("env", {}).get("GITHUB_TOKEN", "") for step in jobs["upgrade"]["steps"]), "Keep the optional upgrade token fallback explicit")
    require("pixi-sandbox plan --config pixi-sandbox.toml --json" in "\n".join(step.get("run", "") for step in jobs["plan"]["steps"]), "Plan the publish matrix from the reviewed manifest")
    pub = jobs["publish"]
    require(pub.get("needs") == "plan" and pub.get("permissions") == {"contents": "write"}, "Only the actual publisher job may push sandbox branches")
    steps = pub.get("steps", [])
    checkout = next((step for step in steps if step.get("uses", "").startswith("actions/checkout@")), {})
    require(checkout.get("with", {}).get("persist-credentials") is False, "Do not persist checkout credentials in the publisher")
    pipeline = next((step for step in steps if "pipeline" in step.get("run", "")), None)
    require(pipeline is not None, "Run the verified Pixi sandbox pack/publish pipeline")
    require(pipeline.get("env", {}).get("PIXI_SANDBOX_PUSH_TOKEN") == "${{ github.token }}", "Pass the short-lived GitHub token only to the publisher pipeline step")
    run = pipeline["run"]
    require('--config pixi-sandbox.toml' in run and '--branch "${{ matrix.branch }}"' in run, "Publish the explicitly planned bundle branch")
    require('--remote "${{ github.server_url }}/${{ github.repository }}.git"' in run, "Publish only to this repository's Git remote")
    require(all(step.get("with", {}).get("pixi-version") == "v" + config(root)["tools"]["pixi"] for step in steps if step.get("uses", "").startswith("prefix-dev/setup-pixi@")), "Pin sandbox workflow Pixi setup to the repository version")
    require("SHA256SUMS" in "\n".join(step.get("run", "") for step in steps), "Verify the standalone publisher binary checksum before execution")

    relock = yaml.safe_load((workflows / "relock.yml").read_text())
    triggers = relock.get("on", relock.get(True, {}))
    require("pull_request" in triggers and "workflow_dispatch" in triggers, "Relock guard must validate PRs and support repaired-head verdicts")
    require(relock["permissions"] == {"contents": "read"}, "Keep relock workflow defaults read-only")
    relock_jobs = relock["jobs"]
    guard_runs = [step.get("run", "") for step in relock_jobs["guard"]["steps"]]
    require("pixi lock --check" in guard_runs, "Check the committed lock before any repair")
    repair = relock_jobs["relock"]
    require(repair.get("permissions") == {"contents": "write", "actions": "write", "checks": "write"}, "Scope lock repair writes to its PR-only job")
    require("needs.guard.result == 'failure'" in repair.get("if", "") and "pull_request" in repair.get("if", ""), "Only repair a failed lock guard on a pull request")
    fork_guard = next((step for step in repair.get("steps", []) if "fork" in step.get("name", "").lower()), None)
    require(fork_guard is not None and "exit 1" in fork_guard.get("run", ""), "Fail explicitly for fork PRs where branch write tokens are unavailable")
    auto_commit = next((step for step in repair.get("steps", []) if step.get("uses", "").startswith("stefanzweifel/git-auto-commit-action@")), None)
    require(auto_commit is not None and auto_commit.get("with", {}).get("file_pattern") == "pixi.lock", "Automatic relock may commit only pixi.lock")
    verdict = relock_jobs["verdict"]
    require(verdict.get("permissions") == {"actions": "read", "checks": "write"}, "Limit detached relock verdict permissions")
    require(all(not step.get("uses", "").startswith("actions/checkout@") for step in verdict.get("steps", [])), "The detached relock observer must not check out PR code")
    require(all(step.get("with", {}).get("pixi-version") == "v" + config(root)["tools"]["pixi"] for job in relock_jobs.values() for step in job.get("steps", []) if step.get("uses", "").startswith("prefix-dev/setup-pixi@")), "Pin relock Pixi operations to the repository version")
    restore = (root / "restore.sh").read_text()
    require("PIXI_SANDBOX_USER_TOOLS" in restore and 'exec "$BIN" restore' in restore, "Keep the generated restore entrypoint's explicit tool-registration behavior")

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
