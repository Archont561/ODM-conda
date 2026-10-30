#!/usr/bin/env python3
"""Compare notice-candidate hashes against a private OpenMVS package."""
import argparse
import hashlib
import json
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, sha256
from audit_open_research import verify_index, verify_payload
from package_archive import read_package


def compare(info: dict[str, bytes], payload: dict[str, bytes], inventory: dict) -> dict:
    verify_index('openmvs-odm', json.loads(info['info/index.json']))
    verify_payload('openmvs-odm', payload)
    entries = inventory['notice_name_candidates']
    package_notices = {p: hashlib.sha256(b).hexdigest() for p, b in payload.items() if p.startswith('share/licenses/openmvs-odm/')}
    conda_notices = {p: hashlib.sha256(b).hexdigest() for p, b in info.items() if p.startswith('info/licenses/')}
    result = []
    for entry in entries:
        digest = entry['sha256']
        result.append({'source_path': entry['path'], 'sha256': digest,
                       'payload_matches': sorted(p for p, h in package_notices.items() if h == digest),
                       'metadata_matches': sorted(p for p, h in conda_notices.items() if h == digest)})
    return {'scope': 'local-research-only; byte equality is not an obligation or legal completeness determination',
            'inventory_tree_sha256': inventory['reduced_tree_sha256'], 'candidates': result,
            'package_license_files': package_notices, 'conda_license_files': conda_notices}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, required=True)
    args = parser.parse_args()
    info, payload = read_package(args.package)
    report = compare(info, payload, json.loads((ROOT / 'research/openmvs-reduced-notice-inventory.json').read_text()))
    report['package_sha256'] = sha256(args.package)
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == '__main__':
    fail_cli(main)
