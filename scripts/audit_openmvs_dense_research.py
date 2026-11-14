#!/usr/bin/env python3
"""Bounded private dense OpenMVS package audit, not source or license clearance."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli
from package_archive import read_package

NAME = 'openmvs-dense-research'
SHARE = f'share/odm-conda/{NAME}/'
FIXTURES = ('openmvs_synthetic_fixture.py', 'openmvs_pointcloud_fixture.py', 'openmvs_fixture.py',
            'texrecon_fixture.py', 'openmvs_tetraflow_weights_fixture.py', 'openmvs_odm_cleanup_fixture.py')
NOTICE_HASHES = frozenset({
    '0f072d4a0ef59e7f6864bb45629c37417ccef63025b58f4073109d1c830bc55f',
    'c231e8064c5afb62b99c49969cd0f0b8d5082f754e9950f4ff8dd20ebe7d1062',
    'fab3dd6bdab226f1c08630b1dd917e11fcb4ec5e1e020e2c16f83a0a13863e85',
    'c83230b770f17ef1386ea1fd3681271dd98aa93646bdbfb5bff3a1b7050fff9d',
    '09c21b5a8ca469b20e0ce3795f19370affba36f532e480e593c9712c91caf4c4',
})


def verify_index(index: dict) -> None:
    if (not isinstance(index, dict) or index.get('name') != NAME or
            index.get('version') != '0.0.0.dev20260827' or
            type(index.get('build_number')) is not int or index['build_number'] != 2 or
            index.get('subdir') != 'linux-64' or index.get('license') != 'LicenseRef-Unreviewed' or
            not re.fullmatch(r'research_cpucompat_[a-z0-9]+_2', str(index.get('build', '')))):
        raise ScaffoldError('Unexpected TetraFlow research package identity')
    deps = index.get('depends')
    if not isinstance(deps, list) or not all(isinstance(item, str) and item.split() for item in deps):
        raise ScaffoldError('Invalid package runtime dependencies')
    names = {item.split()[0] for item in deps}
    required = {'libboost', 'libopencv', 'libjxl', 'tbb', 'mpfr', 'gmp', 'libgomp', 'python'}
    if not required <= names:
        raise ScaffoldError('Missing TetraFlow runtime dependency')
    matches = [item for item in deps if item.split()[0] == 'libjxl']
    if not any(re.fullmatch(r'libjxl\s+>=0\.11(?:\.0)?,<0\.12(?:\.0a0)?', match) for match in matches):
        raise ScaffoldError('Unexpected TetraFlow JPEG XL ABI constraint')


def verify_contents(info: dict[str, bytes], payload: dict[str, bytes]) -> None:
    notice_hashes = {hashlib.sha256(data).hexdigest() for path, data in info.items() if path.startswith('info/licenses/')}
    if not NOTICE_HASHES <= notice_hashes:
        raise ScaffoldError(f'Missing or modified research metadata notice hashes: {sorted(NOTICE_HASHES - notice_hashes)}')
    expected = {'bin/ReconstructMesh', 'bin/DensifyPointCloud', SHARE + 'SOURCE.txt'} | {SHARE + name for name in FIXTURES}
    if set(payload) != expected:
        raise ScaffoldError('Unexpected or missing TetraFlow package payload')
    if not all(payload[name].startswith(b'\x7fELF') for name in ('bin/ReconstructMesh', 'bin/DensifyPointCloud')):
        raise ScaffoldError('TetraFlow executable is not ELF')
    if payload[SHARE + 'SOURCE.txt'] != b'PRIVATE RESEARCH ONLY: rights and ODM compatibility unreviewed.\n':
        raise ScaffoldError('Missing research provenance warning')
    for name in FIXTURES:
        if hashlib.sha256(payload[SHARE + name]).digest() != hashlib.sha256((ROOT / 'scripts' / name).read_bytes()).digest():
            raise ScaffoldError(f'Modified research fixture: {name}')


def audit(package: Path) -> None:
    info, payload = read_package(package)
    try:
        index = json.loads(info['info/index.json'])
    except (KeyError, ValueError) as error:
        raise ScaffoldError('Missing or invalid package index') from error
    verify_index(index)
    verify_contents(info, payload)
    patchelf = shutil.which('patchelf')
    if not patchelf:
        raise ScaffoldError('patchelf is required')
    with tempfile.TemporaryDirectory(prefix='tetraflow-audit-') as temp:
        for name in ('ReconstructMesh', 'DensifyPointCloud'):
            binary = Path(temp) / name
            binary.write_bytes(payload['bin/' + name])
            result = subprocess.run([patchelf, '--print-rpath', str(binary)], capture_output=True, text=True, check=True)
            for entry in result.stdout.strip().split(':'):
                if entry and not (entry in ('$ORIGIN', '${ORIGIN}') or entry.startswith(('$ORIGIN/', '${ORIGIN}/'))):
                    raise ScaffoldError('Non-relocatable dense research ELF RPATH')
    print('PASS: Dense research identity, payload, selected notices and RPATH; not a release audit', flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', type=Path)
    args = parser.parse_args()
    audit(args.package)


if __name__ == '__main__':
    fail_cli(main)
