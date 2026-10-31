#!/usr/bin/env python3
"""Run the private ODM research build on an ephemeral Actions runner.

Never upload the private channel, binaries, source archives, or dataset outputs.
This validates a throwaway bundle; it does not create an owner-retained bundle.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

from common import ScaffoldError, fail_cli, run
from private_odm_bundle import PORT, build

DATASET_URL = 'https://github.com/OpenDroneMap/odm_data_seneca.git'
DATASET_COMMIT = '9220acfdca75cc5e2dd6d27fe48550c5ae0877f2'


def main() -> None:
    print('::notice::ODM private research build: no artifacts will be uploaded or published', flush=True)
    with tempfile.TemporaryDirectory(prefix='odm-private-workflow-') as temporary:
        root = Path(temporary)
        dataset = root / 'seneca'
        run(['git', 'init', str(dataset)])
        run(['git', '-C', str(dataset), 'fetch', '--depth=1', DATASET_URL, DATASET_COMMIT])
        run(['git', '-C', str(dataset), 'checkout', '--detach', 'FETCH_HEAD'])
        actual = subprocess.check_output(['git', '-C', str(dataset), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != DATASET_COMMIT:
            raise ScaffoldError('Unexpected Seneca dataset commit')
        build(root / 'bundle', PORT, dataset)
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with Path(summary).open('a', encoding='utf-8') as stream:
            stream.write('### Private ODM research build\n\n'
                         'Source build, relocated locked replay, Seneca pipeline and raster sanity passed. '
                         'The private bundle, source inputs and outputs were discarded; no artifacts were uploaded. '
                         'This is not release approval or a retained corresponding-source bundle.\n')
    print('::notice::Private ODM source build, replay and Seneca validation passed; outputs discarded', flush=True)


if __name__ == '__main__':
    fail_cli(main)
