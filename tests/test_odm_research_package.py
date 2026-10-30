"""The local-only ODM package must stay relocatable and fail closed."""
import os
from pathlib import Path
import subprocess

import pytest


def test_installs_relocatable_local_candidate(tmp_path):
    from build_odm_research import install

    source = tmp_path / 'source'
    source.mkdir()
    (source / 'run.py').write_text('print("not invoked")\n')
    (source / 'VERSION').write_text('3.6.2\n')
    (source / 'build_env.sh').write_text('do not package build environment')
    (source / 'opendm').mkdir()
    (source / 'opendm/context.py').write_text('ODM_CONDA_LOCAL_PREFIX\n')
    prefix = tmp_path / 'prefix'
    prefix.mkdir()
    install(source, prefix)
    app = prefix / 'share/odm-conda/odm-fast-research/app'
    assert (app / 'VERSION').read_text() == '3.6.2\n'
    assert (app / 'LOCAL-ONLY.txt').exists()
    assert not (app / 'build_env.sh').exists()
    launcher = prefix / 'bin/odm-fast-research'
    assert os.access(launcher, os.X_OK)
    # A moved prefix is resolved at invocation, not embedded at build time.
    moved = tmp_path / 'moved prefix'
    prefix.rename(moved)
    bindir = moved / 'bin'
    (bindir / 'python').symlink_to(Path(__import__('sys').executable))
    result = subprocess.run([str(bindir / 'odm-fast-research'), 'dataset'], text=True, capture_output=True)
    assert result.returncode != 0
    assert 'fast-orthophoto' in result.stderr
    assert str(prefix) not in (bindir / 'odm-fast-research').read_text()


def test_refuses_unpatched_source_and_existing_destination(tmp_path):
    from build_odm_research import install
    from common import ScaffoldError

    source = tmp_path / 'src'; source.mkdir()
    (source / 'run.py').touch(); (source / 'VERSION').touch()
    (source / 'opendm').mkdir(); (source / 'opendm/context.py').write_text('unpatched')
    prefix = tmp_path / 'prefix'; prefix.mkdir()
    with pytest.raises(ScaffoldError, match='patched'):
        install(source, prefix)
    (source / 'opendm/context.py').write_text('ODM_CONDA_LOCAL_PREFIX')
    (prefix / 'share/odm-conda/odm-fast-research').mkdir(parents=True)
    with pytest.raises(ScaffoldError, match='exists'):
        install(source, prefix)


def test_rejects_source_symlinks(tmp_path):
    from build_odm_research import install
    from common import ScaffoldError

    source = tmp_path / 'src'; source.mkdir()
    (source / 'run.py').touch(); (source / 'VERSION').touch()
    (source / 'opendm').mkdir(); (source / 'opendm/context.py').write_text('ODM_CONDA_LOCAL_PREFIX')
    (source / 'untrusted-link').symlink_to('/etc/passwd')
    prefix = tmp_path / 'prefix'; prefix.mkdir()
    with pytest.raises(ScaffoldError, match='symlink'):
        install(source, prefix)


def test_packaged_patch_matches_validated_prototype():
    from common import ROOT
    from odm_local_prototype import PATCH, PATCH_SHA256, digest

    recipe_patch = ROOT / 'research/recipes/odm-fast-research/patches/0001-prefix.patch'
    assert digest(PATCH) == PATCH_SHA256
    assert digest(recipe_patch) == PATCH_SHA256
