import io
import tarfile
from pathlib import Path

import pytest
from common import ROOT, ScaffoldError


def test_prepares_separate_local_recipe_and_builder(tmp_path, monkeypatch):
    import opensfm_reduced_recipe as reduced
    original = tmp_path/'original.tar.gz'
    original.write_bytes(b'fixture')
    candidate = tmp_path/'candidate.tar.gz'
    with tarfile.open(candidate, 'w:gz') as archive:
        for name,data in [('source/CANDIDATE-MANIFEST.json',b'{}'),('source/opensfm/dataset.py',b'code')]:
            member=tarfile.TarInfo(name); member.size=len(data); archive.addfile(member,io.BytesIO(data))
    def fake_make(source, output):
        output.write_bytes(candidate.read_bytes()); return {'scope':'fixture'}
    monkeypatch.setattr(reduced,'make_candidate',fake_make)
    files = [ROOT/'research/recipes/opensfm-scoped-odm/recipe.yaml', ROOT/'scripts/build_open_research.py']
    monkeypatch.setattr(reduced,'repository_files',lambda root: files)
    dest=tmp_path/'output'
    reduced.prepare(original,candidate,dest)
    recipe=(dest/'packaging/research/recipes/opensfm-scoped-odm/recipe.yaml').read_text()
    builder=(dest/'packaging/scripts/build_open_research.py').read_text()
    assert str(dest/'source') in recipe and 'c5328439465e6ace011f39077d1077d7b1cdd65d' not in recipe
    assert 'verify_reduced_opensfm_research_tree(source)' in builder
    assert 'assets_preexcluded=True' in builder
    assert not (dest/'source/CANDIDATE-MANIFEST.json').exists()
    compile(builder, 'builder', 'exec')


def test_reduced_graph_fails_closed(tmp_path, monkeypatch):
    import opensfm_reduced_recipe as reduced
    monkeypatch.setattr(reduced,'EXPECTED_REDUCED_GRAPH',(1,'good'))
    monkeypatch.setattr(reduced,'fingerprint_tree',lambda tree, ignore_root_files: (1,'bad'))
    with pytest.raises(ScaffoldError, match='Unrecognized'):
        reduced.verify_reduced_opensfm_research_tree(tmp_path)
    (tmp_path/'.source_info.json').symlink_to(tmp_path/'missing')
    with pytest.raises(ScaffoldError, match='Unsafe'):
        reduced.verify_reduced_opensfm_research_tree(tmp_path)
