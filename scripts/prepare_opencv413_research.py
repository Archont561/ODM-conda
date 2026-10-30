#!/usr/bin/env python3
"""Prepare disposable OpenCV 4.13 packaging copies, never release artifacts."""
import argparse
import shutil
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, repository_files

RECIPES = (
    'recipes/odm-orthophoto/recipe.yaml',
    'research/recipes/opensfm-scoped-odm/recipe.yaml',
    'research/recipes/openmvs-odm/reduced.yaml',
)
OLD = '>=4.12,<4.13'
NEW = '>=4.13,<4.14'
WARNING = '# PRIVATE OPENCV 4.13 ABI EXPERIMENT; NOT A RELEASE RECIPE\n'


def prepare(destination: Path, root: Path = ROOT) -> None:
    root, destination = Path(root).resolve(), Path(destination)
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir() or destination.resolve().is_relative_to(root):
        raise ScaffoldError('Destination must be a new directory outside the repository')
    files = repository_files(root)
    texts = {}
    for relative in RECIPES:
        recipe = root/relative
        if recipe not in files:
            raise ScaffoldError(f'Missing research input: {relative}')
        text = recipe.read_text()
        if text.count(OLD) != 2 or NEW in text:
            raise ScaffoldError(f'Unexpected OpenCV recipe constraints: {relative}')
        texts[relative] = WARNING + text.replace(OLD, NEW)
    try:
        destination.mkdir()
    except FileExistsError as error:
        raise ScaffoldError('Destination already exists') from error
    try:
        for path in files:
            if path.name.startswith(('tmp_', 'tmp-')):
                continue
            target = destination/path.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        for relative, text in texts.items():
            (destination/relative).write_text(text)
    except Exception:
        shutil.rmtree(destination, ignore_errors=True)
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path)
    args = parser.parse_args()
    prepare(args.destination)
    print('Prepared local-only ABI experiment; build/test/audit separately; no release approval.')


if __name__ == '__main__':
    fail_cli(main)
