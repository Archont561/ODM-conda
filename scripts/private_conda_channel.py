#!/usr/bin/env python3
"""Create a private disposable linux-64 Conda channel from explicit packages.

It never starts a server or publishes anything. Research packages are not
redistributable. The caller is responsible for keeping the directory private.
"""
import argparse
import hashlib
import json
import shutil
import tarfile
import zipfile
from pathlib import Path

import zstandard
from common import ROOT, ScaffoldError, fail_cli, sha256


def create(packages: list[Path], destination: Path, root: Path = ROOT) -> list[dict]:
    destination = Path(destination)
    if destination.exists() or destination.is_symlink() or not destination.parent.is_dir() or destination.resolve().is_relative_to(Path(root).resolve()):
        raise ScaffoldError('Channel destination must be new and outside the repository')
    if not packages:
        raise ScaffoldError('No packages supplied')
    metadata = {}
    paths = []
    for package in map(Path, packages):
        if package.is_symlink() or not package.is_file() or package.suffix != '.conda' or package.name in metadata:
            raise ScaffoldError('Invalid or duplicate local package')
        with zipfile.ZipFile(package) as outer:
            names = outer.namelist()
            infos = [n for n in names if n.startswith('info-') and n.endswith('.tar.zst') and '/' not in n]
            if len(infos) != 1 or len(names) != len(set(names)):
                raise ScaffoldError('Unexpected package info archive')
            with outer.open(infos[0]) as stream, zstandard.ZstdDecompressor().stream_reader(stream) as decompressed:
                with tarfile.open(fileobj=decompressed, mode='r|') as tar:
                    matches = []
                    for member in tar:
                        if member.name == 'info/index.json':
                            if not member.isfile() or member.size > 1024*1024:
                                raise ScaffoldError('Invalid package index')
                            matches.append(json.load(tar.extractfile(member)))
                    if len(matches) != 1:
                        raise ScaffoldError('Missing or duplicate package index')
        index = matches[0]
        if not isinstance(index, dict) or index.get('subdir') != 'linux-64' or not all(isinstance(index.get(k), str) and index[k] for k in ('name','version','build')):
            raise ScaffoldError('Invalid linux-64 package identity')
        if package.name != f"{index['name']}-{index['version']}-{index['build']}.conda":
            raise ScaffoldError('Package filename and index differ')
        digest=sha256(package)
        h=hashlib.md5()
        with package.open('rb') as f:
            for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
        index.update(sha256=digest, md5=h.hexdigest(), size=package.stat().st_size)
        metadata[package.name]=index
        paths.append(package)
    try:
        destination.mkdir(mode=0o700)
    except FileExistsError as error:
        raise ScaffoldError('Channel destination exists') from error
    try:
        for subdir in ('linux-64','noarch'):
            directory=destination/subdir; directory.mkdir(mode=0o700)
            records=metadata if subdir=='linux-64' else {}
            (directory/'repodata.json').write_text(json.dumps({'info':{'subdir':subdir},'packages':{},'packages.conda':records},sort_keys=True))
        for p in paths: shutil.copy2(p,destination/'linux-64'/p.name)
    except Exception:
        shutil.rmtree(destination,ignore_errors=True)
        raise
    return [{'filename':p.name,'sha256':metadata[p.name]['sha256']} for p in paths]


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',type=Path,required=True)
    parser.add_argument('packages',type=Path,nargs='+')
    args=parser.parse_args()
    print(json.dumps(create(args.packages,args.destination),sort_keys=True,indent=2))


if __name__=='__main__': fail_cli(main)
