#!/usr/bin/env python3
"""Create a local-only JPEG XL research source candidate without test images.

The original sdist, test assets, crate sources and rights remain separate
questions. This is not a corresponding-source offer or publication approval.
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import tarfile
import tempfile
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, sha256
from prepare_jxl_source import SOURCE_SHA256
from source_bundle import add_bytes
from source_graph import unpack_archive

EXCLUDED = {
    'bench.png': 'a74a88ae0b2036643d1a85182aae3c47bb49f5ee941037e41536237f4053326b',
    'icc_profile/62AHB.jpg': 'ad27c0fc339b543f9e992024a77e6625d754df9b0687e7f8f03cad03ad070099',
    'icc_profile/62AHB.jxl': '033d2501abe9e4c16107eb3b74cbe1e7e6f88cb449fa514d9c2968b120d2de08',
    'metadata/1x1_exif_xmp.jpg': 'c6d30276e37711069950d50b8d8c94c037f5b7a1fdcc36235c6f3f066487bed8',
    'metadata/1x1_exif_xmp.jpg.jxl': '470386429a5af0781337c1b08e345fe2ba44ab50249c076f4f5453377e4eee9f',
    'metadata/1x1_exif_xmp.png': '52c778cae7b176e04c5531fcceddc9cb28725891f50b5a99d6bc23c66e6a3958',
    'metadata/1x1_exif_xmp.png.jxl': 'e74a4f086e95d299cd24df4f8cbe77ba866f229b248e0598a6e18145b512f8c7',
    'metadata/sample.exif': '6c85b7a3c972ddac708067f17754d1ff2260432dc36a58f4c34490fce72ab6fc',
    'metadata/sample.xmp': '6647f7dc147d3f05ec79854c2201993da53aa21499c57e1bcb983c3cb9ef8cc0',
    'sample.jpg': 'd28d532e12cc86acc4a612912b37e78de830aee23ecbf9734b631e46a89444c9',
    'sample.jxl': '2e57ec4687a6dc53c1e3fb9a167a40f753a538647a6ae50cfc59415e9b4a3773',
    'sample.png': '8d94300d85be24c7e5e743d775cae82ac8ffe69d5a35b461d95b52d923bff349',
    'sample_float.jxl': '647557c6a5d4e8018a3ff3e54a862b6e930b164b57d7c92ade313878c771fb5e',
    'sample_float.ppm': 'f264c3d80009b52dcf9e6b2730266a01e1cf7c3b88b24ad00205bb7cef8e3343',
    'sample_grey.jxl': '794908a4ab2c147b96b01d9db726fe051dab5194cc405a3fe8b453449ff9918d',
    'sample_grey.png': 'cb892870b00170f2bb6d202070686f0e88546b7c080df06d2e31d7980661db29',
}
README_SHA256 = '613fefef533c1552bcf0f013768a21625db3d7468126344a8245879964691057'


def make_candidate(source: Path, destination: Path) -> dict:
    source, destination = Path(source), Path(destination)
    if source.is_symlink() or not source.is_file() or sha256(source) != SOURCE_SHA256:
        raise ScaffoldError('Unexpected JPEG XL source archive')
    if (destination.exists() or destination.is_symlink() or not destination.parent.is_dir()
            or destination.resolve().is_relative_to(ROOT)):
        raise ScaffoldError('Unsafe or existing destination')
    with tempfile.TemporaryDirectory(prefix='jxl-reduced-', dir=destination.parent) as temp:
        tree = Path(temp)/'tree'; tree.mkdir()
        unpack_archive(source, tree)
        image_root = tree/'test/images'
        if image_root.is_symlink() or not image_root.is_dir():
            raise ScaffoldError('Missing test images directory')
        files = {}
        for path in sorted(image_root.rglob('*')):
            if path.is_symlink() or not (path.is_file() or path.is_dir()):
                raise ScaffoldError('Unexpected test image member')
            if path.is_file(): files[path.relative_to(image_root).as_posix()] = sha256(path)
        expected = EXCLUDED | {'README.md': README_SHA256}
        if files != expected: raise ScaffoldError('Test image set or digest differs from pinned source')
        for name in EXCLUDED: (image_root/name).unlink()
        retained = {}
        for path in sorted(tree.rglob('*')):
            if path.is_symlink() or not (path.is_dir() or path.is_file()): raise ScaffoldError('Unsupported source member')
            if path.is_file(): retained[path.relative_to(tree).as_posix()] = {'sha256': sha256(path), 'mode': f'{path.stat().st_mode & 0o777:04o}'}
        if 'CANDIDATE-MANIFEST.json' in retained: raise ScaffoldError('Unexpected source manifest')
        manifest = {'scope': 'local-research-only', 'original_archive_sha256': SOURCE_SHA256,
                    'excluded_files': {'test/images/'+k:v for k,v in EXCLUDED.items()}, 'files': retained,
                    'warning': 'Not corresponding source; original sdist, test rights, crate sources and distribution obligations remain unresolved.'}
        try:
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as error:
            raise ScaffoldError('Unsafe or existing destination') from error
        try:
            with os.fdopen(fd, 'wb') as output, gzip.GzipFile(filename='', mode='wb', fileobj=output, mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode='w', format=tarfile.PAX_FORMAT) as archive:
                    for name, info in retained.items():
                        add_bytes(archive, 'source/'+name, (tree/name).read_bytes(), int(info['mode'], 8))
                    add_bytes(archive, 'source/CANDIDATE-MANIFEST.json', (json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode())
        except Exception:
            destination.unlink(missing_ok=True)
            raise
    return manifest


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=make_candidate(args.source,args.output)
    print(f"Local-only candidate SHA256 {sha256(args.output)}; excluded {len(result['excluded_files'])} test files; not a source offer")


if __name__ == '__main__': fail_cli(main)
