"""Check named inputs of one reduced OpenMVS link, not redistribution rights."""
from pathlib import Path

from common import ScaffoldError, sha256


def verify_openmvs_link_map(path: Path) -> str:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 128 * 1024 * 1024:
        raise ScaffoldError('Missing or unsafe OpenMVS link map')
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
        raise ScaffoldError('Cannot read OpenMVS link map') from error
    required = ('Memory Configuration', 'Linker script and memory map', 'libMVS.a',
                'libMath.a', 'ReconstructMesh.cpp.o', 'SceneReconstruct.cpp.o', 'OUTPUT(')
    if not all(marker in text for marker in required):
        raise ScaffoldError('incomplete or unrecognized OpenMVS link map')
    forbidden = ('ibfs', 'trws', 'mrfenergy', 'scenedensify.cpp.o', 'scenerefine.cpp.o',
                 'scenetexture.cpp.o')
    if any(marker in text.lower() for marker in forbidden):
        raise ScaffoldError('restricted or excluded OpenMVS input appears in link map')
    return sha256(path)
