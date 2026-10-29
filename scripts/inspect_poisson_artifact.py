#!/usr/bin/env python3
"""Temporary, read-only inspection of one pinned Poisson CI artifact.

The ZIP digest, source digest, artifact ID and target filenames are immutable
for this investigation. No archive member is executed by the inspection.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import zipfile

from common import ROOT, ScaffoldError, config, fail_cli, sha256
from audit_package import audit
from package_archive import read_package

ARTIFACT_ID = '12880822311'
ZIP_SHA = 'cd3f7ab8b1fe3ebd3b77bd246b02af5b78035095c8c67b64336915a53ccca7d1'
SOURCE_SHA = '943f6b5e3e76b1c2a28ec80b8f1213738901aab3f2bd74dafb10029d05237eeb'
PACKAGE = 'poissonrecon-odm-13.8-h873e7db_2.conda'
SOURCE = 'source-poissonrecon-odm-13.8-b2.tar.gz'
REPORT = 'audit-poissonrecon-odm.json'
WORK = ROOT / 'output' / 'poisson-artifact-inspection'


def fetch() -> None:
    if not os.environ.get('GH_TOKEN'):
        raise ScaffoldError('Read-only GH_TOKEN is required for artifact download')
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / 'artifact.zip'
    with target.open('wb') as output:
        subprocess.run(['gh', 'api', f'repos/Archont561/ODM-conda/actions/artifacts/{ARTIFACT_ID}/zip'],
                       stdout=output, check=True)
    if target.stat().st_size > 100 * 1024 * 1024 or sha256(target) != ZIP_SHA:
        raise ScaffoldError('Artifact ZIP digest or size mismatch')
    print(f'PASS artifact {ARTIFACT_ID} ZIP SHA256 {ZIP_SHA}', flush=True)


def unpack_pinned_zip(path: Path, dest: Path) -> dict[str, Path]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 100 * 1024 * 1024 or sha256(path) != ZIP_SHA:
        raise ScaffoldError('Artifact ZIP digest or size mismatch')
    expected = {PACKAGE, SOURCE, REPORT}
    selected = {}
    with zipfile.ZipFile(path) as archive:
        for item in archive.infolist():
            name = item.filename
            parts = PurePosixPath(name).parts
            if not parts or name.startswith('/') or '..' in parts or '\\' in name or item.is_dir():
                raise ScaffoldError('Unsafe or unexpected ZIP entry')
            base = parts[-1]
            if base not in expected or base in selected or item.file_size > 100 * 1024 * 1024:
                raise ScaffoldError('Unexpected, duplicate, or oversized artifact entry')
            target = dest / ('linux-64' if base == PACKAGE else 'evidence') / base
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(item) as src, target.open('wb') as output:
                for chunk in iter(lambda: src.read(1024 * 1024), b''):
                    output.write(chunk)
            selected[base] = target
    if set(selected) != expected:
        raise ScaffoldError('Artifact ZIP does not contain the exact expected files')
    return selected


def inspect_source(path: Path) -> dict:
    if sha256(path) != SOURCE_SHA:
        raise ScaffoldError('Source-bundle SHA256 mismatch')
    files = {}
    total = 0
    with tarfile.open(path, 'r:gz') as archive:
        for item in archive:
            parts = PurePosixPath(item.name).parts
            if not parts or item.name.startswith('/') or '..' in parts or '\\' in item.name or not item.isfile():
                raise ScaffoldError('Unsafe source bundle member')
            if item.name in files or item.size > 64 * 1024 * 1024:
                raise ScaffoldError('Duplicate or oversized source bundle member')
            total += item.size
            if total > 256 * 1024 * 1024 or len(files) > 10000:
                raise ScaffoldError('Source bundle exceeds inspection limits')
            data = archive.extractfile(item).read()
            files[item.name] = (hashlib.sha256(data).hexdigest(), data if item.name == 'SOURCE-MANIFEST.json' else None)
    manifest = json.loads(files['SOURCE-MANIFEST.json'][1])
    if manifest.get('component') != 'poissonrecon-odm' or manifest.get('build_number') != 2 or manifest.get('packaging_commit') != '3ffabd94f2b1858b662e8ec66541fe5ac05fe3d5':
        raise ScaffoldError('Source manifest identity mismatch')
    for name, digest in manifest['files'].items():
        if name not in files or files[name][0] != digest:
            raise ScaffoldError(f'Source manifest digest mismatch: {name}')
    required = ['packaging/recipes/poissonrecon-odm/patches/0001-system-libpng.patch',
                'packaging/scripts/poisson_linkage.py', 'packaging/scripts/poisson_png_smoke.cpp']
    if not all(name in manifest['files'] for name in required):
        raise ScaffoldError('Source bundle missing the inspected patch or checks')
    return {'source_sha256': SOURCE_SHA, 'manifest_files_verified': len(manifest['files']),
            'packaging_commit': manifest['packaging_commit'], 'patch_sha256': files[required[0]][0]}


def inspect() -> None:
    paths = unpack_pinned_zip(WORK / 'artifact.zip', WORK)
    source = inspect_source(paths[SOURCE])
    component = config()['components']['poissonrecon-odm']
    result = audit('poissonrecon-odm', component, paths[PACKAGE])
    original = json.loads(paths[REPORT].read_text())
    for key in ('sha256', 'artifact', 'component', 'runtime_dependencies', 'elf_needed', 'rpath'):
        if original.get(key) != result.get(key):
            raise ScaffoldError(f'Original audit report differs: {key}')
    _, payload = read_package(paths[PACKAGE])
    evidence = json.loads(payload['share/odm-conda/poissonrecon-odm/link-evidence.json'])
    print('INSPECTION RESULT (named link inputs, not full security or license clearance):')
    print(json.dumps({'artifact_id': ARTIFACT_ID, 'zip_sha256': ZIP_SHA, 'package': result,
                      'link_evidence': evidence, 'source': source}, indent=2, sort_keys=True), flush=True)
    print('PASS independently inspected package and source; release gates remain closed', flush=True)


def main() -> None:
    if sys.argv[1:] == ['fetch']:
        fetch()
    elif sys.argv[1:] == ['inspect']:
        inspect()
    else:
        raise ScaffoldError('Choose fetch or inspect')


if __name__ == '__main__':
    fail_cli(main)
