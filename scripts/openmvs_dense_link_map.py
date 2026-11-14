"""Check named link inputs for research dense/mesh binaries; not rights clearance."""
from pathlib import Path

from common import ScaffoldError, sha256


def verify_dense_link_map(path: Path, target: str) -> str:
    if target not in ('ReconstructMesh', 'DensifyPointCloud'):
        raise ScaffoldError('Unexpected dense research target')
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 128 * 1024 * 1024:
        raise ScaffoldError('Missing or unsafe OpenMVS link map')
    try:
        text = path.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as error:
        raise ScaffoldError('Cannot read OpenMVS link map') from error
    required = ('Memory Configuration', 'Linker script and memory map', 'libMVS.a',
                'libMath.a', f'{target}.cpp.o', 'OUTPUT(')
    if not all(marker in text for marker in required):
        raise ScaffoldError('Incomplete dense research link map')
    if target == 'DensifyPointCloud' and 'SceneDensify.cpp.o' not in text:
        raise ScaffoldError('Missing dense implementation link input')
    if target == 'ReconstructMesh' and 'SceneReconstruct.cpp.o' not in text:
        raise ScaffoldError('Missing mesh implementation link input')
    forbidden = ('ibfs', 'trws', 'mrfenergy', 'scenerefine.cpp.o', 'scenetexture.cpp.o')
    if any(marker in text.lower() for marker in forbidden):
        raise ScaffoldError('Restricted or excluded OpenMVS link input')
    return sha256(path)
