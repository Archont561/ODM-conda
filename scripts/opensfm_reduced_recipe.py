#!/usr/bin/env python3
"""Prepare a private scoped recipe from the pinned reduced OpenSfM archive."""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, repository_files, sha256
from openmvs_graph_policy import fingerprint_tree
from opensfm_reduced_candidate import make_candidate
from source_graph import unpack_archive

EXPECTED_REDUCED_GRAPH = (874, '74c5be8ef66a189a8001816e7564e6b83144856dff176ca2674798f7b809b6d9')
GENERATED = frozenset({'.source_info.json', 'build_env.sh', 'conda_build.sh', 'conda_build.log'})


def verify_reduced_opensfm_research_tree(tree: Path) -> None:
    """Verify all retained sources, including exact pybind11 and vmem bytes.

    Ignore only rattler build-generated root files; no source or legal approval.
    """
    tree = Path(tree)
    for name in GENERATED:
        path = tree / name
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise ScaffoldError('Unsafe rattler-generated file')
    if fingerprint_tree(tree, ignore_root_files=GENERATED) != EXPECTED_REDUCED_GRAPH:
        raise ScaffoldError('Unrecognized reduced OpenSfM source graph')


def prepare(original: Path, candidate: Path, destination: Path, root: Path = ROOT) -> dict:
    original, candidate, destination, root = map(Path, (original, candidate, destination, root))
    if candidate.is_symlink() or not candidate.is_file():
        raise ScaffoldError('Invalid candidate')
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir() or destination.resolve().is_relative_to(root.resolve()):
        raise ScaffoldError('Unsafe or existing destination')
    with tempfile.TemporaryDirectory(prefix='opensfm-verify-', dir=destination.parent) as temp:
        expected = Path(temp) / 'expected.tar.gz'
        manifest = make_candidate(original, expected)
        if sha256(expected) != sha256(candidate):
            raise ScaffoldError('Candidate differs from reproducible pinned original')
        try:
            destination.mkdir()
        except FileExistsError as error:
            raise ScaffoldError('Unsafe or existing destination') from error
        try:
            source = destination / 'source'
            source.mkdir()
            unpack_archive(candidate, source)
            (source / 'CANDIDATE-MANIFEST.json').unlink()
            packaging = destination / 'packaging'
            for path in repository_files(root):
                relative = path.relative_to(root)
                if path.name.startswith(('tmp-', 'tmp_')):
                    continue
                target = packaging / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
            recipe = packaging / 'research/recipes/opensfm-scoped-odm/recipe.yaml'
            text = recipe.read_text()
            url = '  - url: https://codeload.github.com/OpenDroneMap/OpenSfM/tar.gz/c5328439465e6ace011f39077d1077d7b1cdd65d\n    sha256: 2bd9ec9ed20c5b426ff2808734e0a8849e2375038e378105f97128e48d704f8e\n'
            if text.count(url) != 1:
                raise ScaffoldError('Unexpected scoped recipe')
            text = text.replace(url, '  - path: ' + json.dumps(str(source.resolve())) + '\n')
            recipe.write_text('# LOCAL RESEARCH ONLY - reduced candidate; not a release recipe\n' + text)
            builder = packaging / 'scripts/build_open_research.py'
            script = builder.read_text()
            before = '        verify_opensfm_research_tree(source)'
            if script.count(before) != 1 or script.count('make_scoped_runtime(staged, scoped)') != 1:
                raise ScaffoldError('Unexpected research builder')
            script = script.replace(before, '        from opensfm_reduced_recipe import verify_reduced_opensfm_research_tree\n        verify_reduced_opensfm_research_tree(source)')
            script = script.replace('make_scoped_runtime(staged, scoped)', 'make_scoped_runtime(staged, scoped, assets_preexcluded=True)')
            old = "Upstream archives and other rights are not cleared for redistribution.\\n'"
            if script.count(old) != 1:
                raise ScaffoldError('Unexpected scoped source warning')
            digest = sha256(candidate)
            script = script.replace(old, 'Reduced source candidate SHA256 ' + digest + '; original archive not included in candidate. Upstream archives and other rights are not cleared for redistribution.\\n\'')
            builder.write_text(script)
            (destination / 'CANDIDATE-MANIFEST.json').write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
            return {'candidate_sha256': digest, 'source_graph_sha256': EXPECTED_REDUCED_GRAPH[1], 'scope': 'local-research-only'}
        except Exception:
            shutil.rmtree(destination)
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', required=True, type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    parser.add_argument('--destination', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(prepare(args.original, args.candidate, args.destination), sort_keys=True, indent=2))


if __name__ == '__main__':
    fail_cli(main)
