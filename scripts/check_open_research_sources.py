#!/usr/bin/env python3
"""Check exact research archives before local research builds, without bundling."""
import argparse
import urllib.request
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, fetch_pinned_archive
from opensfm_graph_policy import PRIMARY, PYBIND11, VMEM, verify_opensfm_archives, verify_vmem_archive
from source_bundle import graph_archives
from stage_sources import load_plan


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('component', choices=('openmvs', 'opensfm'))
    parser.add_argument('--cache', type=Path, default=ROOT / '.cache/sources')
    args = parser.parse_args()
    if args.component == 'opensfm':
        primary = fetch_pinned_archive(PRIMARY['name'], PRIMARY, args.cache)
        dependency = fetch_pinned_archive(PYBIND11['name'], PYBIND11, args.cache)
        verify_opensfm_archives(primary, dependency)
        args.cache.mkdir(parents=True, exist_ok=True)
        archive = args.cache / 'vmem-1.0.2.tar.gz'
        if archive.is_symlink():
            raise ScaffoldError('Refusing symlinked vmem cache entry')
        if not archive.exists():
            request = urllib.request.Request(VMEM['url'], headers={'User-Agent': 'ODM-conda-research/1'})
            with urllib.request.urlopen(request, timeout=90) as response:
                if not response.url.startswith('https://'):
                    raise ScaffoldError('vmem download redirected away from HTTPS')
                data = response.read(10 * 1024 * 1024 + 1)
            if len(data) > 10 * 1024 * 1024:
                raise ScaffoldError('vmem archive exceeds size limit')
            archive.write_bytes(data)
        verify_vmem_archive(archive)
    else:
        plan = load_plan(ROOT / 'research/source-graphs.json', 'openmvs')
        graph_archives('openmvs-odm', {**plan['primary'], 'additional_sources': plan['additional'],
                                       'disabled_build_trees': []}, args.cache)
    print('PASS: pinned research archives scanned; no distribution or network-isolation approval implied')


if __name__ == '__main__':
    fail_cli(main)
