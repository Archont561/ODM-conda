#!/usr/bin/env python3
"""Inventory the exact retained build/host environments of a RenderDEM build.

Metadata is sanitized and does not establish package/source rights or license
compliance. The runtime solve used by a consumer is a separate environment.
"""
from __future__ import annotations

import re
from pathlib import Path

from common import ScaffoldError, find_package, sha256
from inventory_conda_environment import inventory


def capture(output: Path, component: dict) -> dict:
    builds = list((output / 'bld').glob('rattler-build_renderdem_*'))
    if len(builds) != 1 or not builds[0].is_dir() or builds[0].is_symlink():
        raise ScaffoldError('Expected exactly one retained RenderDEM build directory')
    build = builds[0] / 'build_env'
    hosts = list(builds[0].glob('host_env_*'))
    if len(hosts) != 1:
        raise ScaffoldError('Expected exactly one retained RenderDEM host environment')
    environments = {'build': inventory(build), 'host': inventory(hosts[0])}
    for env in environments.values():
        for record in env['packages']:
            if not isinstance(record.get('sha256'), str) or not re.fullmatch('[0-9a-f]{64}', record['sha256']):
                raise ScaffoldError('Build/host record lacks a SHA256 identity')
    package = find_package('renderdem', component, output)
    if package.is_symlink() or not package.is_file():
        raise ScaffoldError('Invalid RenderDEM build package')
    return {'schema_version': 1, 'component': 'renderdem', 'package': package.name,
            'package_sha256': sha256(package), 'environments': environments,
            'scope': 'Installed Conda build/host metadata from this build, not a runtime lock, source inventory, independent dependency archive verification, or legal review.'}
