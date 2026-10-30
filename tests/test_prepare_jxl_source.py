"""Preparation must verify the original source and pin the offline Cargo graph."""
import hashlib
import io
import tarfile

import pytest


def archive(path):
    files = {
        'Cargo.lock': b'version = 4\n[[package]]\nname = "test"\nversion = "1.0.0"\nsource = "registry+https://github.com/rust-lang/crates.io-index"\nchecksum = "' + b'1'*64 + b'"\n',
        'pyproject.toml': b'[tool.maturin]\nfeatures = ["pyo3/extension-module", "vendored"]\n',
        'Cargo.toml': b'[package]\nname = "sample"\nversion = "1.0.0"\n',
    }
    with tarfile.open(path, 'w:gz') as tar:
        for name, data in files.items():
            info = tarfile.TarInfo('src/'+name); info.size = len(data)
            tar.addfile(info, io.BytesIO(data))


def test_prepare_validates_source_and_stages_cargo_with_dynamic_linking(tmp_path, monkeypatch):
    import prepare_jxl_source as mod
    source = tmp_path/'source.tar.gz'; archive(source)
    monkeypatch.setattr(mod, 'SOURCE_SHA256', hashlib.sha256(source.read_bytes()).hexdigest())
    def vendor(command, **kwargs):
        assert '--locked' in command
        crate = kwargs['cwd']/'vendor/test-1.0.0'
        crate.mkdir(parents=True)
        (crate/'.cargo-checksum.json').write_text('{"package":"' + '1'*64 + '","files":{}}')
        return type('Completed', (), {'stdout': '[source.crates-io]\nreplace-with = "vendored-sources"\n[source.vendored-sources]\ndirectory = "vendor"\n'})()
    monkeypatch.setattr(mod.subprocess, 'run', vendor)
    result = mod.prepare(source, tmp_path/'prepared')
    pyproject=(result/'source/pyproject.toml').read_text()
    assert '"dynamic"' in pyproject and '"vendored"' not in pyproject
    assert (result/'source/.cargo/config.toml').is_file()
    assert str(result/'source') in (result/'recipe/recipe.yaml').read_text()
    with pytest.raises(mod.ScaffoldError):
        mod.prepare(source, tmp_path/'prepared')


def test_prepare_rejects_untrusted_source(tmp_path):
    from prepare_jxl_source import prepare
    from common import ScaffoldError
    source=tmp_path/'invalid.tar.gz';source.write_bytes(b'invalid')
    with pytest.raises(ScaffoldError, match='checksum'):
        prepare(source, tmp_path/'prepared')
