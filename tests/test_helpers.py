from __future__ import annotations

import copy
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from common import ROOT, ScaffoldError, config, first_comment, relative_path, release_tag, select_components, source_archive, source_url
from lint import check_repository
from release_guard import reviewed_component


class HelperTests(unittest.TestCase):
    def test_manifest_and_recipe_invariants(self):
        self.assertEqual(check_repository(), 2)

    def test_only_implemented_components_are_buildable(self):
        self.assertEqual(set(select_components("all")), {"dem2points", "fpcfilter"})
        for name in ("opendronemap", "opensfm-odm", "../fpcfilter", "all; echo unsafe"):
            with self.assertRaises(ScaffoldError):
                select_components(name)

    def test_paths_reject_traversal_absolute_and_windows_forms(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(relative_path(root, "safe/file"), root / "safe/file")
            for value in ("../escape", "/absolute", "safe/../../escape", "\\windows", ""):
                with self.assertRaises(ScaffoldError):
                    relative_path(root, value)

    def test_paths_reject_escaping_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "root"
            root.mkdir()
            (root / "link").symlink_to(Path(directory))
            with self.assertRaises(ScaffoldError):
                relative_path(root, "link/elsewhere")

    def test_original_notice_is_not_rewritten(self):
        self.assertEqual(first_comment(b"\n  /* Copyright X\nTerms. */\nint main(){}"), b"/* Copyright X\nTerms. */\n")
        with self.assertRaises(ScaffoldError):
            first_comment(b"// not a complete block notice")
        with self.assertRaises(ScaffoldError):
            first_comment(b"/* unterminated")

    def test_unreviewed_release_is_blocked(self):
        data = copy.deepcopy(config())
        for name, component in data["components"].items():
            component["release_checks"] = {key: False for key in component["release_checks"]}
            with self.assertRaisesRegex(ScaffoldError, "blocked"):
                reviewed_component(release_tag(name, component), data)

    def test_all_release_gates_are_required_and_are_booleans(self):
        data = copy.deepcopy(config())
        name = "fpcfilter"
        component = data["components"][name]
        tag = release_tag(name, component)
        for key in component["release_checks"]:
            component["release_checks"][key] = True
        self.assertEqual(reviewed_component(tag, data)[0], name)
        for key in component["release_checks"]:
            component["release_checks"][key] = False
            with self.assertRaisesRegex(ScaffoldError, "blocked"):
                reviewed_component(tag, data)
            component["release_checks"][key] = "true"
            with self.assertRaises(ScaffoldError):
                reviewed_component(tag, data)
            component["release_checks"][key] = True

    def test_tags_are_exact(self):
        data = copy.deepcopy(config())
        for component in data["components"].values():
            component["release_checks"] = {key: True for key in component["release_checks"]}
        for bad in ("v3.6.2", "fpcfilter-v0.2", "fpcfilter-v0.2-b0", "fpcfilter-v0.2-b2", "fpcfilter-v0.2-b1\nanything"):
            with self.assertRaises(ScaffoldError):
                reviewed_component(bad, data)

    def test_source_url_has_exact_release_asset(self):
        component = config()["components"]["fpcfilter"]
        self.assertEqual(source_url("fpcfilter", component),
                         "https://github.com/Archont561/ODM-conda/releases/download/fpcfilter-v0.2-b1/source-fpcfilter-0.2-b1.tar.gz")

    def test_cached_archive_is_always_rehashed(self):
        component = config()["components"]["dem2points"]
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            (cache / f"dem2points-{component['source']['commit']}.tar.gz").write_bytes(b"corrupt source")
            with self.assertRaisesRegex(ScaffoldError, "checksum mismatch"):
                source_archive("dem2points", component, cache)

    def test_external_graph_is_not_silently_omitted(self):
        component = copy.deepcopy(config()["components"]["dem2points"])
        component["source"]["additional_sources"] = [{"repository": "nested"}]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ScaffoldError, "not implemented"):
                source_archive("dem2points", component, Path(directory))


if __name__ == "__main__":
    unittest.main()
