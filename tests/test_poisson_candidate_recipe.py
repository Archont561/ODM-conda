import io
import tarfile
from pathlib import Path

import pytest
from common import ScaffoldError, sha256
from test_poisson_reduced_candidate import fixture_archive


def test_prepare_rewrites_recipe_and_provenance_without_touching_original(tmp_path, monkeypatch):
    import poisson_reduced_candidate as candidate
    import poisson_candidate_recipe as preparer
    from poisson_candidate_recipe import prepare
    original = tmp_path / 'original.tar.gz'
    fixture_archive(original)
    monkeypatch.setattr(candidate, 'PINNED_SHA256', sha256(original))
    monkeypatch.setattr(preparer, 'PINNED_SHA256', sha256(original))
    packaging = tmp_path / 'packaging'
    recipe = packaging / 'recipes/poissonrecon-odm/recipe.yaml'
    recipe.parent.mkdir(parents=True)
    recipe.write_text('source:\n  url: https://codeload.github.com/OpenDroneMap/PoissonRecon/tar.gz/97caa6d34d1b05b59888bed019dea89ced74445e\n  sha256: ${{ source_sha256 }}\nbuild:\n  number: 3\n')
    builder = packaging / 'scripts/build_component.py'
    builder.parent.mkdir()
    builder.write_text('def main():\n    pass\n\n\nif __name__ == "__main__":\n    main()\n')
    monkeypatch.setattr(candidate, 'repository_files', lambda root: [recipe, builder])
    archive = tmp_path / 'candidate.tar.gz'
    candidate.make_candidate(original, archive, root=packaging)
    destination = tmp_path / 'prepared'
    info = prepare(archive, destination, original, root=packaging)
    assert 'string: research_${{ hash }}_3' in (destination / 'packaging/recipes/poissonrecon-odm/recipe.yaml').read_text()
    generated = (destination / 'packaging/recipes/poissonrecon-odm/recipe.yaml').read_text()
    assert str(destination / 'source') in generated
    assert 'codeload.github.com' not in generated and 'sha256: ${{ source_sha256 }}' not in generated
    assert 'LOCAL RESEARCH ONLY' in (destination / 'packaging/scripts/build_component.py').read_text()
    assert info['candidate_sha256'] == sha256(archive)
    assert 'codeload.github.com' in recipe.read_text()
    assert list((destination / 'source/JPEG').iterdir()) == []


def test_rejects_unsafe_candidate_without_creating_destination(tmp_path, monkeypatch):
    import poisson_candidate_recipe as preparer
    from poisson_candidate_recipe import prepare
    original = tmp_path / 'original.tar.gz'
    fixture_archive(original)
    monkeypatch.setattr(preparer, 'PINNED_SHA256', sha256(original))
    archive = tmp_path / 'evil.tar.gz'
    with tarfile.open(archive, 'w:gz') as out:
        entry = tarfile.TarInfo('../escape')
        entry.size = 1
        out.addfile(entry, io.BytesIO(b'x'))
    destination = tmp_path / 'dest'
    with pytest.raises(ScaffoldError, match='Unsafe'):
        prepare(archive, destination, original, root=tmp_path / 'root')
    assert not destination.exists()


def test_rejects_rehashed_but_forged_source(tmp_path, monkeypatch):
    import hashlib
    import json
    import poisson_reduced_candidate as candidate
    import poisson_candidate_recipe as preparer
    original = tmp_path / 'original.tar.gz'
    fixture_archive(original)
    monkeypatch.setattr(candidate, 'PINNED_SHA256', sha256(original))
    monkeypatch.setattr(preparer, 'PINNED_SHA256', sha256(original))
    root = tmp_path / 'packaging'
    root.mkdir()
    (root / 'dummy').write_text('x')
    monkeypatch.setattr(candidate, 'repository_files', lambda root: [root / 'dummy'])
    good, bad = tmp_path / 'good.tar.gz', tmp_path / 'bad.tar.gz'
    candidate.make_candidate(original, good, root=root)
    with tarfile.open(good) as archive:
        entries = [(m, archive.extractfile(m).read() if m.isfile() else b'') for m in archive]
    manifest = json.loads(next(data for m, data in entries if m.name == 'CANDIDATE-MANIFEST.json'))
    manifest['files']['source/Makefile'] = hashlib.sha256(b'forged').hexdigest()
    with tarfile.open(bad, 'w:gz') as out:
        for member, data in entries:
            if member.name == 'source/Makefile':
                data = b'forged'
            if member.name == 'CANDIDATE-MANIFEST.json':
                data = json.dumps(manifest).encode()
            member.size = len(data)
            out.addfile(member, io.BytesIO(data) if member.isfile() else None)
    with pytest.raises(ScaffoldError, match='differs from pinned'):
        preparer.prepare(bad, tmp_path / 'prepared', original, root=root)
    assert not (tmp_path / 'prepared').exists()
