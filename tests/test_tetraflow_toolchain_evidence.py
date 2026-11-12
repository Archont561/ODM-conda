"""Cross-check the recorded evidence, not the original downloads or legal conclusions."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_selected_source_evidence_is_anchored_to_trial_inventory():
    inventory_path = ROOT / 'research/tetraflow-build-input-inventory.json'
    evidence = json.loads((ROOT / 'research/tetraflow-cgal-toolchain-evidence.json').read_text())
    assert hashlib.sha256(inventory_path.read_bytes()).hexdigest() == evidence['trial_inventory_sha256']
    inventory = json.loads(inventory_path.read_text())
    trial = {p['name']: p['sha256'] for group in ('build', 'host') for p in inventory[group]}
    records = evidence['binary_recipe_metadata']
    for name, record in records.items():
        assert record['binary_sha256'] == trial[name]
    expected = {
        'cgal': ('cgal-cpp', 0),
        'gcc-14': ('gcc_impl_linux-64', 0),
        'gcc-16': ('libgcc', 0),
        'binutils': ('binutils_impl_linux-64', 0),
        'zlib': ('gcc_impl_linux-64', 1),
    }
    assert set(evidence['downloaded_archive_checks']) == set(expected)
    for name, (package, index) in expected.items():
        sources = records[package]['sources']['info/recipe/meta.yaml']
        if isinstance(sources, dict):
            sources = [sources]
        assert evidence['downloaded_archive_checks'][name]['sha256'] == sources[index]['sha256']
    assert evidence['cgal_inventory_summary']['file_count'] == evidence['downloaded_archive_checks']['cgal']['counts']['files']
