#!/usr/bin/env python3
"""Prepare a distinct, image-excluded local-only JPEG XL research build.

It requires the verified original sdist and locked Cargo sources. This is not a
corresponding-source bundle, release recipe, rights clearance or publication.
"""
from __future__ import annotations

import argparse
import base64
import json
import shutil
import tempfile
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, sha256
from jxl_reduced_candidate import EXCLUDED, make_candidate
from prepare_jxl_source import prepare as prepare_original
from source_graph import unpack_archive

CANDIDATE_SHA256 = '29941b25637e871e8c60a33b1bc65a67322b7d6951700b5574f0c85799be0f52'
FIXTURE = ROOT/'scripts/jxl_synthetic_fixture.py'


def prepare(source: Path, destination: Path) -> Path:
    source, destination = Path(source), Path(destination)
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir() or destination.resolve().is_relative_to(ROOT):
        raise ScaffoldError('Unsafe or existing destination')
    with tempfile.TemporaryDirectory(prefix='jxl-reduced-verify-', dir=destination.parent) as temp:
        work = Path(temp)
        candidate = work/'candidate.tar.gz'
        manifest = make_candidate(source, candidate)
        if sha256(candidate) != CANDIDATE_SHA256:
            raise ScaffoldError('Unexpected reduced source candidate digest')
        tree = work/'candidate'; tree.mkdir()
        unpack_archive(candidate, tree)
        if json.loads((tree/'CANDIDATE-MANIFEST.json').read_text()) != manifest:
            raise ScaffoldError('Reduced source candidate manifest mismatch')
        if any(sha256(tree/name) != info['sha256'] for name, info in manifest['files'].items()):
            raise ScaffoldError('Reduced source file hash mismatch')
        prepared = False
        try:
            prepare_original(source, destination)
            prepared = True
            staged = destination/'source'
            for name, info in manifest['files'].items():
                if name == 'pyproject.toml':
                    original = (tree/name).read_text()
                    old = 'features = ["pyo3/extension-module", "vendored"]'
                    new = 'features = ["pyo3/extension-module", "dynamic"]'
                    if original.count(old) != 1 or (staged/name).read_text() != original.replace(old, new):
                        raise ScaffoldError('Unexpected dynamic feature patch')
                elif sha256(staged/name) != info['sha256']:
                    raise ScaffoldError(f'Prepared source differs from candidate: {name}')
            for name, digest in EXCLUDED.items():
                path = staged/'test/images'/name
                if path.is_symlink() or not path.is_file() or sha256(path) != digest:
                    raise ScaffoldError(f'Unexpected excluded test file: {name}')
                path.unlink()
            shutil.copy2(tree/'CANDIDATE-MANIFEST.json', staged/'CANDIDATE-MANIFEST.json')
            fixture = FIXTURE.read_bytes()
            recipe = destination/'recipe/recipe.yaml'
            text = recipe.read_text()
            old = 'build:\n  number: 1\n  string: research_${{ hash }}_1\n'
            new = 'build:\n  number: 2\n  string: research_reduced_${{ hash }}_2\n'
            if text.count(old) != 1:
                raise ScaffoldError('Unexpected research recipe build identity')
            text = text.replace(old, new)
            begin = text.index('tests:\n'); end = text.index('about:\n', begin)
            test_code = base64.b64encode(fixture).decode('ascii')
            text = text[:begin] + (
                "tests:\n  - script:\n      interpreter: python\n      content: |\n"
                f"        exec(__import__('base64').b64decode('{test_code}'), {{'__name__': '__main__'}})\n"
                "    requirements:\n      run:\n        - python >=3.12,<3.13\n"
            ) + text[end:]
            recipe.write_text(text)
            print(f'Prepared reduced research source {CANDIDATE_SHA256}; synthetic test SHA256 {sha256(FIXTURE)}; no release approval', flush=True)
            return destination
        except Exception:
            if prepared:
                shutil.rmtree(destination, ignore_errors=True)
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.source, args.destination)


if __name__ == '__main__':
    fail_cli(main)
