#!/usr/bin/env python3
"""Inventory installed Conda metadata; this is not a source or license audit."""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from common import ScaffoldError, fail_cli


def inventory(prefix: Path) -> dict:
    prefix = Path(prefix)
    meta = prefix/'conda-meta'
    if prefix.is_symlink() or not prefix.is_dir() or meta.is_symlink() or not meta.is_dir():
        raise ScaffoldError('Invalid Conda environment prefix')
    records = []
    for path in sorted(meta.glob('*.json')):
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 8*1024*1024:
            raise ScaffoldError('Unsafe Conda metadata file')
        item = json.loads(path.read_text())
        if not all(isinstance(item.get(k), str) and item[k] for k in ('name', 'version', 'build')):
            raise ScaffoldError(f'Invalid package metadata: {path.name}')
        url = item.get('url') or ''
        parsed = urlsplit(url)
        if parsed.scheme in ('https', 'http') and parsed.hostname:
            # Remove user info, query and fragment; preserve only public host/path.
            public_url = urlunsplit((parsed.scheme, parsed.hostname, parsed.path, '', ''))
        elif parsed.scheme == 'file':
            public_url = 'local-file:' + Path(parsed.path).name
        else:
            public_url = None
        files = item.get('files') or []
        notices = [x for x in files if isinstance(x, str) and ('license' in x.lower() or 'copyright' in x.lower() or 'copying' in x.lower())]
        records.append({k: item.get(k) for k in ('name','version','build','build_number','subdir','sha256','md5','license','license_family')} | {'source_package_url': public_url, 'notice_paths': sorted(notices)})
    if not records:
        raise ScaffoldError('No installed Conda package metadata')
    return {'scope': 'Conda installation records only; URLs identify binary packages, not source archives. Metadata and filename heuristics are not legal, completeness or rights review. Pip distributions and package file bytes are not audited.', 'packages': sorted(records, key=lambda r: (r['name'],r['version'],r['build']))}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prefix', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(inventory(args.prefix), sort_keys=True, indent=2))


if __name__ == '__main__':
    fail_cli(main)
