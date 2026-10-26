#!/usr/bin/env python3
"""Stage one audited artifact and its source bundle; never publish anything."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from audit_package import audit
from common import ROOT, ScaffoldError, fail_cli, find_package, select_components, sha256
from source_bundle import make_bundle


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output")
    parser.add_argument("--destination", type=Path, default=ROOT / "release-artifacts")
    parser.add_argument("--cache", type=Path, default=ROOT / ".cache" / "sources")
    options = parser.parse_args()
    selected = select_components(options.component)
    if len(selected) != 1:
        raise ScaffoldError("A release stages exactly one component, never 'all'")
    if options.destination.exists() and any(options.destination.iterdir()):
        raise ScaffoldError("Release staging directory must be empty; do not mix releases")
    options.destination.mkdir(parents=True, exist_ok=True)
    name, component = next(iter(selected.items()))
    package = find_package(name, component, options.output_dir)
    report = audit(name, component, package)
    # Source construction failure leaves no published binary: this command only stages.
    make_bundle(name, component, options.destination, options.cache)
    shutil.copy2(package, options.destination / package.name)
    (options.destination / "audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    files = sorted(path for path in options.destination.iterdir() if path.is_file())
    (options.destination / "SHA256SUMS").write_text("".join(f"{sha256(path)}  {path.name}\n" for path in files), encoding="ascii")
    print(f"Staged {name} in {options.destination}; publication has NOT occurred")


if __name__ == "__main__":
    fail_cli(main)
