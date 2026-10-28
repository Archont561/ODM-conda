from __future__ import annotations

import hashlib
import io
import json
import subprocess
import tarfile
import zipfile
from pathlib import Path

import pytest
import zstandard

import source_bundle
from common import ScaffoldError, config, sha256
from package_archive import read_package, validate_member
from source_bundle import add_bytes, make_bundle, validate_upstream_archive


def tar_bytes(members: dict[str, bytes], link: str | None = None) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w") as archive:
        for name, value in members.items():
            add_bytes(archive, name, value)
        if link:
            entry = tarfile.TarInfo(link)
            entry.type = tarfile.SYMTYPE
            entry.linkname = "/etc/passwd"
            archive.addfile(entry)
    return output.getvalue()


def conda_bytes(path: Path, payload: bytes) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("metadata.json", json.dumps({"conda_pkg_format_version": 2}))
        archive.writestr("info-x.tar.zst", zstandard.ZstdCompressor().compress(tar_bytes({"info/index.json": b"{}"})))
        archive.writestr("pkg-x.tar.zst", zstandard.ZstdCompressor().compress(payload))


def test_package_paths_are_safe():
    validate_member("share/licenses/package/notice.txt")
    for bad in ("/etc/passwd", "../out", "bin/../../out", "C:\\outside", "a\\b", ""):
        with pytest.raises(ScaffoldError):
            validate_member(bad)


def test_conda_reader_checks_format_and_separates_payload(tmp_path):
    path = tmp_path / "fixture.conda"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("metadata.json", json.dumps({"conda_pkg_format_version": 2}))
        archive.writestr("info-fixture.tar.zst", zstandard.ZstdCompressor().compress(tar_bytes({"info/index.json": b"{}"})))
        archive.writestr("pkg-fixture.tar.zst", zstandard.ZstdCompressor().compress(tar_bytes({"bin/tool": b"ELF"})))
    info, payload = read_package(path)
    assert info == {"info/index.json": b"{}"}
    assert payload == {"bin/tool": b"ELF"}


@pytest.mark.parametrize("payload", [tar_bytes({"../escape": b"x"}), tar_bytes({}, link="bin/tool")], ids=["escaping-path", "symlink"])
def test_conda_reader_rejects_escaping_path_and_links(tmp_path, payload):
    path = tmp_path / "bad.conda"
    conda_bytes(path, payload)
    with pytest.raises(ScaffoldError):
        read_package(path)


def test_source_archive_rejects_submodules_fetches_and_traversal(tmp_path):
    cases = [{"project/.gitmodules": b"[submodule]"},
             {"project/CMakeLists.txt": b"ExternalProject_Add(nested)"},
             {"project/CMakeLists.txt": b"file(\nDOWNLOAD https://example.invalid)"},
             {"project/CMakeLists.txt": b"file(\tDOWNLOAD https://example.invalid)"},
             {"../escape": b"x"}]
    path = tmp_path / "source.tar.gz"
    for entries in cases:
        with tarfile.open(path, "w:gz") as archive:
            for name, value in entries.items():
                add_bytes(archive, name, value)
        with pytest.raises(ScaffoldError):
            validate_upstream_archive(path)


def test_disabled_test_fetch_requires_explicit_scope(tmp_path):
    path = tmp_path / "source.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        add_bytes(archive, "project/CMakeLists.txt", b"project(example)\n")
        add_bytes(archive, "project/test/CMakeLists.txt", b"FetchContent_Declare(googletest)\n")
    with pytest.raises(ScaffoldError):
        validate_upstream_archive(path)
    validate_upstream_archive(path, ("test",))


def test_plain_source_archive_is_accepted(tmp_path):
    path = tmp_path / "source.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        add_bytes(archive, "project/CMakeLists.txt", b"project(example)\n")
        add_bytes(archive, "project/LICENSE", b"license bytes")
    validate_upstream_archive(path)


def test_source_bundle_is_deterministic_and_contains_manifest(tmp_path, monkeypatch):
    readme = tmp_path / "README.md"
    readme.write_text("original packaging")
    upstream = tmp_path / "upstream.tar.gz"
    with tarfile.open(upstream, "w:gz") as archive:
        add_bytes(archive, "project/CMakeLists.txt", b"project(example)\n")
    component = config()["components"]["fpcfilter"]
    component["source"]["sha256"] = hashlib.sha256(upstream.read_bytes()).hexdigest()

    def fail_git(*args, **kwargs):
        raise subprocess.CalledProcessError(1, ["git"])

    monkeypatch.setattr(source_bundle, "source_archive", lambda *args, **kwargs: upstream)
    monkeypatch.setattr(source_bundle, "repository_files", lambda *args, **kwargs: [readme])
    monkeypatch.setattr(source_bundle.subprocess, "check_output", fail_git)

    first = make_bundle("fpcfilter", component, tmp_path / "one", tmp_path / "cache", tmp_path)
    second = make_bundle("fpcfilter", component, tmp_path / "two", tmp_path / "cache", tmp_path)
    assert sha256(first) == sha256(second)
    with tarfile.open(first, "r:gz") as archive:
        manifest = json.load(archive.extractfile("SOURCE-MANIFEST.json"))
        assert manifest["files"]["packaging/README.md"] == hashlib.sha256(readme.read_bytes()).hexdigest()
        assert "README-SOURCE.txt" in archive.getnames()
        assert all(member.mtime == 0 for member in archive)


def test_exact_hashed_disabled_fetch_file_does_not_exempt_neighbors(tmp_path):
    path = tmp_path / 'source.tar.gz'
    accepted = b'file(DOWNLOAD https://example.invalid file)\n'
    expected = {'disabled/CMakeLists.txt': hashlib.sha256(accepted).hexdigest()}
    with tarfile.open(path, 'w:gz') as archive:
        add_bytes(archive, 'project/disabled/CMakeLists.txt', accepted)
    validate_upstream_archive(path, fetch_exceptions=expected)
    with pytest.raises(ScaffoldError, match='exception'):
        validate_upstream_archive(path, fetch_exceptions={'disabled/CMakeLists.txt': '0' * 64})
    with tarfile.open(path, 'w:gz') as archive:
        add_bytes(archive, 'project/CMakeLists.txt', b'project(test)')
    with pytest.raises(ScaffoldError, match='exception'):
        validate_upstream_archive(path, fetch_exceptions={'missing/CMakeLists.txt': '0' * 64})
    with tarfile.open(path, 'w:gz') as archive:
        add_bytes(archive, 'project/disabled/CMakeLists.txt', accepted)
        add_bytes(archive, 'project/disabled/neighbor.cmake', b'file(DOWNLOAD https://bad.invalid x)')
    with pytest.raises(ScaffoldError, match='Unstaged external'):
        validate_upstream_archive(path, fetch_exceptions=expected)
