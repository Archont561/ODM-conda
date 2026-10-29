"""Validate selected GNU link inputs; not a complete security or source audit."""
import hashlib
from pathlib import Path
import re

from common import ScaffoldError


def verify_poisson_link_map(path: Path, prefix: Path) -> dict:
    # Real Poisson link maps can exceed 190 MiB; never read the whole map at once.
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2 * 1024**3:
        raise ScaffoldError('Missing or unsafe PoissonRecon link map')
    markers = {'Memory Configuration', 'Linker script and memory map', 'OUTPUT('}
    seen = set()
    inputs = []
    digest = hashlib.sha256()
    forbidden = re.compile(r'libmypng|libpng[^/\s()]*\.a(?:\(|\b)|(?:^|/)PNG/[^\s]*\.o', re.IGNORECASE)
    try:
        with path.open('rb') as stream:
            for raw in stream:
                if len(raw) > 1024 * 1024:
                    raise ScaffoldError('Unreasonably long line in PoissonRecon link map')
                digest.update(raw)
                line = raw.decode('utf-8')
                seen.update(marker for marker in markers if marker in line)
                if forbidden.search(line):
                    raise ScaffoldError('Bundled or static PNG input found in link map')
                if line.startswith('LOAD '):
                    inputs.append(line[5:].strip())
    except (OSError, UnicodeError) as error:
        raise ScaffoldError('Cannot read PoissonRecon link map') from error
    if seen != markers:
        raise ScaffoldError('Incomplete PoissonRecon link map')
    if not any(Path(item).name == 'PoissonRecon.o' for item in inputs):
        raise ScaffoldError('Missing PoissonRecon object in link map')
    png = [item for item in inputs if re.fullmatch(r'libpng(?:16)?\.so(?:\.\d+)*', Path(item).name)]
    expected = prefix / 'lib' / 'libpng.so'
    if (len(png) != 1 or not expected.is_file() or Path(png[0]) != expected
            or expected.resolve().parent != (prefix / 'lib').resolve()):
        raise ScaffoldError('PoissonRecon must link host-prefix libpng.so')
    # Preserve a path-free inventory and hash; the raw map stays in the build tree.
    return {'map_sha256': digest.hexdigest(), 'link_inputs': [Path(item).name for item in inputs]}


def verify_poisson_package_evidence(evidence: object, needed: list[str]) -> None:
    if not isinstance(evidence, dict):
        raise ScaffoldError('Invalid PoissonRecon shared-libpng link evidence')
    digest = evidence.get('map_sha256')
    inputs = evidence.get('link_inputs')
    if (not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest)
            or not isinstance(inputs, list) or not all(isinstance(item, str) for item in inputs)
            or 'libpng.so' not in inputs or 'PoissonRecon.o' not in inputs
            or any('libmypng' in item.lower() or re.fullmatch(r'libpng[^/\\]*\.a', item, re.IGNORECASE)
                   or '/' in item or '\\' in item for item in inputs)
            or 'libpng16.so.16' not in needed):
        raise ScaffoldError('Invalid PoissonRecon shared-libpng link evidence')
