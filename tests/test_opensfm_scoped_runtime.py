"""Scoped OpenSfM runtime rejects configurations requiring omitted assets."""
import pytest


def test_scoped_config_allows_default_and_rejects_bow_vlad():
    from opensfm_scoped_guard import validate_config
    default = {'matcher_type': 'FLANN', 'matching_bow_neighbors': 0, 'matching_vlad_neighbors': 0}
    validate_config(default)
    for changes in ({'matcher_type': 'words'}, {'matching_bow_neighbors': 2}, {'matching_vlad_neighbors': 1}):
        with pytest.raises(ValueError, match='not supported'):
            validate_config({**default, **changes})


def test_scoped_config_rejects_invalid_or_missing_fields():
    from opensfm_scoped_guard import validate_config
    for value in ({}, {'matcher_type': 'FLANN', 'matching_bow_neighbors': '0', 'matching_vlad_neighbors': 0},
                  {'matcher_type': None, 'matching_bow_neighbors': 0, 'matching_vlad_neighbors': 0}):
        with pytest.raises(ValueError, match='invalid'):
            validate_config(value)


def test_scoped_copy_removes_only_verified_assets_and_adds_guard(tmp_path, monkeypatch):
    import hashlib
    import opensfm_scoped_runtime as scoped

    source = tmp_path / 'installed' / 'opensfm'
    source.mkdir(parents=True)
    dataset = b'class DataSet:\n    def load_config(self):\n        self.config = {}\n\n    def _image_list_file(self):\n        pass\n'
    (source / 'dataset.py').write_bytes(dataset)
    monkeypatch.setattr(scoped, 'DATASET_SHA256', hashlib.sha256(dataset).hexdigest())
    assets = {'data/bow/a.npz': b'a', 'data/bow/b.npz': b'b', 'data/sensor_data.sqlite': b'c'}
    monkeypatch.setattr(scoped, 'EXCLUDED_ASSETS', {k: hashlib.sha256(v).hexdigest() for k, v in assets.items()})
    for name, data in assets.items():
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (source / 'data/keep.json').write_text('{}')
    target = tmp_path / 'candidate' / 'opensfm'
    target.parent.mkdir()
    report = scoped.make_scoped_runtime(source, target)
    assert report['excluded_count'] == 3
    assert (source / 'data/bow/a.npz').exists()
    assert not (target / 'data/bow/a.npz').exists()
    assert (target / 'data/keep.json').is_file()
    assert 'validate_config(self.config)' in (target / 'dataset.py').read_text()
    assert (target / 'scoped_runtime_guard.py').is_file()


def test_scoped_copy_rejects_unverified_and_existing_inputs(tmp_path):
    import opensfm_scoped_runtime as scoped
    from common import ScaffoldError
    source = tmp_path / 'source'
    source.mkdir()
    (source / 'dataset.py').write_text('unverified')
    target = tmp_path / 'target'
    with pytest.raises(ScaffoldError):
        scoped.make_scoped_runtime(source, target)
    assert not target.exists()
    target.mkdir()
    with pytest.raises(ScaffoldError):
        scoped.make_scoped_runtime(source, target)
