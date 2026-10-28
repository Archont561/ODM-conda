#!/usr/bin/env python3
"""Verify a preliminary notice inventory against a staged research tree.

This checks listed bytes only, not whether the inventory is complete or legally
sufficient. It does not authorize a package build or release.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, relative_path, sha256


def verify_inventory(tree: Path, inventory: dict) -> int:
    if inventory.get("schema_version") != 1:
        raise ScaffoldError("Unsupported notice inventory schema")
    entries = inventory.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ScaffoldError("Notice inventory must not be empty")
    seen: set[str] = set()
    for entry in entries:
        name, expected = entry["path"], entry["sha256"]
        if name in seen or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ScaffoldError(f"Duplicate path or invalid checksum: {name!r}")
        seen.add(name)
        path = relative_path(tree, name)
        if not path.is_file() or sha256(path) != expected:
            raise ScaffoldError(f"Notice file missing or checksum mismatch: {name}")
    return len(seen)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tree", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, default=ROOT / "research/mvs-texturing-notices.json")
    args = parser.parse_args()
    count = verify_inventory(args.tree, json.loads(args.inventory.read_text()))
    print(f"Verified {count} listed notice-bearing files; completeness and licensing remain unreviewed.")


if __name__ == "__main__":
    fail_cli(main)
