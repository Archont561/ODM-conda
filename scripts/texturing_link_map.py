"""Fail closed on missing GNU link-map evidence for the texturing executable.

This checks named inputs to one link; it does not decide patent rights, prove
that equivalent code is absent elsewhere, or clear the full source archives.
"""
from pathlib import Path

from common import ScaffoldError, sha256


def verify_texturing_link_map(path: Path) -> str:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 128 * 1024 * 1024:
        raise ScaffoldError('Missing or unsafe texturing link map')
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
        raise ScaffoldError('Cannot read texturing link map') from error
    required = ('Memory Configuration', 'Linker script and memory map',
                'libmve.a', 'libmve_util.a', 'texrecon.cpp.o', 'OUTPUT(')
    if not all(marker in text for marker in required):
        raise ScaffoldError('incomplete or unrecognized texturing link map')
    if any(marker in text for marker in ('libmve_sfm.a', 'sift.cc.o', 'surf.cc.o')):
        raise ScaffoldError('SIFT/SURF archive or object appears in texturing link map')
    return sha256(path)
