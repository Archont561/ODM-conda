from copy import deepcopy

import pytest

from common import ROOT, ScaffoldError
from stage_sources import load_plan


def source():
    plan = load_plan(ROOT / 'research/source-graphs.json', 'opensfm')
    return {**plan['primary'], 'additional_sources': deepcopy(plan['additional']), 'disabled_build_trees': []}


def test_only_pinned_opensfm_graph_is_accepted():
    from opensfm_graph_policy import validate_opensfm_graph
    primary, additional = validate_opensfm_graph('opensfm-odm', source())
    assert primary['name'] == 'opensfm'
    assert additional[0]['name'] == 'pybind11'


@pytest.mark.parametrize('mutation', ['name', 'primary', 'revision', 'path', 'gitlink', 'disabled', 'extra'])
def test_opensfm_graph_fails_closed(mutation):
    from opensfm_graph_policy import validate_opensfm_graph
    data = source()
    name = 'opensfm-odm'
    if mutation == 'name':
        name = 'other'
    elif mutation == 'primary':
        data['sha256'] = '0' * 64
    elif mutation == 'revision':
        data['additional_sources'][0]['commit'] = '0' * 40
    elif mutation == 'path':
        data['additional_sources'][0]['path'] = 'other'
    elif mutation == 'gitlink':
        data['additional_sources'][0]['gitlink'] = False
    elif mutation == 'disabled':
        data['disabled_build_trees'] = ['tests']
    else:
        data['additional_sources'].append(deepcopy(data['additional_sources'][0]))
    with pytest.raises(ScaffoldError, match='Unreviewed'):
        validate_opensfm_graph(name, data)


def test_opensfm_patched_tree_rejects_modified_files_and_symlinks(tmp_path, monkeypatch):
    import opensfm_graph_policy as policy
    from openmvs_graph_policy import fingerprint_tree

    tree = tmp_path / 'tree'
    tree.mkdir()
    (tree / 'CMakeLists.txt').write_text('reviewed')
    monkeypatch.setattr(policy, 'EXPECTED_TREE', fingerprint_tree(tree))
    policy.verify_opensfm_tree(tree)
    (tree / 'extra').write_text('unexpected')
    with pytest.raises(ScaffoldError, match='fingerprint'):
        policy.verify_opensfm_tree(tree)
    (tree / 'extra').unlink()
    (tree / 'link').symlink_to('/etc/passwd')
    with pytest.raises(ScaffoldError, match='symlink'):
        policy.verify_opensfm_tree(tree)


def test_opensfm_patch_must_match_reviewed_bytes():
    from opensfm_graph_policy import validate_opensfm_patch
    patch = {'file': 'research/patches/opensfm-ceres-config.patch',
             'sha256': '1cbf2c8044e0281368c8802205f14816fc3b635fb419a7d8fa3570603fdfd773',
             'target': '.', 'summary': 'Use Ceres config targets.'}
    validate_opensfm_patch({'patches': [patch]})
    patch['sha256'] = '0' * 64
    with pytest.raises(ScaffoldError, match='patch'):
        validate_opensfm_patch({'patches': [patch]})


def test_archive_scans_validate_gitmodules_and_test_fetches(tmp_path, monkeypatch):
    import hashlib
    import tarfile
    import opensfm_graph_policy as policy
    from source_bundle import add_bytes

    root = tmp_path / 'root.tar.gz'
    dep = tmp_path / 'dep.tar.gz'
    modules = b'[submodule "dep"]\npath = third_party/dep\n'
    fetch = b'FetchContent_Declare(eigen)'
    with tarfile.open(root, 'w:gz') as tar:
        add_bytes(tar, 'root/.gitmodules', modules)
        add_bytes(tar, 'root/CMakeLists.txt', b'project(example)')
    with tarfile.open(dep, 'w:gz') as tar:
        add_bytes(tar, 'dep/tests/CMakeLists.txt', fetch)
    monkeypatch.setattr(policy, 'PRIMARY', {**policy.PRIMARY, 'sha256': hashlib.sha256(root.read_bytes()).hexdigest()})
    monkeypatch.setattr(policy, 'PYBIND11', {**policy.PYBIND11, 'sha256': hashlib.sha256(dep.read_bytes()).hexdigest()})
    monkeypatch.setattr(policy, 'GITMODULES_SHA256', hashlib.sha256(modules).hexdigest())
    monkeypatch.setattr(policy, 'PYBIND_FETCH_EXCEPTIONS', {'tests/CMakeLists.txt': hashlib.sha256(fetch).hexdigest()})
    policy.verify_opensfm_archives(root, dep)
    with tarfile.open(dep, 'w:gz') as tar:
        add_bytes(tar, 'dep/tests/CMakeLists.txt', fetch)
        add_bytes(tar, 'dep/other/CMakeLists.txt', b'file(DOWNLOAD https://example.invalid)')
    monkeypatch.setattr(policy, 'PYBIND11', {**policy.PYBIND11, 'sha256': hashlib.sha256(dep.read_bytes()).hexdigest()})
    with pytest.raises(ScaffoldError, match='Unstaged external CMake source'):
        policy.verify_opensfm_archives(root, dep)
    dep.write_bytes(b'tampered')
    with pytest.raises(ScaffoldError, match='checksum'):
        policy.verify_opensfm_archives(root, dep)
