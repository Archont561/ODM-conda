#!/usr/bin/env python3
"""Verify an independently anchored private orthophoto handoff, without publishing.

This checks bounded package/source metadata and hashes, not source completeness,
installed bytes, successful integration, legal rights, or release approval.
"""
import argparse
import hashlib
import json
import re
import tarfile
import tempfile
from pathlib import Path, PurePosixPath

from audit_package import audit
from common import ScaffoldError, fail_cli, sha256
from package_archive import read_package

MAX_MEMBER = 128 * 1024 * 1024
MAX_TOTAL = 512 * 1024 * 1024
HEX = re.compile(r'[0-9a-f]{64}')


def verify(directory: Path, receipt_sha256: str) -> dict:
    directory = Path(directory)
    receipt_file = directory/'receipt.json'
    if directory.is_symlink() or not directory.is_dir() or receipt_file.is_symlink() or not receipt_file.is_file():
        raise ScaffoldError('Missing or unsafe handoff directory or receipt')
    if not HEX.fullmatch(receipt_sha256) or sha256(receipt_file) != receipt_sha256:
        raise ScaffoldError('Receipt does not match independently supplied SHA256')
    data = json.loads(receipt_file.read_text())
    if data.get('schema_version') != 1:
        raise ScaffoldError('Unexpected handoff receipt schema')
    def item(key: str, folder: str) -> Path:
        obj = data.get(key)
        if not isinstance(obj, dict): raise ScaffoldError('Missing handoff identity')
        name, digest = obj.get('filename'), obj.get('sha256')
        if not isinstance(name, str) or Path(name).name != name or not isinstance(digest, str) or not HEX.fullmatch(digest):
            raise ScaffoldError('Invalid handoff filename or SHA256')
        parent = directory/folder; path = parent/name
        if parent.is_symlink() or not parent.is_dir() or path.is_symlink() or not path.is_file() or sha256(path) != digest:
            raise ScaffoldError(f'{key} missing, unsafe or checksum mismatch')
        if set(parent.iterdir()) != {path}: raise ScaffoldError(f'Unexpected files in {folder}')
        return path
    package = item('package', 'package'); source = item('source_bundle', 'source')
    if set(directory.iterdir()) != {receipt_file, directory/'package', directory/'source'}:
        raise ScaffoldError('Unexpected handoff files')
    info, _ = read_package(package)
    index = json.loads(info['info/index.json'])
    name, version, build = index.get('name'), index.get('version'), index.get('build')
    if (name != 'odm-orthophoto' or version != '0.0.0.dev20250225' or index.get('build_number') != 3
            or not isinstance(build, str) or not re.fullmatch(r'candidate_opencv413_[a-z0-9]+_3', build)
            or package.name != f'{name}-{version}-{build}.conda'
            or 'libopencv >=4.13,<4.14' not in index.get('depends', [])):
        raise ScaffoldError('Unexpected package identity or OpenCV dependency')
    with tarfile.open(source, 'r:gz') as archive:
        entries = {}; total = 0
        for entry in archive:
            parts = PurePosixPath(entry.name).parts
            if (not parts or entry.name.startswith('/') or '\\' in entry.name or '..' in parts
                    or entry.name != '/'.join(parts) or entry.name in entries or not entry.isfile()):
                raise ScaffoldError('Unsafe or duplicate source bundle entry')
            total += entry.size
            if entry.size < 0 or entry.size > MAX_MEMBER or total > MAX_TOTAL:
                raise ScaffoldError('Source bundle exceeds size limit')
            entries[entry.name] = entry
        def content(name: str) -> bytes:
            if name not in entries: raise ScaffoldError(f'Missing source entry: {name}')
            handle = archive.extractfile(entries[name])
            if handle is None: raise ScaffoldError('Cannot read source entry')
            with handle: return handle.read()
        manifest = json.loads(content('SOURCE-MANIFEST.json'))
        files = manifest.get('files')
        if (manifest.get('schema_version') != 1 or manifest.get('component') != name
                or manifest.get('version') != version or manifest.get('build_number') != 3
                or not isinstance(files, dict) or set(entries) != set(files) | {'SOURCE-MANIFEST.json', 'README-SOURCE.txt'}):
            raise ScaffoldError('Unexpected source manifest or entry set')
        for path, digest in files.items():
            if not path.startswith(('packaging/', 'upstream/')): raise ScaffoldError('Unexpected source manifest path')
            if not isinstance(digest, str) or not HEX.fullmatch(digest) or hashlib.sha256(content(path)).hexdigest() != digest:
                raise ScaffoldError(f'Source manifest checksum mismatch: {path}')
        recipe_path = 'packaging/recipes/odm-orthophoto/recipe.yaml'
        config_path = 'packaging/recipes/components.json'
        if files.get(recipe_path) != data.get('staged_recipe_sha256') or files.get(config_path) != data.get('staged_manifest_sha256'):
            raise ScaffoldError('Staged recipe or manifest does not match handoff receipt')
        config_bytes = content(config_path); config = json.loads(config_bytes)
        component = config['components'][name]
        upstream = manifest.get('upstream')
        gates = component.get('release_checks')
        if (component.get('build_number') != 3 or not isinstance(gates, dict)
                or set(gates) != {'publishable', 'license_reviewed', 'source_completeness_reviewed', 'native_validation_passed'}
                or any(value is not False for value in gates.values()) or upstream != component.get('source')):
            raise ScaffoldError('Staged component identity, gates or source differ')
        source_names = [key for key in files if key.startswith('upstream/')]
        if len(source_names) != 1 or files[source_names[0]] != upstream.get('sha256'):
            raise ScaffoldError('Upstream archive differs from source pin')
        recipe = content(recipe_path).decode('utf-8')
        if ('number: 3\n  string: candidate_opencv413_${{ hash }}_3' not in recipe
                or recipe.count('libopencv >=4.13,<4.14') != 2):
            raise ScaffoldError('Unexpected staged candidate recipe')
    # Audit against the exact manifest included in the source archive; the
    # source URL check establishes its expected value, not that the URL exists.
    with tempfile.TemporaryDirectory(prefix='orthophoto-handoff-verify-') as tmp:
        root = Path(tmp); (root/'recipes').mkdir(); (root/'recipes/components.json').write_bytes(config_bytes)
        checked = audit(name, component, package, root=root)
    if checked['sha256'] != data['package']['sha256'] or checked['result'] != 'passed':
        raise ScaffoldError('Re-audit did not match the anchored package')
    return {'result': 'passed', 'package_sha256': checked['sha256'], 'source_sha256': data['source_bundle']['sha256'],
            'source_manifest_entries': len(files), 'scope': 'private metadata and artifact audit only; not integration, source completeness, legal rights or release approval'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--receipt-sha256', required=True, help='Receipt SHA256 recorded independently of this handoff')
    args = parser.parse_args()
    print(json.dumps(verify(args.directory, args.receipt_sha256), indent=2, sort_keys=True))


if __name__ == '__main__': fail_cli(main)
