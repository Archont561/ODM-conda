from __future__ import annotations

import copy

import pytest

from common import ROOT, ScaffoldError, config, fetch_pinned_archive, first_comment, relative_path, release_tag, select_components, source_archive, source_url
from lint import check_repository
from release_guard import reviewed_component


def test_manifest_and_recipe_invariants():
    assert check_repository() == 8


def test_only_implemented_components_are_buildable():
    assert set(select_components("all")) == {"dem2mesh", "dem2points", "fastrasterfilter", "fpcfilter", "mvs-texturing-odm", "odm-orthophoto", "renderdem", "poissonrecon-odm"}
    for name in ("opendronemap", "opensfm-odm", "../fpcfilter", "all; echo unsafe"):
        with pytest.raises(ScaffoldError):
            select_components(name)


def test_paths_reject_traversal_absolute_and_windows_forms(tmp_path):
    assert relative_path(tmp_path, "safe/file") == (tmp_path / "safe/file").resolve()
    for value in ("../escape", "/absolute", "safe/../../escape", "\\windows", ""):
        with pytest.raises(ScaffoldError):
            relative_path(tmp_path, value)


def test_paths_reject_escaping_symlink(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "link").symlink_to(tmp_path)
    with pytest.raises(ScaffoldError):
        relative_path(root, "link/elsewhere")


def test_original_notice_is_not_rewritten():
    assert first_comment(b"\n  /* Copyright X\nTerms. */\nint main(){}") == b"/* Copyright X\nTerms. */\n"
    with pytest.raises(ScaffoldError):
        first_comment(b"// not a complete block notice")
    with pytest.raises(ScaffoldError):
        first_comment(b"/* unterminated")


def test_unreviewed_release_is_blocked():
    data = copy.deepcopy(config())
    for name, component in data["components"].items():
        component["release_checks"] = {key: False for key in component["release_checks"]}
        with pytest.raises(ScaffoldError, match="blocked"):
            reviewed_component(release_tag(name, component), data)


def test_all_release_gates_are_required_and_are_booleans():
    data = copy.deepcopy(config())
    name = "fpcfilter"
    component = data["components"][name]
    tag = release_tag(name, component)
    for key in component["release_checks"]:
        component["release_checks"][key] = True
    assert reviewed_component(tag, data)[0] == name
    for key in component["release_checks"]:
        component["release_checks"][key] = False
        with pytest.raises(ScaffoldError, match="blocked"):
            reviewed_component(tag, data)
        component["release_checks"][key] = "true"
        with pytest.raises(ScaffoldError):
            reviewed_component(tag, data)
        component["release_checks"][key] = True


def test_tags_are_exact():
    data = copy.deepcopy(config())
    for component in data["components"].values():
        component["release_checks"] = {key: True for key in component["release_checks"]}
    for bad in ("v3.6.2", "fpcfilter-v0.2", "fpcfilter-v0.2-b0", "fpcfilter-v0.2-b2", "fpcfilter-v0.2-b1\nanything"):
        with pytest.raises(ScaffoldError):
            reviewed_component(bad, data)


def test_source_url_has_exact_release_asset():
    component = config()["components"]["fpcfilter"]
    assert source_url("fpcfilter", component) == (
        "https://github.com/Archont561/ODM-conda/releases/download/fpcfilter-v0.2-b1/source-fpcfilter-0.2-b1.tar.gz"
    )


def test_cached_archive_is_always_rehashed(tmp_path):
    component = config()["components"]["dem2points"]
    (tmp_path / f"dem2points-{component['source']['commit']}.tar.gz").write_bytes(b"corrupt source")
    with pytest.raises(ScaffoldError, match="checksum mismatch"):
        source_archive("dem2points", component, tmp_path)


def test_external_graph_is_not_silently_omitted(tmp_path):
    component = copy.deepcopy(config()["components"]["dem2points"])
    component["source"]["additional_sources"] = [{"repository": "nested"}]
    with pytest.raises(ScaffoldError, match="not implemented"):
        source_archive("dem2points", component, tmp_path)


def test_individual_pinned_archive_cache_is_checked(tmp_path):
    import hashlib

    content = b"nested source archive bytes"
    source = {"commit": "a" * 40, "sha256": hashlib.sha256(content).hexdigest(),
              "url": "https://example.invalid/archive"}
    target = tmp_path / ("pybind11-" + source["commit"] + ".tar.gz")
    target.write_bytes(content)
    assert fetch_pinned_archive("pybind11", source, tmp_path) == target
    target.write_bytes(b"tampered")
    with pytest.raises(ScaffoldError, match="checksum mismatch"):
        fetch_pinned_archive("pybind11", source, tmp_path)


@pytest.mark.parametrize("name,commit", [
    ("../nested", "a" * 40), ("nested/source", "a" * 40),
    ("nested", "../outside"), ("nested", "HEAD"),
])
def test_pinned_archive_rejects_unsafe_cache_keys(tmp_path, name, commit):
    source = {"commit": commit, "sha256": "0" * 64, "url": "https://example.invalid/archive"}
    with pytest.raises(ScaffoldError):
        fetch_pinned_archive(name, source, tmp_path)


def test_pinned_archive_download_rejects_wrong_bytes_and_cleans_temporary_file(tmp_path, monkeypatch):
    import io
    import urllib.request

    class Response(io.BytesIO):
        url = "https://example.invalid/archive"

    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: Response(b"wrong bytes"))
    source = {"commit": "a" * 40, "sha256": "0" * 64, "url": "https://example.invalid/archive"}
    with pytest.raises(ScaffoldError, match="checksum mismatch"):
        fetch_pinned_archive("nested", source, tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_pinned_archive_rejects_insecure_redirect(tmp_path, monkeypatch):
    import io
    import urllib.request

    class Response(io.BytesIO):
        url = "http://example.invalid/archive"

    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: Response(b"bytes"))
    source = {"commit": "a" * 40, "sha256": "0" * 64, "url": "https://example.invalid/archive"}
    with pytest.raises(ScaffoldError, match="redirected away from HTTPS"):
        fetch_pinned_archive("nested", source, tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_source_fetch_refuses_symlink_cache_entry(tmp_path):
    import hashlib

    content = b"valid bytes"
    source = {"commit": "a" * 40, "sha256": hashlib.sha256(content).hexdigest(),
              "url": "https://example.invalid/archive"}
    outside = tmp_path / "outside"
    outside.write_bytes(content)
    (tmp_path / ("nested-" + source["commit"] + ".tar.gz")).symlink_to(outside)
    with pytest.raises(ScaffoldError, match="symlinked"):
        fetch_pinned_archive("nested", source, tmp_path)
