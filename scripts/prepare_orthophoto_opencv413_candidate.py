#!/usr/bin/env python3
"""Stage an isolated, non-publishable orthophoto OpenCV 4.13 candidate.

The staged source URL names a future b3 source bundle and is not proof that it
exists. Never publish the candidate or treat the staged manifest as approval.
"""
import argparse
import json
import shutil
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli
from prepare_opencv413_research import prepare as prepare_research


def prepare(destination: Path, root: Path = ROOT) -> None:
    prepare_research(destination, root)
    try:
        recipe = destination / 'recipes/odm-orthophoto/recipe.yaml'
        text = recipe.read_text()
        before = 'build:\n  number: 2\n  string: research_${{ hash }}_2\n'
        after = 'build:\n  number: 3\n  string: candidate_opencv413_${{ hash }}_3\n'
        if text.count(before) != 1:
            raise ScaffoldError('Unexpected private orthophoto identity')
        recipe.write_text(text.replace(before, after))
        manifest = destination / 'recipes/components.json'
        data = json.loads(manifest.read_text())
        component = data['components']['odm-orthophoto']
        if component['build_number'] != 2:
            raise ScaffoldError('Unexpected published orthophoto build number')
        component['build_number'] = 3
        for key in component['release_checks']:
            component['release_checks'][key] = False
        manifest.write_text(json.dumps(data, indent=2) + '\n')
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path)
    args = parser.parse_args()
    prepare(args.destination)
    print('Prepared unpublished build 3 candidate; all staged release gates are closed.')


if __name__ == '__main__':
    fail_cli(main)
