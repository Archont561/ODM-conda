#!/usr/bin/env python3
"""Check exact research archives before local research builds, without bundling."""
import argparse
from pathlib import Path

from common import ROOT, fail_cli, fetch_pinned_archive
from opensfm_graph_policy import PRIMARY, PYBIND11, verify_opensfm_archives
from source_bundle import graph_archives
from stage_sources import load_plan


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('component', choices=('openmvs', 'opensfm'))
    parser.add_argument('--cache', type=Path, default=ROOT / '.cache/sources')
    args = parser.parse_args()
    if args.component == 'opensfm':
        primary = fetch_pinned_archive(PRIMARY['name'], PRIMARY, args.cache)
        dependency = fetch_pinned_archive(PYBIND11['name'], PYBIND11, args.cache)
        verify_opensfm_archives(primary, dependency)
    else:
        plan = load_plan(ROOT / 'research/source-graphs.json', 'openmvs')
        graph_archives('openmvs-odm', {**plan['primary'], 'additional_sources': plan['additional'],
                                       'disabled_build_trees': []}, args.cache)
    print('PASS: pinned research archives scanned; no distribution or network-isolation approval implied')


if __name__ == '__main__':
    fail_cli(main)
