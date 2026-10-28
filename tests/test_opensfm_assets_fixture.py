"""Validate OpenSfM's pinned runtime assets without claiming redistribution rights."""
import hashlib

import pytest

import opensfm_assets_fixture as fixture


def test_asset_fixture_rejects_missing_changed_and_symlinked_assets(tmp_path, monkeypatch):
    asset = tmp_path / 'opensfm' / 'data' / 'bow' / 'vocabulary.npz'
    asset.parent.mkdir(parents=True)
    content = b'example asset bytes'
    monkeypatch.setattr(fixture, 'ASSETS', {'data/bow/vocabulary.npz': hashlib.sha256(content).hexdigest()})
    with pytest.raises(ValueError, match='missing'):
        fixture.verify_assets(tmp_path)
    asset.write_bytes(content)
    fixture.verify_assets(tmp_path)
    asset.write_bytes(b'changed')
    with pytest.raises(ValueError, match='checksum'):
        fixture.verify_assets(tmp_path)
    asset.unlink()
    target = tmp_path / 'external'
    target.write_bytes(content)
    asset.symlink_to(target)
    with pytest.raises(ValueError, match='symlink'):
        fixture.verify_assets(tmp_path)
    asset.unlink()
    asset.parent.rmdir()
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'vocabulary.npz').write_bytes(content)
    asset.parent.symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match='symlink'):
        fixture.verify_assets(tmp_path)
