"""Local-only reduced-tree transformation behavior; no rights conclusions."""
from pathlib import Path

import pytest

from common import ScaffoldError


def make_tree(path: Path) -> None:
    files = {
        'LICENSE': 'root license',
        'COPYRIGHT.md': 'copyright',
        '_external/vcg/LICENSE.txt': 'vcg',
        '_external/eigen/COPYING.MPL2': 'eigen',
        '_external/eigen/COPYING.README': 'eigen readme',
        'libs/MVS/SceneReconstruct.cpp': 'reconstruct',
        'libs/MVS/SceneDensify.cpp': 'densify',
        'libs/MVS/SceneRefine.cpp': 'refine',
        'libs/MVS/SceneTexture.cpp': 'texture',
        **{f'libs/Math/{d}/file{i}.txt': f'{d}{i}' for d in ('IBFS', 'TRWS') for i in range(10)},
    }
    for name, content in files.items():
        target = path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)


def test_reduction_copies_only_retained_files_with_deterministic_manifest(tmp_path, monkeypatch):
    import openmvs_reduced_tree as reducer

    source = tmp_path / 'source'
    make_tree(source)
    monkeypatch.setattr(reducer, 'verify_openmvs_tree', lambda tree, research: None)
    monkeypatch.setattr(reducer, 'EXPECTED_REDUCED_TREE', None)
    a, b = tmp_path / 'a', tmp_path / 'b'
    first = reducer.make_reduced_tree(source, a)
    second = reducer.make_reduced_tree(source, b)
    assert first == second
    assert first['retained_count'] == 6
    assert 'libs/MVS/SceneReconstruct.cpp' in first['files']
    assert (a / 'LICENSE').read_text() == 'root license'
    assert not (a / 'libs/Math/IBFS').exists()
    assert not (a / 'libs/Math/TRWS').exists()
    assert not (a / 'libs/MVS/SceneDensify.cpp').exists()
    assert (source / 'libs/Math/IBFS/file0.txt').exists()
    assert not (a / '.source_info.json').exists()


def test_rejects_unverified_tree_and_existing_destination(tmp_path, monkeypatch):
    import openmvs_reduced_tree as reducer

    source = tmp_path / 'source'
    make_tree(source)
    destination = tmp_path / 'output'
    def reject(tree, research):
        raise ScaffoldError('Unrecognized OpenMVS source tree fingerprint')
    monkeypatch.setattr(reducer, 'verify_openmvs_tree', reject)
    with pytest.raises(ScaffoldError, match='fingerprint'):
        reducer.make_reduced_tree(source, destination)
    assert not destination.exists()
    destination.mkdir()
    (destination / 'keep').write_text('original')
    with pytest.raises(ScaffoldError, match='existing'):
        reducer.make_reduced_tree(source, destination)
    assert (destination / 'keep').read_text() == 'original'


def test_fingerprint_mismatch_cleans_destination_and_keeps_source(tmp_path, monkeypatch):
    import openmvs_reduced_tree as reducer

    source = tmp_path / 'source'
    make_tree(source)
    destination = tmp_path / 'output'
    monkeypatch.setattr(reducer, 'verify_openmvs_tree', lambda tree, research: None)
    with pytest.raises(ScaffoldError, match='reduced source fingerprint'):
        reducer.make_reduced_tree(source, destination)
    assert not destination.exists()
    assert (source / 'libs/Math/TRWS/file0.txt').is_file()


def test_symlink_and_nested_destination_are_rejected(tmp_path, monkeypatch):
    import openmvs_reduced_tree as reducer

    source = tmp_path / 'source'
    make_tree(source)
    monkeypatch.setattr(reducer, 'verify_openmvs_tree', lambda tree, research: None)
    with pytest.raises(ScaffoldError, match='overlap'):
        reducer.make_reduced_tree(source, source / 'nested')
    (source / 'alias').symlink_to(source / 'LICENSE')
    with pytest.raises(ScaffoldError, match='Symlink'):
        reducer.make_reduced_tree(source, tmp_path / 'output')
    assert not (tmp_path / 'output').exists()
