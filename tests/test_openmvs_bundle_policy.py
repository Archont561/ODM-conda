from copy import deepcopy

import pytest

from common import ROOT, ScaffoldError
from stage_sources import load_plan


def component_source():
    plan = load_plan(ROOT / 'research' / 'source-graphs.json', 'openmvs')
    root = {key: plan['primary'][key] for key in ('url', 'commit', 'sha256')}
    root['additional_sources'] = deepcopy(plan['additional'])
    root['disabled_build_trees'] = []
    return root


def test_only_reviewed_openmvs_graph_is_accepted():
    from openmvs_graph_policy import validate_openmvs_graph

    primary, additional = validate_openmvs_graph('openmvs-odm', component_source())
    assert primary['name'] == 'openmvs'
    assert [source['name'] for source in additional] == ['vcg', 'eigen34']


@pytest.mark.parametrize('mutation', ['name', 'root', 'nested-hash', 'nested-path', 'extra', 'disabled'])
def test_unreviewed_openmvs_graph_is_rejected(mutation):
    from openmvs_graph_policy import validate_openmvs_graph

    source = component_source()
    name = 'openmvs-odm'
    if mutation == 'name':
        name = 'other'
    elif mutation == 'root':
        source['sha256'] = '0' * 64
    elif mutation == 'nested-hash':
        source['additional_sources'][0]['sha256'] = '0' * 64
    elif mutation == 'nested-path':
        source['additional_sources'][1]['path'] = 'other'
    elif mutation == 'extra':
        source['additional_sources'].append(deepcopy(source['additional_sources'][0]))
    else:
        source['disabled_build_trees'] = ['other']
    with pytest.raises(ScaffoldError, match='Unreviewed'):
        validate_openmvs_graph(name, source)


def test_multi_source_bundle_contains_all_verified_inputs(tmp_path, monkeypatch):
    import json
    import tarfile

    import openmvs_graph_policy as policy
    import source_bundle
    from test_source_graph import cached_archive

    cache = tmp_path / 'cache'
    primary = cached_archive(cache, 'openmvs', [('root/CMakeLists.txt', b'project(example)')])
    primary['name'] = 'openmvs'
    vcg = cached_archive(cache, 'vcg', [('root/header.h', b'vcg')])
    vcg.update(name='vcg', path='_external/vcg')
    eigen = cached_archive(cache, 'eigen34', [('root/lapack/CMakeLists.txt', b'file(DOWNLOAD x y)'),
                                                ('root/Eigen/Core', b'eigen')])
    eigen.update(name='eigen34', path='_external/eigen')
    monkeypatch.setattr(policy, 'OPENMVS', primary)
    monkeypatch.setattr(policy, 'VCG', vcg)
    monkeypatch.setattr(policy, 'EIGEN', eigen)
    readme = tmp_path / 'README.md'
    readme.write_text('packaging', encoding='utf-8')
    monkeypatch.setattr(source_bundle, 'repository_files', lambda *_: [readme])
    source = dict(primary, additional_sources=[vcg, eigen], disabled_build_trees=[])
    component = {'source': source, 'version': '1.0', 'build_number': 0}
    result = source_bundle.make_bundle('openmvs-odm', component, tmp_path / 'bundle', cache, tmp_path)
    with tarfile.open(result, 'r:gz') as archive:
        manifest = json.load(archive.extractfile('SOURCE-MANIFEST.json'))
        for item in (primary, vcg, eigen):
            path = f"upstream/{item['name']}-{item['commit']}.tar.gz"
            assert path in manifest['files']
            assert archive.extractfile(path).read() == (cache / path.split('/')[-1]).read_bytes()

    (cache / f"vcg-{vcg['commit']}.tar.gz").write_bytes(b'tampered')
    with pytest.raises(ScaffoldError, match='checksum'):
        source_bundle.make_bundle('openmvs-odm', component, tmp_path / 'bad', cache, tmp_path)


def test_eigen_fetch_outside_disabled_tree_is_rejected(tmp_path, monkeypatch):
    import openmvs_graph_policy as policy
    from source_bundle import graph_archives
    from test_source_graph import cached_archive

    cache = tmp_path / 'cache'
    primary = cached_archive(cache, 'openmvs', [('root/CMakeLists.txt', b'project(example)')])
    primary['name'] = 'openmvs'
    vcg = cached_archive(cache, 'vcg', [('root/header.h', b'vcg')])
    vcg.update(name='vcg', path='_external/vcg')
    eigen = cached_archive(cache, 'eigen34', [('root/lapack/CMakeLists.txt', b'file(DOWNLOAD x y)'),
                                                ('root/cmake/Unsafe.cmake', b'FetchContent_Declare(bad)')])
    eigen.update(name='eigen34', path='_external/eigen')
    monkeypatch.setattr(policy, 'OPENMVS', primary)
    monkeypatch.setattr(policy, 'VCG', vcg)
    monkeypatch.setattr(policy, 'EIGEN', eigen)
    source = dict(primary, additional_sources=[vcg, eigen], disabled_build_trees=[])
    with pytest.raises(ScaffoldError, match='Unstaged external CMake source'):
        graph_archives('openmvs-odm', source, cache)


def test_staged_tree_fingerprint_rejects_changes_and_symlinks(tmp_path, monkeypatch):
    import openmvs_graph_policy as policy

    tree = tmp_path / 'tree'
    tree.mkdir()
    (tree / 'CMakeLists.txt').write_text('project(example)\n', encoding='utf-8')
    nested = tree / '_external' / 'eigen'
    nested.mkdir(parents=True)
    (nested / 'header').write_text('original', encoding='utf-8')
    count, digest = policy.fingerprint_tree(tree)
    monkeypatch.setattr(policy, 'EXPECTED_TREE', (count, digest))
    policy.verify_openmvs_tree(tree)
    (nested / 'header').write_text('changed', encoding='utf-8')
    with pytest.raises(ScaffoldError, match='tree fingerprint'):
        policy.verify_openmvs_tree(tree)
    (nested / 'header').unlink()
    (nested / 'header').symlink_to(tree / 'CMakeLists.txt')
    with pytest.raises(ScaffoldError, match='symlink'):
        policy.verify_openmvs_tree(tree)


def test_openmvs_builder_rejects_missing_or_changed_patch_metadata():
    from openmvs_graph_policy import validate_openmvs_patches

    patches = [
        {'file': 'research/patches/openmvs-reconstruct-only.patch',
         'sha256': '2dc920d550119443bb8d079911b0cdfc4cc747eb916a48a01e09ebdaf6a2c96a',
         'summary': 'Select the reduced Boost reconstruction target.'},
        {'file': 'research/patches/openmvs-visibility-check.patch',
         'sha256': '74f36291ca9254b2fe32c600c7e939827859aa1d07f73a976217961d39624c90',
         'summary': 'Reject point clouds without valid visibility.'},
    ]
    validate_openmvs_patches({'patches': patches})
    with pytest.raises(ScaffoldError, match='patch'):
        validate_openmvs_patches({'patches': patches[:1]})
    patches[0]['sha256'] = '0' * 64
    with pytest.raises(ScaffoldError, match='patch'):
        validate_openmvs_patches({'patches': patches})
