from copy import deepcopy

import pytest

from common import ROOT, ScaffoldError
from stage_sources import load_plan


def source():
    plan = load_plan(ROOT / 'research' / 'source-graphs.json', 'mvs-texturing')
    return {**plan['primary'], 'additional_sources': deepcopy(plan['additional']), 'disabled_build_trees': []}


def test_exact_texturing_graph_is_recognized():
    from texturing_graph_policy import validate_texturing_graph

    primary, nested = validate_texturing_graph('mvs-texturing-odm', source())
    assert primary['name'] == 'texturing'
    assert [entry['name'] for entry in nested] == ['mve', 'mapmap', 'rayint', 'eigen332']


@pytest.mark.parametrize('change', ['name', 'root', 'hash', 'path', 'missing', 'disabled'])
def test_unrecognized_texturing_graph_is_rejected(change):
    from texturing_graph_policy import validate_texturing_graph

    data = source()
    name = 'mvs-texturing-odm'
    if change == 'name':
        name = 'other'
    elif change == 'root':
        data['sha256'] = '0' * 64
    elif change == 'hash':
        data['additional_sources'][0]['sha256'] = '0' * 64
    elif change == 'path':
        data['additional_sources'][1]['path'] = '../elsewhere'
    elif change == 'missing':
        data['additional_sources'].pop()
    else:
        data['disabled_build_trees'] = ['src']
    with pytest.raises(ScaffoldError, match='Unreviewed'):
        validate_texturing_graph(name, data)


def test_texturing_bundle_stages_five_sources_and_rejects_tampering(tmp_path, monkeypatch):
    import hashlib
    import json
    import tarfile
    import source_bundle
    import texturing_graph_policy as policy
    from test_source_graph import cached_archive

    cache = tmp_path / 'cache'
    root_fetch = b'externalproject_add(bad)'
    primary = cached_archive(cache, 'texturing', [('root/CMakeLists.txt', b'project(example)'),
                                                  ('root/elibs/CMakeLists.txt', root_fetch)])
    primary['name'] = 'texturing'
    entries = []
    for name, path in [('mve', '_external/mve'), ('mapmap', 'elibs/mapmap'),
                       ('rayint', 'elibs/rayint'), ('eigen332', 'elibs/eigen')]:
        entry = cached_archive(cache, name, [('root/header.h', name.encode())])
        entry.update(name=name, path=path)
        entries.append(entry)
    monkeypatch.setattr(policy, 'PRIMARY', primary)
    monkeypatch.setattr(policy, 'ADDITIONAL', entries)
    monkeypatch.setattr(policy, 'FETCH_EXCEPTIONS', {'texturing': {'elibs/CMakeLists.txt': hashlib.sha256(root_fetch).hexdigest()},
                                                       'mve': {}, 'mapmap': {}, 'rayint': {}, 'eigen332': {}})
    readme = tmp_path / 'README.md'
    readme.write_text('packaging')
    monkeypatch.setattr(source_bundle, 'repository_files', lambda *_: [readme])
    src = dict(primary, additional_sources=entries, disabled_build_trees=[])
    component = {'source': src, 'version': '1.0', 'build_number': 0}
    result = source_bundle.make_bundle('mvs-texturing-odm', component, tmp_path / 'out', cache, tmp_path)
    with tarfile.open(result, 'r:gz') as archive:
        manifest = json.load(archive.extractfile('SOURCE-MANIFEST.json'))
        for item in [primary, *entries]:
            archive_path = f"upstream/{item['name']}-{item['commit']}.tar.gz"
            assert archive_path in manifest['files']
            assert archive.extractfile(archive_path).read() == (cache / archive_path.split('/')[-1]).read_bytes()
    (cache / f"rayint-{entries[2]['commit']}.tar.gz").write_bytes(b'tampered')
    with pytest.raises(ScaffoldError, match='checksum'):
        source_bundle.make_bundle('mvs-texturing-odm', component, tmp_path / 'bad', cache, tmp_path)


def test_patched_texturing_tree_verifier_rejects_changes(tmp_path, monkeypatch):
    import texturing_graph_policy as policy
    from openmvs_graph_policy import fingerprint_tree

    source_tree = tmp_path / 'src'
    source_tree.mkdir()
    (source_tree / 'source.cpp').write_text('original', encoding='utf-8')
    monkeypatch.setattr(policy, 'EXPECTED_TREE', fingerprint_tree(source_tree))
    policy.verify_texturing_tree(source_tree)
    (source_tree / 'source.cpp').write_text('changed', encoding='utf-8')
    with pytest.raises(ScaffoldError, match='tree fingerprint'):
        policy.verify_texturing_tree(source_tree)
    (source_tree / 'source.cpp').unlink()
    (source_tree / 'link').symlink_to('/etc/passwd')
    with pytest.raises(ScaffoldError, match='symlink'):
        policy.verify_texturing_tree(source_tree)


def test_texturing_patch_metadata_must_identify_both_exact_patches():
    from texturing_graph_policy import validate_texturing_patches

    patches = [
        {'file': 'research/patches/mvs-texturing-offline.patch',
         'sha256': '37d03ca8b5a50bd72b6e7a4ed2f2856e1d83c0355806f7fc9efa059f9a57ef65',
         'target': '.', 'summary': 'Use staged dependencies.'},
        {'file': 'research/patches/mve-baseline-cpu.patch',
         'sha256': '7427f3332ba65a1ebf677940fbf9ec957c7343a311844953d829d30e0944646c',
         'target': '_external/mve', 'summary': 'Build for baseline CPUs.'},
    ]
    validate_texturing_patches({'patches': patches})
    with pytest.raises(ScaffoldError, match='patch'):
        validate_texturing_patches({'patches': patches[:1]})
    patches[0]['sha256'] = '0' * 64
    with pytest.raises(ScaffoldError, match='patch'):
        validate_texturing_patches({'patches': patches})


def test_rattler_source_metadata_must_match_pinned_graph(tmp_path, monkeypatch):
    import json
    import texturing_graph_policy as policy
    from openmvs_graph_policy import fingerprint_tree

    tree = tmp_path / 'source'
    tree.mkdir()
    (tree / 'CMakeLists.txt').write_text('test', encoding='utf-8')
    monkeypatch.setattr(policy, 'EXPECTED_TREE', fingerprint_tree(tree))
    sources = [{'url': policy.PRIMARY['url'], 'sha256': policy.PRIMARY['sha256'],
                'patches': ['patches/0001-offline.patch']}]
    for entry in policy.ADDITIONAL:
        item = {'url': entry['url'], 'sha256': entry['sha256'], 'target_directory': entry['path']}
        if entry['name'] == 'mve':
            item['patches'] = ['patches/0002-mve-baseline.patch']
        sources.append(item)
    info = tree / '.source_info.json'
    info.write_text(json.dumps({'sources': sources}), encoding='utf-8')
    policy.verify_texturing_tree(tree)
    sources[1]['sha256'] = '0' * 64
    info.write_text(json.dumps({'sources': sources}), encoding='utf-8')
    with pytest.raises(ScaffoldError, match='source metadata'):
        policy.verify_texturing_tree(tree)
    info.unlink()
    info.symlink_to('/etc/passwd')
    with pytest.raises(ScaffoldError, match='symlink'):
        policy.verify_texturing_tree(tree)
