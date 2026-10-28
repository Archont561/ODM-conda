from __future__ import annotations

import hashlib
import io
import tarfile

import pytest

from common import ScaffoldError
from source_graph import stage_graph


def cached_archive(cache, name, members):
    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode="w:gz") as archive:
        for path, data in members:
            info = tarfile.TarInfo(path)
            if data is None:
                info.type = tarfile.SYMTYPE
                info.linkname = "/etc/passwd"
                archive.addfile(info)
            else:
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
    content = payload.getvalue()
    commit = ("a" if name == "main" else "b") * 40
    cache.mkdir(exist_ok=True)
    (cache / f"{name}-{commit}.tar.gz").write_bytes(content)
    return {"commit": commit, "sha256": hashlib.sha256(content).hexdigest(),
            "url": "https://example.invalid/archive"}


def test_stage_pinned_submodule_into_fresh_tree(tmp_path):
    cache = tmp_path / "cache"
    primary = cached_archive(cache, "main", [("main-root/CMakeLists.txt", b"project(main)"),
                                               ("main-root/sub/.gitkeep", b"")])
    nested = cached_archive(cache, "nested", [("nested-root/include/header.h", b"header")])
    nested.update(name="nested", path="third_party/nested")
    stage_graph("main", primary, [nested], cache, tmp_path / "staged")
    assert (tmp_path / "staged/CMakeLists.txt").read_bytes() == b"project(main)"
    assert (tmp_path / "staged/third_party/nested/include/header.h").read_bytes() == b"header"
    with pytest.raises(ScaffoldError, match="already exists"):
        stage_graph("main", primary, [nested], cache, tmp_path / "staged")


@pytest.mark.parametrize("members", [
    [("root/../../escape", b"x")],
    [("root/link", None)],
    [("root/file", b"x"), ("other/file", b"y")],
    [("root/file", b"x"), ("root/file", b"y")],
])
def test_invalid_archive_cannot_leave_partial_tree(tmp_path, members):
    cache = tmp_path / "cache"
    primary = cached_archive(cache, "main", members)
    with pytest.raises(ScaffoldError):
        stage_graph("main", primary, [], cache, tmp_path / "staged")
    assert not (tmp_path / "staged").exists()
    assert not list(tmp_path.glob(".source-stage-*"))


@pytest.mark.parametrize("path", ["../outside", "/absolute", "x/../../outside", "x\\outside", ""])
def test_unsafe_nested_destination_rejected(tmp_path, path):
    entry = {"name": "nested", "path": path}
    with pytest.raises(ScaffoldError, match="Unsafe staging path"):
        stage_graph("main", {}, [entry], tmp_path / "cache", tmp_path / "staged")


def test_nonempty_nested_destination_rejected(tmp_path):
    cache = tmp_path / "cache"
    primary = cached_archive(cache, "main", [("main-root/nested/file", b"original")])
    nested = cached_archive(cache, "nested", [("nested-root/file", b"new")])
    nested.update(name="nested", path="nested")
    with pytest.raises(ScaffoldError, match="not empty"):
        stage_graph("main", primary, [nested], cache, tmp_path / "staged")
    assert not (tmp_path / "staged").exists()


def test_overlapping_nested_destinations_rejected(tmp_path):
    entries = [{"name": "one", "path": "third_party"},
               {"name": "two", "path": "third_party/nested"}]
    with pytest.raises(ScaffoldError, match="Overlapping"):
        stage_graph("main", {}, entries, tmp_path / "cache", tmp_path / "staged")


def test_experimental_plans_are_explicit_and_commit_pinned(tmp_path):
    import json
    import re

    from common import ROOT, repository_files
    from stage_sources import load_plan

    assert ROOT / "research" / "source-graphs.json" in repository_files()
    assert ROOT / "research" / "README.md" in repository_files()
    path = ROOT / "research" / "source-graphs.json"
    document = json.loads(path.read_text())
    assert set(document["plans"]) == {"dem2mesh", "poissonrecon", "renderdem", "opensfm", "openmvs", "mvs-texturing"}
    for name in document["plans"]:
        plan = load_plan(path, name)
        for source in [plan["primary"], *plan["additional"]]:
            assert re.fullmatch(r"[0-9a-f]{40}", source["commit"])
            assert re.fullmatch(r"[0-9a-f]{64}", source["sha256"])
    with pytest.raises(ScaffoldError, match="Unknown experimental"):
        load_plan(path, "opendronemap")
    document["plans"]["opensfm"]["additional"][0]["url"] = "https://example.invalid/main"
    broken = tmp_path / "plans.json"
    broken.write_text(json.dumps(document))
    with pytest.raises(ScaffoldError, match="commit-pinned"):
        load_plan(broken, "opensfm")


