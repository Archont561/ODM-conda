"""Keep the recorded, bounded Cargo source evidence internally coherent."""
import hashlib
import json
import re
from pathlib import Path


def test_jxl_locked_crate_inventory_is_complete_and_anchored():
    path = Path(__file__).resolve().parents[1] / 'research/pillow-jxl-locked-crates-2026-11-11.json'
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == '21b48b27922396dd9f342d1e3504b0f2be1c1f015ed81c3a48c307973ba0373e'
    data = json.loads(raw)
    crates = data['crates']
    assert len(crates) == 40
    assert len({(entry['name'], entry['version']) for entry in crates}) == 40
    assert all(re.fullmatch(r'[0-9a-f]{64}', entry['sha256']) for entry in crates)
    assert all(entry['manifest_license'] and entry['notice_sha256'] for entry in crates)
    assert all(re.fullmatch(r'[0-9a-f]{64}', digest) for entry in crates for digest in entry['notice_sha256'].values())
    indexed = {entry['name']: entry for entry in crates}
    for name in ('jpegxl-rs', 'jpegxl-sys'):
        assert indexed[name]['manifest_license'] == 'GPL-3.0-or-later'
        assert any(line.startswith(name + ' v') for line in data['cargo_tree'])
