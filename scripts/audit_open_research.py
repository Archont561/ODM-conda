#!/usr/bin/env python3
"""Audit non-distributable research packages; this is not a release audit."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

from common import ScaffoldError, fail_cli
from opensfm_assets_fixture import ASSETS
from package_archive import read_package


def verify_payload(name: str, payload: dict[str, bytes]) -> list[str]:
    if name not in ('openmvs-odm', 'opensfm-odm'):
        raise ScaffoldError('Unknown research component')
    share = f'share/odm-conda/{name}/'
    licenses = f'share/licenses/{name}/'
    required = {share + 'SOURCE.txt', licenses + 'packaging-MIT.txt', licenses + 'upstream-LICENSE.txt'}
    if name == 'openmvs-odm':
        required.update({'bin/ReconstructMesh', share + 'functional_test.py', share + 'openmvs_synthetic_fixture.py',
                         share + 'openmvs_pointcloud_fixture.py', share + 'texrecon_fixture.py'})
    else:
        required.update({'bin/opensfm', 'bin/opensfm_run_all', share + 'opensfm_main.py',
                         share + 'opensfm_fixture.py', share + 'opensfm_assets_fixture.py'})
    missing = required - payload.keys()
    if missing:
        raise ScaffoldError(f'Missing research package files: {sorted(missing)}')
    binaries = []
    for path, raw in payload.items():
        parts = PurePosixPath(path).parts
        if any(part in ('.git', '.pixi', '.cache', '__pycache__', 'src', 'test', 'tests') for part in parts):
            raise ScaffoldError(f'Checkout or build source leak: {path}')
        allowed = path.startswith(share) or path.startswith(licenses)
        if name == 'openmvs-odm':
            allowed |= path == 'bin/ReconstructMesh'
        else:
            allowed |= path in ('bin/opensfm', 'bin/opensfm_run_all')
            allowed |= bool(re.fullmatch(r'lib/python3\.12/site-packages/opensfm/.+\.(?:py|so|npz|json|yaml|txt|sqlite)', path))
        if not allowed:
            raise ScaffoldError(f'Unexpected package file or environment leak: {path}')
        if raw.startswith(b'\x7fELF'):
            binaries.append(path)
    if name == 'openmvs-odm':
        if 'bin/ReconstructMesh' not in binaries:
            raise ScaffoldError('ReconstructMesh is not ELF')
    else:
        root = 'lib/python3.12/site-packages/opensfm/'
        for module in ('pygeo', 'pygeometry', 'pyrobust', 'pybundle', 'pyfeatures', 'pydense', 'pysfm', 'pymap'):
            matches = [p for p in binaries if p.startswith(root + module + '.') and p.endswith('.so')]
            if len(matches) != 1:
                raise ScaffoldError(f'Missing or ambiguous OpenSfM native module: {module}')
        for path, digest in ASSETS.items():
            data = payload.get(root + path)
            if data is None or hashlib.sha256(data).hexdigest() != digest:
                raise ScaffoldError(f'Missing or modified OpenSfM asset: {path}')
    return binaries


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('component', choices=('openmvs-odm', 'opensfm-odm'))
    parser.add_argument('package', type=Path)
    args = parser.parse_args()
    info, payload = read_package(args.package)
    index = json.loads(info['info/index.json'])
    if index.get('name') != args.component or index.get('subdir') != 'linux-64':
        raise ScaffoldError('Research package identity mismatch')
    binaries = verify_payload(args.component, payload)
    patchelf = shutil.which('patchelf')
    if not patchelf:
        raise ScaffoldError('patchelf is required')
    with tempfile.TemporaryDirectory(prefix='odm-open-audit-') as directory:
        for i, name in enumerate(binaries):
            path = Path(directory) / str(i)
            path.write_bytes(payload[name])
            result = subprocess.run([patchelf, '--print-rpath', str(path)], text=True, capture_output=True, check=True)
            for entry in result.stdout.strip().split(':'):
                if entry and not (entry in ('$ORIGIN', '${ORIGIN}') or entry.startswith(('$ORIGIN/', '${ORIGIN}/'))):
                    raise ScaffoldError(f'Non-relocatable ELF RPATH in {name}: {entry}')
    print(f'PASS: {args.component} research leak and ELF RPATH audit; not license or release approval')


if __name__ == '__main__':
    fail_cli(main)