def test_declared_git_submodule_must_be_staged(tmp_path):
    cache = tmp_path / "cache"
    modules = b'[submodule "dep"]\n\tpath = vendor/dep\n\turl = https://example.invalid/dep.git\n'
    primary = cached_archive(cache, "main", [("main-root/.gitmodules", modules)])
    with pytest.raises(ScaffoldError, match="Unstaged"):
        stage_graph("main", primary, [], cache, tmp_path / "missing")
    assert not (tmp_path / "missing").exists()
    nested = cached_archive(cache, "nested", [("nested-root/README", b"dep")])
    nested.update(name="nested", path="vendor/dep")
    stage_graph("main", primary, [nested], cache, tmp_path / "complete")
    assert (tmp_path / "complete/vendor/dep/README").read_bytes() == b"dep"


@pytest.mark.parametrize("content", [
    b'[submodule "dep"]\npath = ../../outside\n',
    b'[submodule "dep"]\nurl = https://example.invalid/dep\n',
    b'not an ini file',
])
def test_invalid_git_submodule_declarations_fail_closed(tmp_path, content):
    cache = tmp_path / "cache"
    primary = cached_archive(cache, "main", [("main-root/.gitmodules", content)])
    with pytest.raises(ScaffoldError):
        stage_graph("main", primary, [], cache, tmp_path / "staged")
    assert not (tmp_path / "staged").exists()


def test_experimental_texturing_patch_is_in_packaging_sources():
    from common import ROOT, repository_files, sha256

    patch = ROOT / "research" / "patches" / "mvs-texturing-offline.patch"
    assert patch in repository_files()
    assert sha256(patch) == "37d03ca8b5a50bd72b6e7a4ed2f2856e1d83c0355806f7fc9efa059f9a57ef65"
    text = patch.read_text()
    assert '-add_subdirectory(elibs)' in text
    assert '-include(ExternalProject)' in text
    assert '-add_dependencies(${LIBRARY} ext_rayint ext_eigen ext_mapmap)' in text
    assert '+        message(FATAL_ERROR "Missing staged dependency: ${required_source}")' in text
    assert '-    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -march=native' in text


def test_experimental_bundle_contains_every_archive_and_patch(tmp_path, monkeypatch):
    import json
    import bundle_staged_sources
    from common import sha256

    cache = tmp_path / "cache"
    primary = cached_archive(cache, "main", [("main-root/CMakeLists.txt", b"project(main)")])
    primary["name"] = "main"
    nested = cached_archive(cache, "nested", [("nested-root/README", b"nested")])
    nested.update(name="nested", path="vendor/nested")
    plan = {"primary": primary, "additional": [nested]}
    patch = tmp_path / "patches" / "offline.patch"
    patch.parent.mkdir()
    patch.write_text("experimental patch\n")
    monkeypatch.setattr(bundle_staged_sources, "repository_files", lambda root: [patch])
    first = bundle_staged_sources.bundle_plan("example", plan, cache, tmp_path / "one.tar.gz", tmp_path)
    second = bundle_staged_sources.bundle_plan("example", plan, cache, tmp_path / "two.tar.gz", tmp_path)
    assert sha256(first) == sha256(second)
    with tarfile.open(first, "r:gz") as archive:
        manifest = json.load(archive.extractfile("EXPERIMENTAL-MANIFEST.json"))
        assert manifest["status"] == "experimental; not a release source bundle"
        assert manifest["plan"] == plan
        assert archive.extractfile("packaging/patches/offline.patch").read() == patch.read_bytes()
        for source in (primary, nested):
            name = f"upstream/{source['name']}-{source['commit']}.tar.gz"
            contents = archive.extractfile(name).read()
            assert hashlib.sha256(contents).hexdigest() == source["sha256"]
            assert manifest["files"][name] == source["sha256"]
    with pytest.raises(ScaffoldError, match="already exists"):
        bundle_staged_sources.bundle_plan("example", plan, cache, first, tmp_path)
    (cache / f"nested-{nested['commit']}.tar.gz").write_bytes(b"tampered")
    with pytest.raises(ScaffoldError, match="checksum mismatch"):
        bundle_staged_sources.bundle_plan("example", plan, cache, tmp_path / "bad.tar.gz", tmp_path)
    assert not (tmp_path / "bad.tar.gz").exists()


def test_staging_rejects_git_metadata(tmp_path):
    primary = cached_archive(tmp_path / "cache", "main", [("root/.git/config", b"unsafe")])
    with pytest.raises(ScaffoldError, match="Unsafe source"):
        stage_graph("main", primary, [], tmp_path / "cache", tmp_path / "staged")
    assert not (tmp_path / "staged").exists()
