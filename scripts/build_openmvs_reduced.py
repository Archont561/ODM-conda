#!/usr/bin/env python3
"""Build OpenMVS from a validated reduced tree, for private research only."""
from build_open_research import main
from common import fail_cli

if __name__ == '__main__':
    fail_cli(lambda: main(reduced_openmvs=True))
