#!/usr/bin/env python3
"""Run local-only research builds and discard packages and source archives."""
import os
import tempfile
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, rattler, run


def main() -> None:
    component = os.environ.get('RESEARCH_COMPONENT', '')
    if component not in ('openmvs', 'opensfm'):
        raise ScaffoldError('Set RESEARCH_COMPONENT to openmvs or opensfm')
    parent = os.environ.get('RUNNER_TEMP')
    with tempfile.TemporaryDirectory(prefix='odm-open-research-', dir=parent) as temp:
        root = Path(temp)
        run(['python', str(ROOT / 'scripts/check_open_research_sources.py'), component, '--cache', str(root / 'sources')])
        output = root / 'output'
        run([rattler(), 'build', '--recipe', str(ROOT / 'research/recipes' / (component + '-odm') / 'recipe.yaml'),
             '--target-platform', 'linux-64', '--variant-config', str(ROOT / 'recipes/variants.yaml'),
             '--channel', 'conda-forge', '--channel-priority', 'strict', '--output-dir', str(output), '--log-style', 'plain'])
        packages = list((output / 'linux-64').glob(component + '-odm-*.conda'))
        if len(packages) != 1:
            raise ScaffoldError('Expected exactly one research package')
        run([rattler(), 'test', '--package-file', str(packages[0]), '--channel', 'conda-forge',
             '--channel-priority', 'strict', '--output-dir', str(root / 'retest'), '--log-style', 'plain'])
        run(['python', str(ROOT / 'scripts/audit_open_research.py'), component + '-odm', str(packages[0])])
    print('PASS: research build, retest and audit; temporary package and sources removed')


if __name__ == '__main__':
    fail_cli(main)
