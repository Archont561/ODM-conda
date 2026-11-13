#!/usr/bin/env python3
"""Build a private orthophoto candidate and source-input bundle from one stage.

Requires Pixi/rattler-build and network access to pinned inputs. The destination
is owner-controlled, private, and must not exist. No upload or publication.
This is not a full dependency-source or legal review.
"""
import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from common import ROOT, config, fail_cli, run, sha256
from private_odm_bundle import build_recipe, validate_destination
from prepare_orthophoto_opencv413_candidate import prepare
from source_bundle import make_bundle


def create(destination: Path) -> None:
    destination = Path(destination)
    validate_destination(destination)
    destination.mkdir(mode=0o700)
    try:
        with tempfile.TemporaryDirectory(prefix='orthophoto-candidate-') as tmp:
            work = Path(tmp)
            staged = work / 'stage'
            prepare(staged)
            recipe = staged / 'recipes/odm-orthophoto/recipe.yaml'
            component = config(staged)['components']['odm-orthophoto']
            source = make_bundle('odm-orthophoto', component, destination / 'source', work / 'cache', root=staged)
            package = build_recipe(recipe, 'odm-orthophoto', work / 'build')
            run([sys.executable, str(staged / 'scripts/audit_package.py'), '--component', 'odm-orthophoto',
                 '--output-dir', str(package.parent.parent), '--reports-dir', str(work / 'reports')])
            audit = json.loads((work / 'reports/audit-odm-orthophoto.json').read_text())
            if audit['sha256'] != sha256(package) or not package.name.endswith('_3.conda') or '-candidate_opencv413_' not in package.name:
                raise ValueError('Candidate artifact identity or digest mismatch')
            target = destination / 'package'
            target.mkdir(mode=0o700)
            shutil.copyfile(package, target / package.name)
            if sha256(target / package.name) != audit['sha256']:
                raise ValueError('Retained package differs from audited bytes')
            receipt = {
                'schema_version': 1,
                'scope': 'private candidate only; no dependency source closure, legal review, integration or release approval',
                'package': {'filename': package.name, 'sha256': audit['sha256']},
                'source_bundle': {'filename': source.name, 'sha256': sha256(source)},
                'staged_recipe_sha256': sha256(recipe),
                'staged_manifest_sha256': sha256(staged / 'recipes/components.json'),
                'audit': audit,
            }
            (destination / 'receipt.json').write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n')
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    create(args.destination)
    print('Retained private candidate and source inputs; record receipt hashes independently. No release approval.')


if __name__ == '__main__':
    fail_cli(main)
