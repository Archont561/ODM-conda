#!/usr/bin/env python3
"""Report recorded build/host Conda inputs from package metadata, not corresponding sources."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import yaml
from common import ScaffoldError, fail_cli, sha256
from package_archive import read_package

SCOPE = ('packaged rattler-build metadata only; binary URLs and hashes do not verify installed bytes, '
         'source provenance, legal rights, source completeness, reproducibility or approval')


def public_url(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        return None
    return urlunsplit(('https', parsed.hostname.lower(), parsed.path, '', ''))


def package_record(record: object) -> dict:
    if not isinstance(record, dict):
        raise ScaffoldError('Invalid resolved package record')
    keys = ('name', 'version', 'build', 'subdir', 'fn', 'sha256')
    if any(not isinstance(record.get(key), str) or not record[key] for key in keys):
        raise ScaffoldError('Incomplete resolved package identity')
    if not re.fullmatch(r'[a-f0-9]{64}', record['sha256']):
        raise ScaffoldError('Invalid binary package SHA256')
    if (Path(record['fn']).name != record['fn'] or record['subdir'] not in ('linux-64', 'noarch')
            or not record['fn'].endswith(('.conda', '.tar.bz2'))):
        raise ScaffoldError('Invalid binary package filename or platform')
    url = public_url(record.get('url'))
    if url is None or not url.endswith('/' + record['fn']):
        raise ScaffoldError('Missing or invalid public binary package URL')
    license = record.get('license')
    if license is not None and not isinstance(license, str):
        raise ScaffoldError('Invalid package license metadata')
    return {key: record[key] for key in keys} | {'binary_package_url': url, 'declared_license': license}


def inspect(package: Path) -> dict:
    package = Path(package)
    if package.is_symlink() or not package.is_file():
        raise ScaffoldError('Invalid package file')
    info, _ = read_package(package)
    try:
        index = json.loads(info['info/index.json'])
        rendered = yaml.safe_load(info['info/recipe/rendered_recipe.yaml'])
    except (KeyError, ValueError, yaml.YAMLError) as error:
        raise ScaffoldError('Missing or invalid package recipe metadata') from error
    if not isinstance(index, dict) or not isinstance(rendered, dict):
        raise ScaffoldError('Unexpected package metadata')
    for key in ('name', 'version', 'build', 'subdir'):
        if not isinstance(index.get(key), str) or not index[key]:
            raise ScaffoldError('Invalid output package identity')
    dependencies = rendered.get('finalized_dependencies')
    if not isinstance(dependencies, dict):
        raise ScaffoldError('Missing finalized build dependencies')
    groups = {}
    for kind in ('build', 'host'):
        group = dependencies.get(kind)
        if not isinstance(group, dict) or not isinstance(group.get('resolved'), list):
            raise ScaffoldError(f'Missing resolved {kind} dependencies')
        records = [package_record(item) for item in group['resolved']]
        if not records or len({(x['name'], x['version'], x['build'], x['subdir']) for x in records}) != len(records):
            raise ScaffoldError(f'Empty or duplicate {kind} dependencies')
        groups[kind] = sorted(records, key=lambda x: (x['name'], x['version'], x['build'], x['subdir']))
    return {'schema_version': 1, 'scope': SCOPE,
            'output': {k: index[k] for k in ('name', 'version', 'build', 'subdir')} | {'sha256': sha256(package)},
            'build': groups['build'], 'host': groups['host']}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.package), sort_keys=True, indent=2))


if __name__ == '__main__':
    fail_cli(main)
