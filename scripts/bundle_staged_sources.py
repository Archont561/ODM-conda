#!/usr/bin/env python3
"""Bundle experimental staged-source inputs; NOT a release source bundle.

The existing release bundler deliberately continues to reject external graphs.
This helper preserves research inputs for review and does not certify the graph,
its licenses, or an offline build.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import tarfile
import tempfile
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, fetch_pinned_archive, repository_files
from source_bundle import add_bytes
from source_graph import stage_graph
from stage_sources import load_plan


def bundle_plan(name: str, plan: dict, cache: Path, output: Path, root: Path = ROOT) -> Path:
    """Verify and stage a plan, then archive all inputs plus packaging source."""
    if output.exists() or output.is_symlink():
        raise ScaffoldError("Experimental bundle destination already exists")
    primary = plan["primary"]
    sources = [primary, *plan["additional"]]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".graph-bundle-", dir=output.parent) as directory:
        temp = Path(directory)
        stage_graph(primary["name"], primary, plan["additional"], cache, temp / "staged")
        entries = {f"packaging/{p.relative_to(root).as_posix()}": p.read_bytes()
                   for p in repository_files(root)}
        for source in sources:
            path = fetch_pinned_archive(source["name"], source, cache)
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != source["sha256"]:
                raise ScaffoldError(f"Source archive changed while bundling: {source['name']}")
            key = f"upstream/{source['name']}-{source['commit']}.tar.gz"
            if key in entries:
                raise ScaffoldError(f"Duplicate bundle entry: {key}")
            entries[key] = data
        entries["EXPERIMENTAL-MANIFEST.json"] = (json.dumps({
            "schema_version": 1,
            "status": "experimental; not a release source bundle",
            "component": name,
            "plan": plan,
            "files": {key: hashlib.sha256(data).hexdigest() for key, data in sorted(entries.items())},
        }, indent=2, sort_keys=True) + "\n").encode()
        temporary = temp / "bundle.tar.gz"
        with temporary.open("wb") as output_file:
            with gzip.GzipFile(filename="", mode="wb", fileobj=output_file, mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                    for key, data in sorted(entries.items()):
                        add_bytes(archive, key, data)
        # Hard-link publication fails rather than overwriting an existing file.
        os.link(temporary, output)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cache", type=Path, default=ROOT / ".cache" / "sources")
    args = parser.parse_args()
    plan = load_plan(ROOT / "research" / "source-graphs.json", args.component)
    result = bundle_plan(args.component, plan, args.cache, args.output)
    print(f"Experimental bundle: {result} (not approved for release)")


if __name__ == "__main__":
    fail_cli(main)
