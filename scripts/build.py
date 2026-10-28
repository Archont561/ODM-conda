#!/usr/bin/env python3
"""Build or render only explicitly implemented component recipes."""
from __future__ import annotations

import argparse
import os
import platform
from pathlib import Path

from common import NAME_RE, ROOT, ScaffoldError, config, fail_cli, rattler, run, select_components


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--component", default="all", help="Comma-separated implemented component names, or all (default)")
    selection.add_argument("--workflow-checkboxes", action="store_true", help="Select components from workflow checkbox environment")
    parser.add_argument("--render-only", action="store_true", help="Validate rendered recipes without solving/building")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output")
    options = parser.parse_args()
    if not options.render_only and (platform.system() != "Linux" or platform.machine().lower() not in ("x86_64", "amd64")):
        raise ScaffoldError("Native builds are enabled for linux-64 only")
    component_selection = options.component
    if options.workflow_checkboxes:
        selected = []
        for name in config()["components"]:
            if NAME_RE.fullmatch(name) is None:
                raise ScaffoldError(f"Unsafe component name in manifest: {name!r}")
            key = "SELECT_" + name.replace("-", "_").upper()
            value = os.environ.get(key)
            if value not in ("true", "false"):
                raise ScaffoldError(f"Missing or invalid workflow checkbox {key}")
            if value == "true":
                selected.append(name)
        component_selection = ",".join(selected) if selected else "all"
        github_env = os.environ.get("GITHUB_ENV")
        if not github_env:
            raise ScaffoldError("GITHUB_ENV is required for workflow checkbox selection")
        # Only names from the trusted manifest can enter the environment file.
        with Path(github_env).open("a", encoding="utf-8") as output:
            output.write(f"COMPONENT={component_selection}\n")
        print(f"Workflow selection: {component_selection}", flush=True)
    for name, component in select_components(component_selection).items():
        if not options.render_only and component['source'].get('additional_sources'):
            # Verify and scan the exact graph before the isolated build; rattler
            # independently verifies its source checksums during staging.
            from source_bundle import graph_archives
            graph_archives(name, component['source'], ROOT / '.cache' / 'sources')
        command = [rattler(), "build", "--recipe", str(ROOT / component["recipe"]),
                   "--target-platform", config()["distribution"]["platform"],
                   "--variant-config", str(ROOT / "recipes" / "variants.yaml"),
                   "--channel", "conda-forge", "--channel-priority", "strict",
                   "--output-dir", str(options.output_dir.resolve()), "--log-style", "plain"]
        if options.render_only:
            command.append("--render-only")
        print(f"\n{'Render' if options.render_only else 'Build'}: {name}", flush=True)
        run(command)


if __name__ == "__main__":
    fail_cli(main)
