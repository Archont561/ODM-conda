#!/usr/bin/env python3
"""Audit private reduced Poisson artifacts; never substitute for release audit."""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

from common import ScaffoldError, config, fail_cli, sha256
from package_archive import read_package
from poisson_linkage import verify_poisson_package_evidence
from poisson_reduced_candidate import PINNED_SHA256

NAME = 'poissonrecon-odm'
PREFIX = f'share/odm-conda/{NAME}/'


def verify_metadata(info: dict, payload: dict, candidate_sha256: str) -> None:
    import re
    component = config()['components'][NAME]
    if not re.fullmatch(r'[0-9a-f]{64}', candidate_sha256):
        raise ScaffoldError('Invalid candidate SHA256')
    index = json.loads(info['info/index.json'])
    if any(index.get(k) != v for k, v in [('name', NAME), ('version', component['version']), ('build_number', component['build_number']), ('subdir', 'linux-64')]):
        raise ScaffoldError('Research artifact identity mismatch')
    if json.loads(info['info/about.json']).get('license') != component['license']:
        raise ScaffoldError('Research license metadata mismatch')
    deps = index.get('depends', [])
    if not isinstance(deps, list) or not all(isinstance(d, str) and d.split() for d in deps):
        raise ScaffoldError('Invalid dependencies')
    if not {'__glibc', 'libgcc', 'libstdcxx', 'libpng', 'libjpeg-turbo', 'libzlib', 'libgomp'} <= {d.split()[0] for d in deps}:
        raise ScaffoldError('Missing runtime dependency')
    license_root = f'share/licenses/{NAME}/'
    required = {f'bin/{component["executable"]}', PREFIX + 'SOURCE.txt', PREFIX + 'upstream.json', PREFIX + 'functional_test.py', PREFIX + 'link-evidence.json', license_root + 'packaging-MIT.txt'}
    required.update(license_root + notice['target'] for notice in component['notices'])
    if required - payload.keys():
        raise ScaffoldError(f'Missing research package files: {sorted(required - payload.keys())}')
    for path in payload:
        if not (path == f'bin/{component["executable"]}' or path.startswith(PREFIX) or path.startswith(license_root)) or any(p in ('.git', '.pixi', '.cache', '__pycache__') for p in PurePosixPath(path).parts):
            raise ScaffoldError(f'Unexpected research payload: {path}')
    expected = {'scope': 'local-research-only', 'candidate_sha256': candidate_sha256, 'original_archive_sha256': PINNED_SHA256, 'excluded_file_count': 59, 'warning': 'No complete corresponding-source offer or license clearance. The original archive was fetched but is not included.'}
    if json.loads(payload[PREFIX + 'upstream.json']) != expected:
        raise ScaffoldError('Research provenance mismatch')
    text = payload[PREFIX + 'SOURCE.txt'].decode()
    if not all(s in text for s in ('LOCAL RESEARCH ONLY', candidate_sha256, PINNED_SHA256, 'original not included', 'No corresponding-source offer')):
        raise ScaffoldError('Research source document mismatch')
    metadata = [p for p in info if p.startswith('info/licenses/')]
    if len(metadata) < len(component['notices']) + 1:
        raise ScaffoldError('Missing metadata license texts')
    digest = '4cf9c190f184019b61c36bcc49d4a24ffeb2a838c6f1690d6c4db14cfb2d0478'
    name = 'IJG-6b-README.txt'
    matches = [info[p] for p in metadata if PurePosixPath(p).name == name]
    if len(matches) != 1 or any(hashlib.sha256(data).hexdigest() != digest for data in [matches[0], payload[license_root + name]]):
        raise ScaffoldError('Modified IJG notice')


def audit(package: Path, candidate: Path) -> dict:
    info, payload = read_package(package)
    verify_metadata(info, payload, sha256(candidate))
    index = json.loads(info['info/index.json'])
    if package.name != f'{NAME}-{index["version"]}-{index["build"]}.conda':
        raise ScaffoldError('Research package filename mismatch')
    binary = payload['bin/PoissonRecon']
    if not binary.startswith(b'\x7fELF') or not shutil.which('patchelf'):
        raise ScaffoldError('ELF binary and patchelf required')
    with tempfile.TemporaryDirectory(prefix='poisson-research-audit-') as directory:
        exe = Path(directory) / 'PoissonRecon'
        exe.write_bytes(binary)
        rpath = subprocess.run(['patchelf', '--print-rpath', str(exe)], text=True, capture_output=True, check=True).stdout.strip()
        needed = subprocess.run(['patchelf', '--print-needed', str(exe)], text=True, capture_output=True, check=True).stdout.splitlines()
        verify_poisson_package_evidence(json.loads(payload[PREFIX + 'link-evidence.json']), needed)
        if any(entry and not (entry in ('$ORIGIN', '${ORIGIN}') or entry.startswith(('$ORIGIN/', '${ORIGIN}/'))) for entry in rpath.split(':')):
            raise ScaffoldError('Non-relocatable RPATH')
    return {'scope': 'local-research-only; not release, legal or complete-source approval', 'package_sha256': sha256(package), 'candidate_sha256': sha256(candidate), 'rpath': rpath, 'needed': needed}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', required=True, type=Path)
    parser.add_argument('--candidate', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(audit(args.package, args.candidate), sort_keys=True, indent=2))


if __name__ == '__main__':
    fail_cli(main)
