import json

import pytest

from common import ScaffoldError
from openmvs_graph_policy import fingerprint_tree
import opensfm_graph_policy as policy


def test_research_tree_requires_exact_vmem_source_metadata(tmp_path, monkeypatch):
    tree = tmp_path / 'tree'
    tree.mkdir()
    (tree / 'file').write_text('verified')
    monkeypatch.setattr(policy, 'EXPECTED_RESEARCH_TREE', fingerprint_tree(tree))
    sources = [
        {'url': policy.PRIMARY['url'], 'sha256': policy.PRIMARY['sha256'], 'patches': ['patches/0001-ceres-config.patch']},
        {'url': policy.PYBIND11['url'], 'sha256': policy.PYBIND11['sha256'], 'target_directory': policy.PYBIND11['path']},
        {'url': policy.VMEM['url'], 'sha256': policy.VMEM['sha256'], 'target_directory': policy.VMEM['path']},
    ]
    metadata = tree / '.source_info.json'
    metadata.write_text(json.dumps({'sources': sources}))
    policy.verify_opensfm_research_tree(tree)
    sources[2]['sha256'] = '0' * 64
    metadata.write_text(json.dumps({'sources': sources}))
    with pytest.raises(ScaffoldError, match='metadata'):
        policy.verify_opensfm_research_tree(tree)


def test_vmem_archive_requires_the_pinned_digest(tmp_path):
    archive = tmp_path / 'vmem.tar.gz'
    archive.write_bytes(b'not the reviewed archive')
    with pytest.raises(ScaffoldError, match='checksum'):
        policy.verify_vmem_archive(archive)
