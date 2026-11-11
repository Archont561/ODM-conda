#!/usr/bin/env python3
"""Run upstream TetraFlow's randomized reference test from a pinned private tree.

This does not build OpenMVS or test the PLY patch, and does not assess rights.
"""
from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

from common import ScaffoldError, fail_cli, sha256

FILES = {
    'apps/Tests/TestsMath.cpp': '72316717ecc52000627c8d43d58ee58d14bc80b764570356434274ecdf91bae9',
    'libs/Math/TetraFlow.h': 'dd3376a592b4c52321b8ab2130cfaadb0ed3b03980a0c7608ad9c98f73c2b380',
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Extracted, private pinned OpenMVS source tree')
    args = parser.parse_args()
    root = args.source.resolve()
    for name, expected in FILES.items():
        path = root / name
        if path.is_symlink() or not path.is_file() or sha256(path) != expected:
            raise ScaffoldError(f'Unexpected source input: {name}')
    original = (root / 'apps/Tests/TestsMath.cpp').read_text()
    expected_includes = ('#include "../../libs/Math/TetraFlow.h"', '#include "Tests.h"',
                         '#include "TestsMath.h"', '#include <random>')
    for include in expected_includes:
        if original.count(include) != 1:
            raise ScaffoldError('Unexpected upstream test includes')
        original = original.replace(include, '')
    preamble = '''#include <cassert>
#include <cmath>
#include <cstdio>
#include <random>
#define ASSERT(x) assert(x)
#define VERBOSE(...) do { std::fprintf(stderr, __VA_ARGS__); std::fputc('\\n', stderr); } while (0)
#include "TetraFlow.h"
'''
    with tempfile.TemporaryDirectory(prefix='tetraflow-reference-') as directory:
        temp = Path(directory)
        (temp / 'test.cpp').write_text(preamble + original + '\nint main() { return SEACAVE::TestTetraFlow() ? 0 : 1; }\n')
        subprocess.run(['g++', '-std=c++17', '-O2', '-Wall', '-Wextra', '-I', str(root / 'libs/Math'),
                        str(temp / 'test.cpp'), '-o', str(temp / 'test')], check=True, timeout=120)
        subprocess.run([str(temp / 'test')], check=True, timeout=120)
    print('PASS: pinned upstream 400 randomized TetraFlow reference comparisons')


if __name__ == '__main__':
    fail_cli(main)
