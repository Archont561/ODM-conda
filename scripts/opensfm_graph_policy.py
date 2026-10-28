"""Recognize one OpenSfM research graph; not recipe or license approval.

A GitHub tarball does not carry the gitlink revision; the pinned Git tree was
verified separately by scripts/verify_gitlinks.py. Do not infer source or asset
rights from a successful fingerprint.
"""
from pathlib import Path
from typing import Any

from common import ROOT, ScaffoldError, relative_path, sha256
from openmvs_graph_policy import fingerprint_tree, rattler_generated_files

PRIMARY = {
    'name': 'opensfm',
    'commit': 'c5328439465e6ace011f39077d1077d7b1cdd65d',
    'sha256': '2bd9ec9ed20c5b426ff2808734e0a8849e2375038e378105f97128e48d704f8e',
    'url': 'https://codeload.github.com/OpenDroneMap/OpenSfM/tar.gz/c5328439465e6ace011f39077d1077d7b1cdd65d',
}
PYBIND11 = {
    'name': 'pybind11',
    'commit': 'a2e59f0e7065404b44dfe92a28aca47ba1378dc4',
    'sha256': '1da0a5c38950e4f49329e9de10c59b2527840a1b963113f1c53b455971cd6aef',
    'url': 'https://codeload.github.com/pybind/pybind11/tar.gz/a2e59f0e7065404b44dfe92a28aca47ba1378dc4',
    'path': 'opensfm/src/third_party/pybind11',
    'gitlink': True,
}
EXPECTED_TREE = (863, '16723bb06cd6b590a291fce8528ba1afb5ebf309c47f8cea12d7b1388d1e1351')
GITMODULES_SHA256 = 'b457f2f3550c9e951e0873a6e735d4722e26f9d023acf0ab73b327d33cf9e234'
PYBIND_FETCH_EXCEPTIONS = {
    'tests/CMakeLists.txt': '17198a0ad1946c01dfacd2b0d16a0193336e3c362c2bcbb3a1cebc1a67424c78',
    'tools/FindCatch.cmake': 'ec3e06c04de5830ff4cbe34c1aa9064bd69311716d7866e3dd9817957af78360',
}


def verify_opensfm_archives(primary: Path, pybind11: Path) -> None:
    # These narrow exceptions are only for these independently hash-pinned
    # archives. A static scan is not proof of network isolation or legal rights.
    from source_bundle import validate_upstream_archive

    for path, expected in ((primary, PRIMARY['sha256']), (pybind11, PYBIND11['sha256'])):
        if path.is_symlink() or not path.is_file() or sha256(path) != expected:
            raise ScaffoldError(f'OpenSfM archive checksum mismatch: {path}')
    validate_upstream_archive(primary, gitmodules_sha256=GITMODULES_SHA256)
    validate_upstream_archive(pybind11, fetch_exceptions=PYBIND_FETCH_EXCEPTIONS)


def validate_opensfm_graph(name: str, source: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    primary = {key: source.get(key) for key in ('commit', 'sha256', 'url')}
    expected = {key: PRIMARY[key] for key in ('commit', 'sha256', 'url')}
    if (name != 'opensfm-odm' or primary != expected
            or source.get('additional_sources') != [PYBIND11]
            or source.get('disabled_build_trees') != []):
        raise ScaffoldError('Unreviewed OpenSfM source graph')
    return dict(PRIMARY), [dict(PYBIND11)]


def validate_opensfm_patch(source: dict[str, Any], root: Path = ROOT) -> None:
    patches = source.get('patches')
    filename = 'research/patches/opensfm-ceres-config.patch'
    digest = '1cbf2c8044e0281368c8802205f14816fc3b635fb419a7d8fa3570603fdfd773'
    if (not isinstance(patches, list) or len(patches) != 1 or not isinstance(patches[0], dict)
            or patches[0].get('file') != filename or patches[0].get('sha256') != digest
            or patches[0].get('target') != '.' or not isinstance(patches[0].get('summary'), str) or not patches[0]['summary'].strip()):
        raise ScaffoldError('Unreviewed OpenSfM patch metadata')
    path = relative_path(root, filename)
    if (root / filename).is_symlink() or not path.is_file() or sha256(path) != digest:
        raise ScaffoldError('OpenSfM patch checksum mismatch')


def verify_opensfm_tree(tree: Path) -> None:
    expected = [
        {'url': PRIMARY['url'], 'sha256': PRIMARY['sha256'],
         'patches': ['patches/0001-ceres-config.patch']},
        {'url': PYBIND11['url'], 'sha256': PYBIND11['sha256'],
         'target_directory': PYBIND11['path']},
    ]
    ignored = rattler_generated_files(tree, expected, 'OpenSfM')
    if fingerprint_tree(tree, ignore_root_files=ignored) != EXPECTED_TREE:
        raise ScaffoldError('Unrecognized OpenSfM source tree fingerprint')


def main() -> None:
    import argparse
    from common import fail_cli
    from stage_sources import load_plan

    def verify() -> None:
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument('--tree', required=True, type=Path, help='Staged tree with the research patch applied')
        parser.add_argument('--primary-archive', type=Path)
        parser.add_argument('--pybind-archive', type=Path)
        args = parser.parse_args()
        if bool(args.primary_archive) != bool(args.pybind_archive):
            parser.error('provide both archives or neither')
        if args.primary_archive and args.pybind_archive:
            verify_opensfm_archives(args.primary_archive, args.pybind_archive)
        plan = load_plan(ROOT / 'research/source-graphs.json', 'opensfm')
        validate_opensfm_graph('opensfm-odm', {**plan['primary'], 'additional_sources': plan['additional'],
                                               'disabled_build_trees': []})
        validate_opensfm_patch({'patches': [{'file': 'research/patches/opensfm-ceres-config.patch',
                                            'sha256': '1cbf2c8044e0281368c8802205f14816fc3b635fb419a7d8fa3570603fdfd773',
                                            'target': '.', 'summary': 'Use Ceres config targets.'}]})
        verify_opensfm_tree(args.tree)
        print('PASS: exact patched OpenSfM research tree; not a recipe or license approval')

    fail_cli(verify)


if __name__ == '__main__':
    main()
