from __future__ import annotations

import hashlib
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import zstandard

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
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


class ArchiveTests(unittest.TestCase):
    def test_package_paths_are_safe(self):
        validate_member("share/licenses/package/notice.txt")
        for bad in ("/etc/passwd", "../out", "bin/../../out", "C:\\outside", "a\\b", ""):
            with self.assertRaises(ScaffoldError):
                validate_member(bad)

    def test_conda_reader_checks_format_and_separates_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.conda"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("metadata.json", json.dumps({"conda_pkg_format_version": 2}))
                archive.writestr("info-fixture.tar.zst", zstandard.ZstdCompressor().compress(tar_bytes({"info/index.json": b"{}"})))
                archive.writestr("pkg-fixture.tar.zst", zstandard.ZstdCompressor().compress(tar_bytes({"bin/tool": b"ELF"})))
            info, payload = read_package(path)
            self.assertEqual(info, {"info/index.json": b"{}"})
            self.assertEqual(payload, {"bin/tool": b"ELF"})

    def test_conda_reader_rejects_escaping_path_and_links(self):
        with tempfile.TemporaryDirectory() as directory:
            for index, payload in enumerate((tar_bytes({"../escape": b"x"}), tar_bytes({}, link="bin/tool"))):
                path = Path(directory) / f"bad-{index}.conda"
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr("metadata.json", json.dumps({"conda_pkg_format_version": 2}))
                    archive.writestr("info-x.tar.zst", zstandard.ZstdCompressor().compress(tar_bytes({"info/index.json": b"{}"})))
                    archive.writestr("pkg-x.tar.zst", zstandard.ZstdCompressor().compress(payload))
                with self.assertRaises(ScaffoldError):
                    read_package(path)

    def test_source_archive_rejects_submodules_fetches_and_traversal(self):
        cases = [{"project/.gitmodules": b"[submodule]"},
                 {"project/CMakeLists.txt": b"ExternalProject_Add(nested)"},
                 {"project/CMakeLists.txt": b"file(\nDOWNLOAD https://example.invalid)"},
                 {"../escape": b"x"}]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.tar.gz"
            for entries in cases:
                with tarfile.open(path, "w:gz") as archive:
                    for name, value in entries.items():
                        add_bytes(archive, name, value)
                with self.assertRaises(ScaffoldError):
                    validate_upstream_archive(path)

    def test_disabled_test_fetch_requires_explicit_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.tar.gz"
            with tarfile.open(path, "w:gz") as archive:
                add_bytes(archive, "project/CMakeLists.txt", b"project(example)\n")
                add_bytes(archive, "project/test/CMakeLists.txt", b"FetchContent_Declare(googletest)\n")
            with self.assertRaises(ScaffoldError):
                validate_upstream_archive(path)
            validate_upstream_archive(path, ("test",))

    def test_plain_source_archive_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.tar.gz"
            with tarfile.open(path, "w:gz") as archive:
                add_bytes(archive, "project/CMakeLists.txt", b"project(example)\n")
                add_bytes(archive, "project/LICENSE", b"license bytes")
            validate_upstream_archive(path)

    def test_source_bundle_is_deterministic_and_contains_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            readme = root / "README.md"
            readme.write_text("original packaging")
            upstream = root / "upstream.tar.gz"
            with tarfile.open(upstream, "w:gz") as archive:
                add_bytes(archive, "project/CMakeLists.txt", b"project(example)\n")
            component = config()["components"]["fpcfilter"]
            with patch("source_bundle.source_archive", return_value=upstream), \
                 patch("source_bundle.repository_files", return_value=[readme]), \
                 patch("source_bundle.subprocess.check_output", side_effect=subprocess.CalledProcessError(1, ["git"])):
                first = make_bundle("fpcfilter", component, root / "one", root / "cache", root)
                second = make_bundle("fpcfilter", component, root / "two", root / "cache", root)
            self.assertEqual(sha256(first), sha256(second))
            with tarfile.open(first, "r:gz") as archive:
                manifest = json.load(archive.extractfile("SOURCE-MANIFEST.json"))
                self.assertEqual(manifest["files"]["packaging/README.md"], hashlib.sha256(readme.read_bytes()).hexdigest())
                self.assertIn("README-SOURCE.txt", archive.getnames())
                self.assertTrue(all(member.mtime == 0 for member in archive))


if __name__ == "__main__":
    unittest.main()
