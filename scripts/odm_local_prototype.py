#!/usr/bin/env python3
"""Prepare and run a local-only ODM fast-orthophoto integration prototype.

This is not an ODM package, source-completeness claim or release approval.
It never invokes SuperBuild and requires an explicitly assembled local prefix.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli
from source_graph import unpack_archive

ODM_SHA256 = '5bdf8fe81b9ca47714e8a474139fd206b8090ac4315c2f530a58fcaef29cde5e'
PATCH_SHA256 = '75ad974f29432f15a53407fba5e3ce8261e973b302b622f8d09e534747ebfe69'
PATCH = ROOT / 'research/patches/odm-prefix-prototype.patch'
# Critical startup imports only; successful imports do not establish a complete ABI.
STARTUP_IMPORTS = ('opensfm', 'opensfm.pygeometry', 'osgeo.gdal', 'cv2', 'numpy',
                   'scipy', 'rasterio', 'pdal', 'yaml', 'pyproj', 'PIL', 'vmem')
REQUIRED_TOOLS = ('python', 'opensfm', 'FPCFilter', 'PoissonRecon', 'ReconstructMesh',
                  'dem2points', 'renderdem', 'fastrasterfilter', 'texrecon', 'odm_orthophoto',
                  'pdal', 'gdal_translate', 'gdalwarp', 'gdaladdo', 'gdalbuildvrt', 'gdaldem', 'exiftool')


class PrototypeError(ScaffoldError):
    """Invalid local-only prototype inputs."""


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def check_prefix(prefix: Path) -> None:
    root = prefix.resolve()
    if not root.is_dir():
        raise PrototypeError(f'Prefix is not a directory: {root}')
    missing = []
    for name in REQUIRED_TOOLS:
        path = root / 'bin' / name
        if not path.exists() or not path.is_file() or not os.access(path, os.X_OK):
            missing.append(name)
        elif not path.resolve().is_relative_to(root):
            raise PrototypeError(f'Executable resolves outside the prefix: {name}')
    if missing:
        raise PrototypeError('Prefix missing required executables: ' + ', '.join(missing))


def check_imports(prefix: Path) -> None:
    # Probe the prefix interpreter in a separate process, without ambient user modules.
    code = (
        "import importlib, os, sys; "
        "assert os.path.realpath(sys.prefix) == os.path.realpath(sys.argv[1]), "
        "'interpreter does not belong to the supplied prefix'; "
        "[importlib.import_module(name) for name in sys.argv[2:]]"
    )
    env = os.environ.copy()
    env.pop('PYTHONPATH', None)
    env.pop('PYTHONHOME', None)
    env['PATH'] = str(prefix / 'bin') + os.pathsep + os.defpath
    result = subprocess.run([str(prefix / 'bin/python'), '-s', '-E', '-c', code,
                             str(prefix), *STARTUP_IMPORTS], env=env,
                            text=True, capture_output=True)
    if result.returncode:
        raise PrototypeError('Prefix Python import probe failed: ' + result.stderr.strip())


def prepare(archive: Path, destination: Path) -> None:
    if archive.is_symlink() or not archive.is_file() or digest(archive) != ODM_SHA256:
        raise PrototypeError('ODM source archive SHA256 does not match the pinned reference')
    if PATCH.is_symlink() or not PATCH.is_file() or digest(PATCH) != PATCH_SHA256:
        raise PrototypeError('ODM local prototype patch checksum mismatch')
    if destination.exists() or destination.is_symlink():
        raise PrototypeError('Destination already exists; choose a fresh directory')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.odm-local-', dir=destination.parent) as temp:
        tree = Path(temp) / 'app'
        tree.mkdir()
        unpack_archive(archive, tree)
        result = subprocess.run(['patch', '--batch', '--fuzz=0', '-p1', '-i', str(PATCH)],
                                cwd=tree, text=True, capture_output=True)
        if result.returncode:
            raise PrototypeError(f'Failed to apply exact local prototype patch: {result.stderr or result.stdout}')
        (tree / 'LOCAL-ONLY.txt').write_text(
            'Research only. No release or redistribution approval. Not a complete ODM package.\n', encoding='utf-8')
        tree.rename(destination)


def run_local(app: Path, prefix: Path, args: list[str]) -> int:
    app = app.resolve()
    prefix = prefix.resolve()
    if not (app / 'LOCAL-ONLY.txt').is_file() or not (app / 'run.py').is_file():
        raise PrototypeError('App must be an explicitly prepared local prototype')
    if '--fast-orthophoto' not in args:
        raise PrototypeError('Prototype only supports an explicit --fast-orthophoto invocation')
    if any(arg == flag or arg.startswith(flag + '=') for arg in args for flag in ('--pc-classify', '--split')):
        raise PrototypeError('Point classification and split/merge are outside this prototype scope')
    check_prefix(prefix)
    check_imports(prefix)
    env = os.environ.copy()
    env.pop('PYTHONPATH', None)
    env.pop('PYTHONHOME', None)
    env['PYTHONNOUSERSITE'] = '1'
    env['ODM_CONDA_LOCAL_PREFIX'] = str(prefix)
    # PDAL/GDAL must use the selected prefix's coordinate database, not an
    # ambient activation or their build-time default. PROJ_LIB is for older PROJ.
    env['PROJ_DATA'] = env['PROJ_LIB'] = str(prefix / 'share/proj')
    env['PATH'] = str(prefix / 'bin') + os.pathsep + os.defpath
    return subprocess.run([str(prefix / 'bin/python'), '-s', '-E', str(app / 'run.py'), *args], env=env).returncode


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    stage = sub.add_parser('prepare', help='Unpack and patch the exact pinned ODM archive')
    stage.add_argument('--archive', type=Path, required=True)
    stage.add_argument('--output', type=Path, required=True)
    preflight = sub.add_parser('check', help='Check explicitly supplied prefix executables')
    preflight.add_argument('--prefix', type=Path, required=True)
    preflight.add_argument('--imports', action='store_true', help='also execute a partial Python import probe')
    launch = sub.add_parser('run', help='Run experimental fast-orthophoto with an assembled prefix')
    launch.add_argument('--app', type=Path, required=True)
    launch.add_argument('--prefix', type=Path, required=True)
    launch.add_argument('odm_args', nargs=argparse.REMAINDER)
    options = parser.parse_args()
    if options.action == 'prepare':
        prepare(options.archive, options.output)
        print(f'Prepared local-only ODM prototype at {options.output}; no build or release validation implied')
    elif options.action == 'check':
        check_prefix(options.prefix)
        if options.imports:
            check_imports(options.prefix.resolve())
        print('PASS: required executable paths exist inside the prefix' +
              ('; selected Python imports passed' if options.imports else '; imports not checked') +
              '; complete ABI and runtime coverage are not checked')
    else:
        args = options.odm_args
        if args and args[0] == '--':
            args = args[1:]
        raise SystemExit(run_local(options.app, options.prefix, args))


if __name__ == '__main__':
    fail_cli(main)
