#!/usr/bin/env python3
"""Fail closed until a reviewed component and an exact protected-branch tag agree."""
from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

from common import CHECKS, ROOT, ScaffoldError, config, fail_cli, release_tag


def reviewed_component(tag: str, data: dict) -> tuple[str, dict]:
    matches = [(name, component) for name, component in data["components"].items() if release_tag(name, component) == tag]
    if len(matches) != 1:
        raise ScaffoldError(f"Tag {tag!r} does not exactly match an implemented component/version/build number")
    name, component = matches[0]
    missing = [check for check in CHECKS if component.get("release_checks", {}).get(check) is not True]
    if missing:
        raise ScaffoldError(f"Publishing {name} is blocked. Review and commit these gates first: {', '.join(missing)}")
    return name, component


def check_git(tag: str, root: Path = ROOT) -> None:
    def git(*arguments: str) -> str:
        return subprocess.check_output(["git", *arguments], cwd=root, text=True, stderr=subprocess.PIPE).strip()
    head = git("rev-parse", "HEAD")
    tagged = git("rev-parse", "--verify", f"refs/tags/{tag}^{{commit}}")
    if tagged != head:
        raise ScaffoldError("The release tag must point to the exact trusted default-branch HEAD being built")
    if git("status", "--porcelain", "--untracked-files=normal"):
        raise ScaffoldError("The packaging checkout must be clean before a release")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--check-git", action="store_true", help="Require a clean checkout and exact HEAD/tag equality")
    parser.add_argument("--github-output", type=Path, help="Write safe outputs for a GitHub Actions job")
    options = parser.parse_args()
    data = config()
    if os.environ.get("GITHUB_REPOSITORY") and os.environ["GITHUB_REPOSITORY"] != data["distribution"]["repository"]:
        raise ScaffoldError("Repository identity differs from the configured publishing repository")
    name, component = reviewed_component(options.tag, data)
    if options.check_git:
        check_git(options.tag)
    if options.github_output:
        with options.github_output.open("a", encoding="utf-8") as handle:
            handle.write(f"component={name}\nversion={component['version']}\nbuild={component['build_number']}\n")
    print(f"Release gates passed for {options.tag}. This is a policy check, not legal certification.")


if __name__ == "__main__":
    fail_cli(main)
