#!/usr/bin/env python3
"""Inventory notice-like names in one exact reduced research tree, not legal review."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli, sha256
from openmvs_reduced_tree import EXPECTED_REDUCED_TREE
from openmvs_graph_policy import fingerprint_tree


def inventory(tree: Path, baseline: Path = ROOT / 'research/openmvs-notices.json') -> dict:
    tree = Path(tree)
    if fingerprint_tree(tree) != EXPECTED_REDUCED_TREE:
        raise ScaffoldError('Unexpected reduced OpenMVS source fingerprint')
    recorded = json.loads(baseline.read_text())['entries']
    matched, missing, changed = [], [], []
    for item in recorded:
        path = tree / item['path']
        if not path.is_file():
            missing.append(item['path'])
        elif sha256(path) != item['sha256']:
            changed.append({'path': item['path'], 'old_sha256': item['sha256'], 'sha256': sha256(path)})
        else:
            matched.append(item['path'])
    names = []
    for path in sorted(tree.rglob('*')):
        if path.is_file() and any(token in path.name.lower() for token in ('license', 'licence', 'copyright', 'copying', 'notice')):
            names.append({'path': path.relative_to(tree).as_posix(), 'sha256': sha256(path)})
    cgal = json.loads((ROOT / 'research/openmvs-cgal-gpl-header-trace.json').read_text())
    return {'scope': 'local-research-only; filename heuristic and prior trace are not complete notices, dependency sources, or license clearance',
            'reduced_tree_sha256': EXPECTED_REDUCED_TREE[1], 'retained_files': EXPECTED_REDUCED_TREE[0],
            'baseline_sha256': sha256(baseline), 'baseline_count': len(recorded), 'baseline_matched': len(matched),
            'baseline_missing': missing, 'baseline_changed': changed, 'notice_name_candidates': names,
            'host_trace': {'cgal_package': cgal['host_package'], 'cgal_package_sha256': cgal['host_package_sha256'],
                           'cgal_gpl_or_commercial_paths': len(cgal['paths']), 'trace_sha256': sha256(ROOT / 'research/openmvs-cgal-gpl-header-trace.json'),
                           'limitations': 'Prior Ninja header trace only; does not establish linked code, entire dependency sources or obligations.'}}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(inventory(args.tree), sort_keys=True, indent=2))


if __name__ == '__main__':
    fail_cli(main)
