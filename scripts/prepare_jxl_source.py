#!/usr/bin/env python3
"""Stage pinned JPEG XL source and locked Cargo crates for a private offline build.

Cargo downloads the crates named in the upstream lock during preparation. The
result is local-only research, not a reviewed corresponding-source bundle.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, sha256
from source_graph import unpack_archive

SOURCE_SHA256 = '8ea589fc559ea7c5dfccb42af4d8148f5db508f5f4d4518328bab5a31fcb268e'
RECIPE = ROOT / 'research/recipes/python-source-research/pillow-jxl-plugin.yaml'


def prepare(archive: Path, destination: Path) -> Path:
    archive, destination = Path(archive), Path(destination)
    if archive.is_symlink() or not archive.is_file() or sha256(archive) != SOURCE_SHA256:
        raise ScaffoldError('JPEG XL source archive checksum mismatch')
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir() or destination.resolve().is_relative_to(ROOT):
        raise ScaffoldError('Unsafe or existing destination')
    try:
        destination.mkdir(mode=0o700)
    except FileExistsError as error:
        raise ScaffoldError('Unsafe or existing destination') from error
    try:
        source=destination/'source'; source.mkdir()
        unpack_archive(archive, source)
        lock=tomllib.loads((source/'Cargo.lock').read_text())
        crates=[x for x in lock['package'] if 'source' in x]
        if not crates or any(x.get('source') != 'registry+https://github.com/rust-lang/crates.io-index' or not re.fullmatch(r'[a-f0-9]{64}',x.get('checksum','')) for x in crates):
            raise ScaffoldError('Unexpected Cargo source or checksum')
        pyproject=source/'pyproject.toml'; text=pyproject.read_text()
        old='features = ["pyo3/extension-module", "vendored"]'
        if text.count(old) != 1:
            raise ScaffoldError('Unexpected maturin feature configuration')
        pyproject.write_text(text.replace(old, 'features = ["pyo3/extension-module", "dynamic"]'))
        with tempfile.TemporaryDirectory(prefix='odm-jxl-cargo-') as home:
            env=os.environ.copy(); env['CARGO_HOME']=home
            result=subprocess.run(['cargo','vendor','--locked','--versioned-dirs','vendor'],cwd=source,env=env,check=True,text=True,stdout=subprocess.PIPE)
        config=tomllib.loads(result.stdout)
        if config.get('source',{}).get('crates-io',{}).get('replace-with') != 'vendored-sources' or config.get('source',{}).get('vendored-sources',{}).get('directory') != 'vendor' or not (source/'vendor').is_dir():
            raise ScaffoldError('Unexpected Cargo vendor configuration')
        expected={f"{item['name']}-{item['version']}": item['checksum'] for item in crates}
        vendor=source/'vendor'
        if len(expected) != len(crates) or {p.name for p in vendor.iterdir()} != set(expected):
            raise ScaffoldError('Unexpected vendored crate set')
        for name, checksum in expected.items():
            path=vendor/name
            if path.is_symlink() or not path.is_dir():
                raise ScaffoldError('Unsafe vendored crate')
            metadata=json.loads((path/'.cargo-checksum.json').read_text())
            if metadata.get('package') != checksum or not isinstance(metadata.get('files'), dict):
                raise ScaffoldError('Vendored crate checksum metadata mismatch')
        (source/'.cargo').mkdir(exist_ok=True)
        (source/'.cargo/config.toml').write_text(result.stdout)
        recipe=destination/'recipe/recipe.yaml'; recipe.parent.mkdir()
        text=RECIPE.read_text()
        begin=text.index('source:\n'); end=text.index('build:\n',begin)
        recipe.write_text(text[:begin]+'source:\n  path: '+json.dumps(str(source.resolve()))+'\n'+text[end:])
        print(f'Prepared {len(crates)} locked registry crates for offline build; no release approval.')
        return destination
    except Exception:
        shutil.rmtree(destination,ignore_errors=True)
        raise


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True,type=Path)
    parser.add_argument('--destination',required=True,type=Path)
    args=parser.parse_args()
    prepare(args.source,args.destination)


if __name__ == '__main__':
    fail_cli(main)
