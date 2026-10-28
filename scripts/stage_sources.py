#!/usr/bin/env python3
"""Stage an experimental source plan; this does not build or authorize a package."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli
from source_graph import stage_graph


def load_plan(path: Path, name: str) -> dict:
    plans = json.loads(path.read_text())
    if plans.get("schema_version") != 1:
        raise ScaffoldError("Unsupported source plan schema")
    plan = plans["plans"].get(name)
    if plan is None:
        raise ScaffoldError(f"Unknown experimental source plan: {name}")
    for source in [plan["primary"], *plan["additional"]]:
        url, commit = source["url"], source["commit"]
        if not url.startswith("https://codeload.github.com/") or not url.endswith("/tar.gz/" + commit):
            raise ScaffoldError("Experimental archives must use commit-pinned GitHub URLs")
    if name == "opensfm":
        # Keep the research staging path bound to the exact separately verified
        # gitlink and archives. This is not a license or recipe approval.
        from opensfm_graph_policy import validate_opensfm_graph
        validate_opensfm_graph('opensfm-odm', {**plan['primary'],
                                                'additional_sources': plan['additional'],
                                                'disabled_build_trees': []})
    return plan


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", required=True)
    parser.add_argument("--output", required=True, type=Path, help="Fresh destination directory")
    parser.add_argument("--cache", type=Path, default=ROOT / ".cache" / "sources")
    args = parser.parse_args()
    plan = load_plan(ROOT / "research" / "source-graphs.json", args.component)
    primary = plan["primary"]
    stage_graph(primary["name"], primary, plan["additional"], args.cache, args.output)
    print(f"Staged experimental sources for {args.component} in {args.output}; not build- or release-validated.")


if __name__ == "__main__":
    fail_cli(main)
