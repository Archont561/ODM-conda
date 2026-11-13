#!/usr/bin/env python3
"""Inventory pinned ODM source requirements and feature markers, without extraction.

This is a static planning aid, not a dependency solver, rights review, feature
validation, production recipe, or evidence that a feature works.
"""
import argparse
import hashlib
import json
import re
import tarfile
from pathlib import Path

COMMIT = '47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45'
ARCHIVE_SHA256 = '5bdf8fe81b9ca47714e8a474139fd206b8090ac4315c2f530a58fcaef29cde5e'
ROOT = f'ODM-{COMMIT}/'
# Each marker is checked in a specific pinned upstream file, not inferred from
# successful imports, help output, or the research candidate's solver result.
MARKERS = {
    'dense_reconstruction': ('opendm/context.py', 'DensifyPointCloud'),
    'dem_to_mesh': ('opendm/mesh.py', 'context.dem2mesh_path'),
    'point_classification': ('opendm/point_cloud.py', 'OpenPointClass'),
    'split_merge': ('stages/splitmerge.py', 'LocalRemoteExecutor'),
    'dtm_enables_classification': ('opendm/config.py', 'if args.dtm and not args.pc_classify:'),
    'remote_processing': ('opendm/remote.py', 'def execute_remote_task('),
}
MAX_MEMBER = 4 * 1024 * 1024


def read_inventory(archive: Path, expected_sha256: str = ARCHIVE_SHA256) -> dict:
    digest = hashlib.sha256()
    with archive.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    if digest.hexdigest() != expected_sha256:
        raise ValueError('ODM source archive SHA256 mismatch')
    wanted = {'requirements.txt', *(path for path, _ in MARKERS.values())}
    found = {}
    with tarfile.open(archive, 'r:gz') as tar:
        for member in tar:
            if not member.name.startswith(ROOT):
                continue
            name = member.name[len(ROOT):]
            if name not in wanted:
                continue
            if name in found or not member.isfile() or member.size > MAX_MEMBER:
                raise ValueError(f'Invalid or duplicate source member: {name}')
            stream = tar.extractfile(member)
            if stream is None:
                raise ValueError(f'Cannot read source member: {name}')
            found[name] = stream.read().decode('utf-8')
    if found.keys() != wanted:
        raise ValueError('Missing expected upstream source files')
    requirements = []
    for line in found['requirements.txt'].splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        match = re.fullmatch(r'([A-Za-z0-9_.-]+)==([^\s#]+)', line)
        if not match:
            raise ValueError(f'Unexpected requirement: {line}')
        requirements.append({'name': match.group(1), 'version': match.group(2)})
    if len({item['name'].lower().replace('_', '-') for item in requirements}) != len(requirements):
        raise ValueError('Duplicate requirement')
    markers = {}
    for name, (path, marker) in MARKERS.items():
        if marker not in found[path]:
            raise ValueError(f'Expected source marker missing: {name}')
        markers[name] = {'file': path, 'marker': marker}
    return {'source_commit': COMMIT, 'archive_sha256': digest.hexdigest(),
            'requirements': requirements, 'feature_markers': markers,
            'scope': 'static source inventory only; not runtime, compatibility, source-rights, or release validation'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path, help='Exact pinned ODM source archive')
    args = parser.parse_args()
    print(json.dumps(read_inventory(args.archive), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
