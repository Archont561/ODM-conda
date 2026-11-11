#!/usr/bin/env python3
"""Stage a hash-verified, incomplete private JPEG XL crate-notice draft.

This is not a package audit, legal analysis, corresponding-source offer, or
permission to redistribute. Other notices and inputs require separate review.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, sha256

INVENTORY = ROOT/'research/pillow-jxl-locked-crates-2026-11-11.json'
INVENTORY_SHA256 = '21b48b27922396dd9f342d1e3504b0f2be1c1f015ed81c3a48c307973ba0373e'
COUNT = 40
NESTED = {
    'pyo3-0.25.1/pyo3-runtime/LICENSE-APACHE': '32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9',
    'pyo3-0.25.1/pyo3-runtime/LICENSE-MIT': 'afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6',
}


def stage(vendor: Path, destination: Path) -> dict:
    vendor, destination = Path(vendor), Path(destination)
    if (vendor.is_symlink() or not vendor.is_dir() or vendor.resolve().is_relative_to(ROOT)
            or destination.exists() or destination.is_symlink() or not destination.parent.is_dir()
            or destination.resolve().is_relative_to(ROOT) or destination.resolve().is_relative_to(vendor.resolve())):
        raise ScaffoldError('Unsafe vendor or destination')
    if sha256(INVENTORY) != INVENTORY_SHA256:
        raise ScaffoldError('Unexpected pinned crate notice inventory')
    entries = json.loads(INVENTORY.read_text())['crates']
    if len(entries) != COUNT:
        raise ScaffoldError('Unexpected crate count')
    requested = {}
    crate_names = set()
    for entry in entries:
        name, version = entry['name'], entry['version']
        if not re.fullmatch(r'[A-Za-z0-9_-]+', name) or not re.fullmatch(r'[A-Za-z0-9.+_-]+', version):
            raise ScaffoldError('Unsafe crate identity')
        crate = f'{name}-{version}'
        if crate in crate_names:
            raise ScaffoldError('Duplicate crate identity')
        crate_names.add(crate)
        directory=vendor/crate
        if directory.is_symlink() or not directory.is_dir(): raise ScaffoldError(f'Missing or unsafe crate: {crate}')
        checksum=directory/'.cargo-checksum.json'
        if checksum.is_symlink() or not checksum.is_file() or json.loads(checksum.read_text()).get('package') != entry['sha256']:
            raise ScaffoldError(f'Unexpected package checksum metadata: {crate}')
        for name, digest in entry['notice_sha256'].items():
            if not re.fullmatch(r'[A-Za-z0-9_.-]+', name) or not re.fullmatch(r'[0-9a-f]{64}', digest):
                raise ScaffoldError('Unsafe notice metadata')
            requested[f'{crate}/{name}'] = digest
    if {p.name for p in vendor.iterdir()} != crate_names:
        raise ScaffoldError('Unexpected vendored crate set')
    requested.update(NESTED)
    for name, digest in requested.items():
        path=vendor/name
        if any(part.is_symlink() for part in (path, *list(path.parents)[:len(Path(name).parts)-1])) or not path.is_file() or sha256(path)!=digest:
            raise ScaffoldError(f'Missing, unsafe or modified notice: {name}')
    try:
        destination.mkdir(mode=0o700)
    except FileExistsError as error:
        raise ScaffoldError('Unsafe or existing destination') from error
    try:
        for name, digest in sorted(requested.items()):
            target=destination/name; target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(vendor/name, target)
            if sha256(target) != digest: raise ScaffoldError(f'Notice changed during copy: {name}')
        manifest={'scope':'private-incomplete-research-notices', 'inventory_sha256': INVENTORY_SHA256,
                  'files':dict(sorted(requested.items())),
                  'warning':'Filename-limited crate notices only; not a complete notice package or distribution approval.'}
        (destination/'MANIFEST.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
        return manifest
    except Exception:
        shutil.rmtree(destination,ignore_errors=True)
        raise


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vendor',required=True,type=Path)
    parser.add_argument('--destination',required=True,type=Path)
    args=parser.parse_args()
    manifest=stage(args.vendor,args.destination)
    print(f"Private incomplete notice draft: {len(manifest['files'])} files; manifest SHA256 {sha256(args.destination/'MANIFEST.json')}; not release approved")


if __name__ == '__main__': fail_cli(main)
