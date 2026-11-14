#!/usr/bin/env python3
"""Restricted CPU dense research entrypoint; not full ODM or a security boundary."""
import hashlib
import os
import subprocess
import sys
from pathlib import Path

from common import ScaffoldError, fail_cli
from odm_local_prototype import check_imports, check_prefix

# Selected obvious unsupported options; upstream aliases and indirect option
# effects are not comprehensively enumerated. Never treat as a security guard.
MODEL_SHA256 = '2960ef1036bb66c42ec908fb5160f396062a9baf5a7ca9a08ba4644976d798c2'

UNSUPPORTED = ('--fast-orthophoto', '--pc-rectify', '--dtm',
               '--split', '--sm-cluster', '--3d-tiles', '--pc-ept', '--pc-copc')


def validate_args(args: list[str]) -> None:
    if any(arg == flag or arg.startswith(flag+'=') for arg in args for flag in UNSUPPORTED):
        raise ScaffoldError('Requested option is outside CPU dense research scope')


def checked_model_root(value: str) -> Path:
    root = Path(value)
    if not value or not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise ScaffoldError('Classification requires an absolute private model directory')
    parts = [root/'openpointclass', root/'openpointclass/v1_0_0', root/'openpointclass/v1_0_0/model.bin']
    if any(p.is_symlink() for p in parts) or not parts[-1].is_file() or not parts[-1].resolve().is_relative_to(root.resolve()):
        raise ScaffoldError('Missing or unsafe research classification model')
    if parts[-1].stat().st_size > 10_000_000 or hashlib.sha256(parts[-1].read_bytes()).hexdigest() != MODEL_SHA256:
        raise ScaffoldError('Research classification model hash mismatch')
    return root.resolve()


def launch(prefix: Path, args: list[str]) -> int:
    validate_args(args)
    prefix = prefix.resolve()
    app = prefix/'share/odm-conda/odm-dense-research/app'
    if not (app/'LOCAL-ONLY.txt').is_file() or not (app/'run.py').is_file():
        raise ScaffoldError('Missing private dense research app')
    check_prefix(prefix)
    classification = '--pc-classify' in args
    model_root = checked_model_root(os.environ.get('ODM_RESEARCH_MODEL_ROOT', '')) if classification else None
    tools = ('DensifyPointCloud', 'dem2mesh', 'pcclassify') if classification else ('DensifyPointCloud', 'dem2mesh')
    for name in tools:
        path = prefix/'bin'/name
        if not path.is_file() or not os.access(path, os.X_OK) or not path.resolve().is_relative_to(prefix):
            raise ScaffoldError(f'Missing or external research executable: {name}')
    check_imports(prefix)
    env = os.environ.copy()
    for key in ('PYTHONPATH', 'PYTHONHOME', 'LD_LIBRARY_PATH', 'DYLD_LIBRARY_PATH'):
        env.pop(key, None)
    env.pop('ODM_CONDA_MODEL_ROOT', None)
    if model_root is not None:
        env['ODM_CONDA_MODEL_ROOT'] = str(model_root)
    env['PYTHONNOUSERSITE'] = '1'
    env['ODM_NO_GPU'] = '1'
    env['ODM_CONDA_LOCAL_PREFIX'] = str(prefix)
    env['PROJ_DATA'] = env['PROJ_LIB'] = str(prefix/'share/proj')
    env['PATH'] = str(prefix/'bin') + os.pathsep + os.defpath
    return subprocess.run([str(prefix/'bin/python'), '-s', '-E', str(app/'run.py'), '--no-gpu', *args], env=env).returncode


def main():
    if len(sys.argv) < 2:
        raise ScaffoldError('Missing research prefix')
    raise SystemExit(launch(Path(sys.argv[1]), sys.argv[2:]))


if __name__ == '__main__':
    fail_cli(main)
