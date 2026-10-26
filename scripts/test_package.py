#!/usr/bin/env python3
"""Reinstall each built artifact into a fresh rattler-build test environment."""
from __future__ import annotations

import argparse
from pathlib import Path

from common import ROOT, fail_cli, find_package, rattler, run, select_components


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", default="all")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output")
    options = parser.parse_args()
    for name, component in select_components(options.component).items():
        package = find_package(name, component, options.output_dir)
        run([rattler(), "test", "--package-file", str(package), "--channel", "conda-forge",
             "--channel-priority", "strict", "--output-dir", str(options.output_dir / "isolated-tests"),
             "--log-style", "plain"])


if __name__ == "__main__":
    fail_cli(main)
