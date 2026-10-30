#!/usr/bin/env python3
"""Summarize selected PyPI lock records without credentials or local paths.

This metadata report is not a runnable lock, wheel audit or license review.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import yaml
from common import ScaffoldError, fail_cli


def summarize(lock: dict, environment: str = 'default', platform: str = 'linux-64') -> dict:
    try:
        selections = lock['environments'][environment]['packages'][platform]
        packages = lock['packages']
        wanted = [x['pypi'] for x in selections if 'pypi' in x]
    except (KeyError, TypeError) as error:
        raise ScaffoldError('Missing lock environment or platform') from error
    if not isinstance(packages, list) or not all(isinstance(x, str) for x in wanted) or len(wanted) != len(set(wanted)):
        raise ScaffoldError('Invalid or duplicate PyPI selections')
    indexed = {}
    for item in packages:
        if not isinstance(item, dict) or 'pypi' not in item:
            continue
        locator = item['pypi']
        if not isinstance(locator, str) or locator in indexed:
            raise ScaffoldError('Invalid or duplicate PyPI lock record')
        indexed[locator] = item
    result = []
    for locator in wanted:
        if locator not in indexed:
            raise ScaffoldError('Missing selected PyPI lock record')
        parsed = urlsplit(locator)
        if parsed.scheme in ('https', 'http') and parsed.hostname in ('files.pythonhosted.org', 'pypi.org'):
            public = urlunsplit((parsed.scheme, parsed.hostname, parsed.path, '', ''))
        elif parsed.scheme == 'file' and Path(parsed.path).name:
            public = 'local-file:' + Path(parsed.path).name
        else:
            raise ScaffoldError('Unsupported PyPI lock URL')
        item = indexed[locator]
        record = {'binary_url': public}
        for key in ('name', 'version', 'sha256', 'md5', 'requires_python'):
            if key in item:
                value = item[key]
                if not isinstance(value, str) or '/' in value or '\\' in value:
                    raise ScaffoldError(f'Invalid lock field: {key}')
                record[key] = value
        if 'hash' in item:
            value = item['hash']
            if not isinstance(value, dict) or not all(k in ('sha256', 'md5') and isinstance(v, str) and v.isalnum() for k, v in value.items()):
                raise ScaffoldError('Invalid PyPI hash field')
            record['hash'] = value
        result.append(record)
    return {'scope': 'Selected PyPI lock metadata only; not a runnable lock, wheel or license audit.', 'environment': environment, 'platform': platform, 'packages': result}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lock', type=Path)
    parser.add_argument('--environment', default='default')
    parser.add_argument('--platform', default='linux-64')
    args = parser.parse_args()
    print(json.dumps(summarize(yaml.safe_load(args.lock.read_text()), args.environment, args.platform), sort_keys=True, indent=2))


if __name__ == '__main__':
    fail_cli(main)
