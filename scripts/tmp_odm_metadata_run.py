#!/usr/bin/env python3
"""Temporary hosted test: export only explicitly selected ODM metadata."""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from common import run
from private_odm_bundle import PORT, build, verify
from run_private_odm_workflow import DATASET_URL, DATASET_COMMIT

FILES = ('pixi.toml', 'pixi.lock', 'conda-inventory.json', 'private-bundle.json')


def main():
    result = Path(os.environ['RUNNER_TEMP']) / 'odm-metadata'
    result.mkdir(mode=0o700)
    with tempfile.TemporaryDirectory(prefix='odm-metadata-run-', dir=os.environ['RUNNER_TEMP']) as scratch:
        root = Path(scratch)
        dataset = root/'seneca'
        run(['git', 'init', str(dataset)])
        run(['git', '-C', str(dataset), 'fetch', '--depth=1', DATASET_URL, DATASET_COMMIT])
        run(['git', '-C', str(dataset), 'checkout', '--detach', 'FETCH_HEAD'])
        commit = subprocess.check_output(['git', '-C', str(dataset), 'rev-parse', 'HEAD'], text=True).strip()
        if commit != DATASET_COMMIT:
            raise RuntimeError('Unexpected dataset commit')
        bundle = root/'bundle'
        build(bundle, PORT, dataset)
        verify(bundle)
        for name in FILES:
            src = bundle/name
            if src.is_symlink() or not src.is_file() or src.stat().st_size > 4*1024*1024:
                raise RuntimeError(f'Unexpected metadata file: {name}')
            shutil.copyfile(src, result/name)
        if {p.name for p in result.iterdir()} != set(FILES):
            raise RuntimeError('Unexpected export file')
        inventory = json.loads((result/'conda-inventory.json').read_text())
        count = len(inventory['packages'])
        def digest(name):
            return hashlib.sha256((result/name).read_bytes()).hexdigest()
        checksums = ''.join(f'{digest(name)}  {name}\n' for name in FILES)
        (result/'SHA256SUMS').write_text(checksums)
        with Path(os.environ['GITHUB_OUTPUT']).open('a') as output:
            output.write(f'lock_sha256={digest("pixi.lock")}\n')
            output.write(f'manifest_sha256={digest("private-bundle.json")}\n')
            output.write(f'inventory_sha256={digest("conda-inventory.json")}\n')
            output.write(f'package_count={count}\n')
        with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a') as summary:
            summary.write('### ODM research metadata\n\n')
            summary.write(f'- Conda package records: {count}\n- Lock SHA256: `{digest("pixi.lock")}`\n')
            summary.write(f'- Bundle manifest SHA256: `{digest("private-bundle.json")}`\n')
            summary.write('- Metadata only; the private packages and all source and imagery were discarded.\n')
        print(f'::notice::ODM metadata ready; {count} Conda records; lock SHA256 {digest("pixi.lock")}')


if __name__ == '__main__':
    main()
