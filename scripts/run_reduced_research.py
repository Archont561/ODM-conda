#!/usr/bin/env python3
"""Build and verify three private reduced candidates; discard all outputs."""
from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from common import ROOT, ScaffoldError, config, fail_cli, fetch_pinned_archive, rattler, run, sha256
from opensfm_graph_policy import PRIMARY
from opensfm_reduced_candidate import make_candidate as make_opensfm
from opensfm_reduced_recipe import prepare as prepare_opensfm
from poisson_reduced_candidate import make_candidate as make_poisson
from poisson_candidate_recipe import prepare as prepare_poisson


def run_one(name: str, root: Path) -> None:
    root.mkdir()
    cache = root/'cache'
    candidate = root/'candidate.tar.gz'
    prepared = root/'prepared'
    output = root/'output'
    if name == 'poisson':
        original = fetch_pinned_archive('poissonrecon', config()['components']['poissonrecon-odm']['source'], cache)
        make_poisson(original, candidate)
        prepare_poisson(candidate, prepared, original)
        recipe = prepared/'packaging/recipes/poissonrecon-odm/recipe.yaml'
        package_name = 'poissonrecon-odm'
    elif name == 'opensfm':
        original = fetch_pinned_archive('opensfm', PRIMARY, cache)
        make_opensfm(original, candidate)
        prepare_opensfm(original, candidate, prepared)
        recipe = prepared/'packaging/research/recipes/opensfm-scoped-odm/recipe.yaml'
        package_name = 'opensfm-scoped-odm'
    elif name == 'openmvs':
        run(['python', str(ROOT/'scripts/check_open_research_sources.py'), 'openmvs', '--cache', str(cache)])
        recipe = ROOT/'research/recipes/openmvs-odm/reduced.yaml'
        package_name = 'openmvs-odm'
    else:
        raise ScaffoldError('Unknown reduced research component')
    run([rattler(), 'build', '--recipe', str(recipe), '--target-platform', 'linux-64', '--variant-config', str(ROOT/'recipes/variants.yaml'), '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', str(output), '--log-style', 'plain'])
    packages = list((output/'linux-64').glob(package_name+'-*.conda'))
    if len(packages) != 1:
        raise ScaffoldError(f'Expected one {package_name} package')
    package = packages[0]
    run([rattler(), 'test', '--package-file', str(package), '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', str(root/'retest'), '--log-style', 'plain'])
    if name == 'poisson':
        run(['python', str(ROOT/'scripts/audit_poisson_research.py'), '--package', str(package), '--candidate', str(candidate)])
    else:
        run(['python', str(ROOT/'scripts/audit_open_research.py'), package_name, str(package)])
    print(f'PASS: {name} reduced research package SHA256 {sha256(package)}; local only', flush=True)


def run_all(root: Path) -> None:
    for name in ('poisson', 'opensfm', 'openmvs'):
        run_one(name, root/name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--component', choices=('poisson', 'opensfm', 'openmvs', 'all'), default='all')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='odm-reduced-research-') as temp:
        root = Path(temp)
        if args.component == 'all':
            run_all(root)
        else:
            run_one(args.component, root/args.component)
    print('PASS: private research outputs discarded; no release approval', flush=True)


if __name__ == '__main__':
    fail_cli(main)
