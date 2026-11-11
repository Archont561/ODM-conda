import hashlib
import json
from pathlib import Path

import pytest


def test_preparation_checks_candidate_and_patches_only_private_recipe(tmp_path, monkeypatch):
    import prepare_jxl_reduced_research as mod
    from common import ScaffoldError

    original = tmp_path/'original'; original.write_bytes(b'original')
    contents = {'pyproject.toml': b'[tool.maturin]\nfeatures = ["pyo3/extension-module", "vendored"]\n', 'src/lib.rs': b'fn f() {}'}
    records = {key: {'sha256': hashlib.sha256(value).hexdigest(), 'mode': '0644'} for key,value in contents.items()}
    manifest = {'scope': 'local-research-only', 'files': records}
    monkeypatch.setattr(mod, 'CANDIDATE_SHA256', hashlib.sha256(b'candidate').hexdigest())
    monkeypatch.setattr(mod, 'EXCLUDED', {'a.png': hashlib.sha256(b'image').hexdigest()})
    def candidate(_source, dest):
        dest.write_bytes(b'candidate')
        return manifest
    def unpack(_archive, dest):
        for name, value in contents.items():
            path=dest/name; path.parent.mkdir(parents=True,exist_ok=True); path.write_bytes(value)
        (dest/'CANDIDATE-MANIFEST.json').write_text(json.dumps(manifest))
    def prepare(_source, dest):
        staged=dest/'source'; (staged/'src').mkdir(parents=True)
        for name, value in contents.items():
            if name == 'pyproject.toml': value=value.replace(b'vendored',b'dynamic')
            (staged/name).write_bytes(value)
        path=staged/'test/images/a.png'; path.parent.mkdir(parents=True); path.write_bytes(b'image')
        recipe=dest/'recipe/recipe.yaml'; recipe.parent.mkdir()
        recipe.write_text('build:\n  number: 1\n  string: research_${{ hash }}_1\ntests:\n  old: true\nabout:\n  license: LicenseRef-Unreviewed\n')
    monkeypatch.setattr(mod,'make_candidate',candidate)
    monkeypatch.setattr(mod,'unpack_archive',unpack)
    monkeypatch.setattr(mod,'prepare_original',prepare)
    result=mod.prepare(original,tmp_path/'prepared')
    text=(result/'recipe/recipe.yaml').read_text()
    assert 'number: 2\n  string: research_reduced_${{ hash }}_2' in text
    assert 'LicenseRef-Unreviewed' in text and 'base64' in text
    assert not (result/'source/test/images/a.png').exists()
    assert (result/'source/CANDIDATE-MANIFEST.json').is_file()
    with pytest.raises(ScaffoldError,match='existing'):
        mod.prepare(original,result)


def test_preparation_does_not_delete_existing_destination_on_race(tmp_path, monkeypatch):
    import prepare_jxl_reduced_research as mod
    from common import ScaffoldError
    original=tmp_path/'original'; original.write_bytes(b'original')
    monkeypatch.setattr(mod,'CANDIDATE_SHA256',hashlib.sha256(b'candidate').hexdigest())
    def candidate(_source,dest): dest.write_bytes(b'candidate'); return {'files': {}}
    def unpack(_source,dest): (dest/'CANDIDATE-MANIFEST.json').write_text('{"files": {}}')
    def race(_source,dest):
        dest.mkdir(); (dest/'other').write_text('preserve')
        raise ScaffoldError('destination exists')
    monkeypatch.setattr(mod,'make_candidate',candidate)
    monkeypatch.setattr(mod,'unpack_archive',unpack)
    monkeypatch.setattr(mod,'prepare_original',race)
    dest=tmp_path/'prepared'
    with pytest.raises(ScaffoldError,match='exists'):
        mod.prepare(original,dest)
    assert (dest/'other').read_text() == 'preserve'
