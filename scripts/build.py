#!/usr/bin/env python3
"""Build or render only explicitly implemented component recipes."""
from __future__ import annotations

import argparse
import platform
from pathlib import Path

from common import ROOT, ScaffoldError, config, fail_cli, rattler, run, select_components


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--component", default="all", help="dem2points, fpcfilter, or all (default)")
    parser.add_argument("--render-only", action="store_true", help="Validate rendered recipes without solving/building")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output")
    options = parser.parse_args()
    if not options.render_only and (platform.system() != "Linux" or platform.machine().lower() not in ("x86_64", "amd64")):
        raise ScaffoldError("Native builds are enabled for linux-64 only")
    for name, component in select_components(options.component).items():
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
