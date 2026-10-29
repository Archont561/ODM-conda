#!/usr/bin/env python3
"""Temporary inspection of one pinned, non-published native-build artifact."""
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

ARTIFACT = '12884831960'
ZIP_SHA = '21526568d7fb39f0070ef929c01c50367881eb81eee1cdf6382cad496b6d2265'
REVISION = '2cc2861a8746589fda4bef57fcf29b1cd60b7f50'
NAMES = ('dem2mesh', 'renderdem', 'poissonrecon-odm')
WORK = ROOT / 'output' / 'batch-artifact-inspection'


def fetch():
    if not os.environ.get('GH_TOKEN'):
        raise ScaffoldError('Read-only GitHub token is required')
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / 'artifact.zip'
    with target.open('wb') as out:
        subprocess.run(['gh', 'api', f'repos/Archont561/ODM-conda/actions/artifacts/{ARTIFACT}/zip'], stdout=out, check=True)
    if target.stat().st_size > 100 * 1024 * 1024 or sha256(target) != ZIP_SHA:
        raise ScaffoldError('Artifact digest or size mismatch')
    print(f'PASS artifact {ARTIFACT} ZIP SHA256 {ZIP_SHA}', flush=True)


def extract(path, dest):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 100 * 1024 * 1024 or sha256(path) != ZIP_SHA:
        raise ScaffoldError('Artifact digest or size mismatch')
    found = {}
    total = 0
    with zipfile.ZipFile(path) as archive:
        for item in archive.infolist():
            parts = PurePosixPath(item.filename).parts
            if not parts or item.filename.startswith('/') or '..' in parts or '\\' in item.filename or item.is_dir():
                raise ScaffoldError('Unsafe or unexpected ZIP entry')
            base = parts[-1]
            if base in found or item.file_size > 100 * 1024 * 1024:
                raise ScaffoldError('Duplicate or oversized ZIP entry')
            total += item.file_size
            if total > 256 * 1024 * 1024 or len(found) >= 32:
                raise ScaffoldError('ZIP inspection limit exceeded')
            target = dest / ('linux-64' if base.endswith('.conda') else 'evidence') / base
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(item) as src, target.open('wb') as out:
                for block in iter(lambda: src.read(1024 * 1024), b''):
                    out.write(block)
            found[base] = target
    return found


def inspect_source(path, name, component):
    files = {}
    total = 0
    with tarfile.open(path, 'r:gz') as archive:
        for item in archive:
            parts = PurePosixPath(item.name).parts
            if not parts or item.name.startswith('/') or '..' in parts or '\\' in item.name or not item.isfile():
                raise ScaffoldError('Unsafe source-bundle entry')
            if item.name in files or item.size > 64 * 1024 * 1024:
                raise ScaffoldError('Duplicate or oversized source-bundle entry')
            total += item.size
            if total > 256 * 1024 * 1024 or len(files) >= 10000:
                raise ScaffoldError('Source inspection limit exceeded')
            stream = archive.extractfile(item)
            if stream is None:
                raise ScaffoldError('Unreadable source entry')
            raw = stream.read()
            files[item.name] = (hashlib.sha256(raw).hexdigest(), raw if item.name == 'SOURCE-MANIFEST.json' else None)
    manifest = json.loads(files['SOURCE-MANIFEST.json'][1])
    if (manifest.get('component') != name or manifest.get('version') != component['version']
            or manifest.get('build_number') != component['build_number'] or manifest.get('packaging_commit') != REVISION
            or manifest.get('upstream') != component['source']):
        raise ScaffoldError(f'Source manifest identity mismatch: {name}')
    for key, digest in manifest['files'].items():
        if key not in files or files[key][0] != digest:
            raise ScaffoldError(f'Source manifest digest mismatch: {key}')
    if set(files) != set(manifest['files']) | {'SOURCE-MANIFEST.json', 'README-SOURCE.txt'}:
        raise ScaffoldError('Unexpected source bundle entries')
    return {'sha256': sha256(path), 'manifest_files_verified': len(manifest['files']),
            'packaging_commit': manifest['packaging_commit'], 'packaging_dirty': manifest.get('packaging_dirty')}


def inspect():
    paths = extract(WORK / 'artifact.zip', WORK)
    components = config()['components']
    results = {}
    selected = set()
    for name in NAMES:
        component = components[name]
        packages = [p for base, p in paths.items() if base.startswith(name + '-' + component['version'] + '-') and base.endswith('.conda')]
        source_name = f"source-{name}-{component['version']}-b{component['build_number']}.tar.gz"
        report_name = f'audit-{name}.json'
        if len(packages) != 1 or source_name not in paths or report_name not in paths:
            raise ScaffoldError(f'Expected package, report and source bundle for {name}')
        package = packages[0]
        selected.update((package.name, source_name, report_name))
        result = audit(name, component, package)
        previous = json.loads(paths[report_name].read_text())
        for key in ('sha256', 'artifact', 'component', 'runtime_dependencies', 'elf_needed', 'rpath'):
            if previous.get(key) != result.get(key):
                raise ScaffoldError(f'Original audit differs: {name} {key}')
        result['source'] = inspect_source(paths[source_name], name, component)
        if name == 'poissonrecon-odm':
            _, payload = read_package(package)
            result['link_evidence'] = json.loads(payload['share/odm-conda/poissonrecon-odm/link-evidence.json'])
        results[name] = result
    if set(paths) != selected:
        raise ScaffoldError('Unexpected artifact contents or component selection')
    print('BATCH INSPECTION RESULT (not legal, security, or source completeness approval):')
    print(json.dumps({'artifact': ARTIFACT, 'zip_sha256': ZIP_SHA, 'packages': results}, indent=2, sort_keys=True), flush=True)
    print('PASS all three packages and source manifests inspected; release gates remain closed', flush=True)


def main():
    if sys.argv[1:] == ['fetch']:
        fetch()
    elif sys.argv[1:] == ['inspect']:
        inspect()
    else:
        raise ScaffoldError('Choose fetch or inspect')


if __name__ == '__main__':
    fail_cli(main)
