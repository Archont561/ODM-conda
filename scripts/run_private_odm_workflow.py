#!/usr/bin/env python3
"""Run the private ODM research build on an ephemeral Actions runner.

Never upload the private channel, binaries, source archives, or dataset outputs.
This validates a throwaway bundle; it does not create an owner-retained bundle.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path

from common import ScaffoldError, fail_cli, run, sha256
from private_odm_bundle import PORT, build

DATASET_URL = 'https://github.com/OpenDroneMap/odm_data_seneca.git'
DATASET_COMMIT = '9220acfdca75cc5e2dd6d27fe48550c5ae0877f2'
CRATE_URL = 'https://static.crates.io/crates/jpegxl-src/jpegxl-src-0.11.2.crate'
CRATE_LIMIT = 128 * 1024 * 1024


def download_crate(destination: Path) -> None:
    """Fetch the pinned crate only into the disposable private runner directory."""
    from prepare_jxl_vendor_scope import CRATE_SHA256
    request = urllib.request.Request(CRATE_URL, headers={'User-Agent': 'ODM-conda-private-research/1'})
    with urllib.request.urlopen(request, timeout=90) as response, destination.open('xb') as output:
        final = urllib.parse.urlsplit(response.url)
        if final.scheme != 'https' or final.hostname != 'static.crates.io' or final.username or final.password:
            raise ScaffoldError('Unexpected crate download redirect')
        size = 0
        while block := response.read(1024 * 1024):
            size += len(block)
            if size > CRATE_LIMIT:
                raise ScaffoldError('JPEG XL crate exceeds download limit')
            output.write(block)
    if sha256(destination) != CRATE_SHA256:
        raise ScaffoldError('JPEG XL crate checksum mismatch')


def main() -> None:
    variant = os.environ.get('ODM_OPENMVS_VARIANT', 'historical')
    if variant not in ('historical', 'tetraflow'):
        raise ScaffoldError('Unknown OpenMVS research variant')
    print(f'::notice::ODM private research build ({variant}): no artifacts will be uploaded or published', flush=True)
    with tempfile.TemporaryDirectory(prefix='odm-private-workflow-') as temporary:
        root = Path(temporary)
        dataset = root / 'seneca'
        run(['git', 'init', str(dataset)])
        run(['git', '-C', str(dataset), 'fetch', '--depth=1', DATASET_URL, DATASET_COMMIT])
        run(['git', '-C', str(dataset), 'checkout', '--detach', 'FETCH_HEAD'])
        actual = subprocess.check_output(['git', '-C', str(dataset), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != DATASET_COMMIT:
            raise ScaffoldError('Unexpected Seneca dataset commit')
        if variant == 'tetraflow':
            crate = root / 'jpegxl-src-0.11.2.crate'
            download_crate(crate)
            build(root / 'bundle', PORT, dataset, runtime_profile='reduced', reduced_jxl=True,
                  vendor_scope_crate=crate, openmvs_variant='tetraflow')
        else:
            build(root / 'bundle', PORT, dataset)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with Path(summary).open('a', encoding='utf-8') as stream:
            stream.write(f'### Private ODM research build ({variant})\n\n'
                         'Source build, relocated locked replay, Seneca pipeline and raster sanity passed. '
                         'The private bundle, source inputs and outputs were discarded; no artifacts were uploaded. '
                         'This is not release approval or a retained corresponding-source bundle.\n')
    print('::notice::Private ODM source build, replay and Seneca validation passed; outputs discarded', flush=True)


if __name__ == '__main__':
    fail_cli(main)
