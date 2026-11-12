#!/usr/bin/env python3
"""Inventory one caller-supplied source archive against an independently supplied SHA256.

This is bounded metadata, not a complete corresponding-source or rights audit.
The archive is not extracted or copied. Links and special files are rejected.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import ScaffoldError, fail_cli
from tetraflow_source_receipt import inspect_archive

SCOPE = ('one caller-selected source archive; no binary/source correspondence, '
         'dependency closure, installed-byte verification, legal review or release approval')


def inspect(path: Path, expected_sha256: str, root_name: str) -> dict:
    if not re.fullmatch(r'[0-9a-f]{64}', expected_sha256):
        raise ScaffoldError('Expected a lowercase SHA256')
    if (not root_name or root_name in ('.', '..') or '/' in root_name or
            '\\' in root_name or '\x00' in root_name):
        raise ScaffoldError('Expected a single archive root name')
    return {'schema_version': 1, 'scope': SCOPE, 'root': root_name,
            'archive': inspect_archive(path, expected_sha256, root_name)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--sha256', required=True, help='independently recorded expected SHA256')
    parser.add_argument('--root', required=True, help='expected top-level directory in the archive')
    args = parser.parse_args()
    print(json.dumps(inspect(args.archive, args.sha256, args.root), sort_keys=True, indent=2))


if __name__ == '__main__':
    fail_cli(main)
