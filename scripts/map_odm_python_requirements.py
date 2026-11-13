#!/usr/bin/env python3
"""Compare pinned upstream Python requirements with research recipe declarations.

Name mapping is an inventory aid, not proof that Conda identities, versions,
transitive dependencies, imports, or licenses match upstream requirements.
"""
import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
ALIASES = {
    'pillow-jxl-plugin': 'odm-research-pillow-jxl-plugin',
    'pyodm': 'odm-research-pyodm',
    'pysolar': 'odm-research-pysolar',
    'pygltflib': 'odm-research-pygltflib',
    'codem': 'odm-research-codem',
}


def normalized(name):
    return re.sub(r'[-_.]+', '-', name).lower()


def compare(inventory, recipe):
    direct = {}
    for spec in recipe['requirements']['run']:
        match = re.match(r'^\s*([A-Za-z0-9_.-]+)', spec)
        if not match:
            raise ValueError(f'Unrecognized run requirement: {spec}')
        key = normalized(match.group(1))
        if key in direct:
            raise ValueError(f'Duplicate run requirement: {key}')
        direct[key] = spec
    result = []
    for item in inventory['requirements']:
        name = normalized(item['name'])
        candidate = ALIASES.get(name, name)
        result.append({'upstream_name': item['name'], 'upstream_version': item['version'],
                       'candidate_name': candidate, 'research_run_spec': direct.get(candidate),
                       'status': 'declared-directly' if candidate in direct else 'not-declared-directly'})
    return {'source_commit': inventory['source_commit'], 'requirements': result,
            'scope': 'name-based research recipe comparison only; not a solve, transitive inventory, version equivalence, or release approval'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', type=Path, default=ROOT/'research/odm-full-scope-source-inventory.json')
    parser.add_argument('--recipe', type=Path, default=ROOT/'research/recipes/odm-fast-research/recipe.yaml')
    args = parser.parse_args()
    print(json.dumps(compare(json.loads(args.inventory.read_text()), yaml.safe_load(args.recipe.read_text())), indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
