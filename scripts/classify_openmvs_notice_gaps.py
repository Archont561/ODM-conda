#!/usr/bin/env python3
"""Classify a prior OpenMVS notice comparison against the historical trace."""
import json
from pathlib import Path

from common import ROOT, ScaffoldError, fail_cli


def classify(comparison: dict, trace: dict) -> dict:
    paths = {entry['path'] for entry in trace['entries']}
    findings = []
    for path in comparison['unmatched']:
        if path == 'libs/Math/LMFit/COPYING':
            evidence = sorted(p for p in paths if p in {'libs/Math/LMFit/lmmin.cpp', 'libs/Math/LMFit/lmmin.h'})
            if len(evidence) != 2:
                raise ScaffoldError('Missing expected historical LMFit trace evidence')
            category = 'traced LMFit source; candidate notice to carry'
        elif path.startswith('_external/eigen/COPYING.'):
            evidence = sorted(p for p in paths if p.startswith('_external/eigen/Eigen/'))
            if not evidence:
                raise ScaffoldError('Missing historical Eigen trace evidence')
            category = 'root Eigen license candidate; traced Eigen headers, applicability unresolved'
        elif path.startswith('_external/eigen/bench/btl/'):
            evidence = sorted(p for p in paths if p.startswith('_external/eigen/bench/btl/'))
            category = 'benchmark tree; no matching historical traced path' if not evidence else 'benchmark tree; historical traced path'
        elif path.startswith('_external/eigen/unsupported/Eigen/src/LevenbergMarquardt/'):
            evidence = sorted(p for p in paths if p.startswith('_external/eigen/unsupported/Eigen/src/LevenbergMarquardt/'))
            category = 'unsupported Eigen module; no matching historical traced path' if not evidence else 'unsupported Eigen module; historical traced path'
        elif path.startswith('_external/vcg/eigenlib/unsupported/Eigen/src/LevenbergMarquardt/'):
            evidence = sorted(p for p in paths if p.startswith('_external/vcg/eigenlib/'))
            category = 'VCG embedded Eigen; no matching historical traced path' if not evidence else 'VCG embedded Eigen; historical traced path'
        elif path.startswith('_external/vcg/docs/ContributorLicenseAgreement.'):
            evidence = sorted(p for p in paths if p.startswith('_external/vcg/docs/'))
            category = 'contributor agreement document; no matching historical traced path' if not evidence else 'contributor agreement document; historical traced path'
        elif path == '_external/eigen/scripts/relicense.py':
            evidence = sorted(p for p in paths if p.startswith('_external/eigen/scripts/'))
            category = 'source maintenance script; no matching historical traced path' if not evidence else 'source maintenance script; historical traced path'
        else:
            raise ScaffoldError(f'Unclassified notice candidate: {path}')
        findings.append({'path': path, 'category': category, 'trace_path_count': len(evidence), 'sample_traced_paths': evidence[:5]})
    return {'scope': 'Prior filename inventory and historical trace only; trace absence is not proof of non-inclusion, legal applicability or complete notices.', 'comparison_package_sha256': comparison['package_sha256'], 'baseline_trace_entries': len(paths), 'findings': findings}


def main() -> None:
    comparison = json.loads((ROOT/'research/openmvs-package-notice-comparison.json').read_text())
    trace = json.loads((ROOT/'research/openmvs-notices.json').read_text())
    print(json.dumps(classify(comparison, trace), sort_keys=True, indent=2))


if __name__ == '__main__':
    fail_cli(main)
