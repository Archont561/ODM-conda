#!/usr/bin/env python3
"""Install a CPU dense ODM research launcher; not a production package."""
import os
import shutil
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli


def install(source: Path, prefix: Path) -> None:
    source, prefix = Path(source).resolve(), Path(prefix).resolve()
    if source == prefix or not source.is_dir() or not prefix.is_dir():
        raise ScaffoldError('Invalid source or prefix')
    if not (source/'run.py').is_file() or not (source/'VERSION').is_file() or not (source/'opendm/context.py').is_file() or 'ODM_CONDA_LOCAL_PREFIX' not in (source/'opendm/context.py').read_text() or not (source/'opendm/ai.py').is_file() or 'ODM_CONDA_MODEL_ROOT' not in (source/'opendm/ai.py').read_text():
        raise ScaffoldError('Missing patched ODM application')
    if any(path.is_symlink() for path in source.rglob('*')):
        raise ScaffoldError('Unexpected symlink in ODM source')
    destination = prefix/'share/odm-conda/odm-dense-research'
    launcher = prefix/'bin/odm-dense-research'
    if destination.exists() or destination.is_symlink() or launcher.exists() or launcher.is_symlink():
        raise ScaffoldError('Research package destination exists')
    destination.mkdir(parents=True)
    try:
        shutil.copytree(source, destination/'app', ignore=shutil.ignore_patterns(
            '.source_info.json', 'build_env.sh', 'conda_build.sh', 'conda_build.log', '__pycache__', '*.pyc'))
        shutil.copy2(ROOT/'scripts/odm_research_merge.py', destination/'app/opendm/conda_research_merge.py')
        (destination/'app/LOCAL-ONLY.txt').write_text('Private CPU dense research only; not release or redistribution approval.\n')
        for name in ('odm_dense_research_launcher.py', 'odm_local_prototype.py', 'common.py', 'source_graph.py'):
            shutil.copy2(ROOT/'scripts'/name, destination/name)
        launcher.parent.mkdir(parents=True, exist_ok=True)
        launcher.write_text('''#!/bin/sh
set -eu
prefix=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
exec "$prefix/bin/python" -s -E "$prefix/share/odm-conda/odm-dense-research/odm_dense_research_launcher.py" "$prefix" "$@"
''')
        launcher.chmod(0o755)
    except Exception:
        launcher.unlink(missing_ok=True)
        shutil.rmtree(destination, ignore_errors=True)
        raise


def main():
    if not os.environ.get('SRC_DIR') or not os.environ.get('PREFIX'):
        raise ScaffoldError('Missing rattler-build source or prefix')
    install(Path(os.environ['SRC_DIR']), Path(os.environ['PREFIX']))


if __name__ == '__main__':
    fail_cli(main)
