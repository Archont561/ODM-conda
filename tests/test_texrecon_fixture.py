from __future__ import annotations

import pytest


def test_fixture_rejects_program_that_does_not_create_outputs(tmp_path):
    from pathlib import Path
    from texrecon_fixture import test_texrecon

    with pytest.raises(AssertionError):
        test_texrecon(Path('/bin/true'), tmp_path)


def test_fixture_rejects_success_message_without_model(tmp_path):
    from texrecon_fixture import test_texrecon

    executable = tmp_path / 'fake-texrecon'
    executable.write_text('#!/bin/sh\necho "0 faces have not been seen"\n', encoding='ascii')
    executable.chmod(0o755)
    working = tmp_path / 'work'
    working.mkdir()
    with pytest.raises(AssertionError, match='Missing generated OBJ or material'):
        test_texrecon(executable, working)


def test_fixture_rejects_truncated_texture(tmp_path):
    from texrecon_fixture import test_texrecon

    executable = tmp_path / 'fake-texrecon'
    executable.write_text('''#!/usr/bin/env python3
from pathlib import Path
import struct
p = Path('result')
p.joinpath('model.obj').write_text('mtllib model.mtl\\nv -1 -1 4\\nv 1 -1 4\\nv 1 1 4\\nv -1 1 4\\nvt 0 0\\nusemtl tex\\nf 1/1 3/1 2/1\\nf 1/1 4/1 3/1\\n')
p.joinpath('model.mtl').write_text('newmtl tex\\nmap_Kd model.png\\n')
p.joinpath('model.png').write_bytes(b'\\x89PNG\\r\\n\\x1a\\n' + struct.pack('>I', 13) + b'IHDR' + struct.pack('>II', 64, 64) + b'0' * 10)
print('0 faces have not been seen')
''', encoding='ascii')
    executable.chmod(0o755)
    working = tmp_path / 'work'
    working.mkdir()
    with pytest.raises(AssertionError, match='Invalid PNG texture'):
        test_texrecon(executable, working)
