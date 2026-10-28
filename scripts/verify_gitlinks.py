#!/usr/bin/env python3
"""Verify an experimental plan's gitlinks against its pinned Git commit.

A matching Git tree is evidence about submodule revisions only. It does not
verify archive equivalence, non-submodule sources, licenses or a build.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path, PurePosixPath

from common import ROOT, ScaffoldError, fail_cli
from stage_sources import load_plan


def verify_gitlinks(repository: Path, plan: dict) -> dict[str, str]:
    revision = plan['primary'].get('commit', '')
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ScaffoldError('Invalid primary Git revision')
    expected = {}
    for entry in plan['additional']:
        if type(entry.get('gitlink', False)) is not bool:
            raise ScaffoldError('Invalid gitlink marker')
        if not entry.get('gitlink', False):
            continue
        path, commit = entry['path'], entry['commit']
        parts = PurePosixPath(path).parts
        if (not parts or path.startswith('/') or '\\' in path or
                any(part in ('.', '..', '.git') for part in parts) or
                '/'.join(parts) != path or not re.fullmatch(r'[0-9a-f]{40}', commit)):
            raise ScaffoldError('Invalid expected gitlink path or revision')
        if path in expected:
            raise ScaffoldError('Duplicate expected gitlink path')
        expected[path] = commit
    kind = subprocess.run(['git', '-C', str(repository), 'cat-file', '-t', revision],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if kind.returncode or kind.stdout.strip() != b'commit':
        raise ScaffoldError('Pinned Git revision is not an available commit')
    result = subprocess.run(['git', '-C', str(repository), 'ls-tree', '-rz', '--full-tree', revision],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise ScaffoldError('Unable to read pinned Git tree; fetch the primary commit first')
    actual = {}
    try:
        for record in result.stdout.split(b'\0'):
            if not record:
                continue
            header, path = record.split(b'\t', 1)
            mode, kind, sha = header.decode('ascii').split(' ')
            if mode == '160000':
                if kind != 'commit':
                    raise ScaffoldError('Unexpected gitlink object type')
                actual[path.decode('utf-8')] = sha
    except (ValueError, UnicodeError) as error:
        raise ScaffoldError('Malformed Git tree output') from error
    if actual != expected:
        raise ScaffoldError(f'Pinned Git tree gitlinks differ from plan: expected {expected!r}, found {actual!r}')
    return actual


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--component', required=True)
    parser.add_argument('--repository', required=True, type=Path, help='Local Git repository containing the pinned commit')
    args = parser.parse_args()
    plan = load_plan(ROOT / 'research' / 'source-graphs.json', args.component)
    links = verify_gitlinks(args.repository, plan)
    print(f'PASS: {args.component} pinned Git tree contains {len(links)} expected gitlink(s); source completeness is not established.')


if __name__ == '__main__':
    fail_cli(main)
