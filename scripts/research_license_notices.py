"""Copy and verify a narrow notice subset, not a legal completeness review."""
from pathlib import Path
import shutil
from typing import Mapping

from common import ScaffoldError, sha256

OPENMVS_NOTICES = {
    'openmvs-COPYRIGHT.md': ('COPYRIGHT.md', '43cfebf3c7ca2b5d2120cff54a7146136e86960ab99f16fa9e5c8e0a21c1b354'),
    'vcg-LICENSE.txt': ('_external/vcg/LICENSE.txt', '589ed823e9a84c56feb95ac58e7cf384626b9cbf4fda2a907bc36e103de1bad2'),
    'eigen-COPYING.MPL2.txt': ('_external/eigen/COPYING.MPL2', 'fab3dd6bdab226f1c08630b1dd917e11fcb4ec5e1e020e2c16f83a0a13863e85'),
    'eigen-COPYING.README.txt': ('_external/eigen/COPYING.README', 'c83230b770f17ef1386ea1fd3681271dd98aa93646bdbfb5bff3a1b7050fff9d'),
}
OPENSFM_NOTICES = {
    'pybind11-LICENSE.txt': ('opensfm/src/third_party/pybind11/LICENSE', '83965b843b98f670d3a85bd041ed4b372c8ec50d7b4a5995a83ac697ba675dcb'),
    'akaze-LICENSE.txt': ('opensfm/src/third_party/akaze/LICENSE', '6cc8c0423679fc8c8e6d7e6b180c32ed3fa31bc5b5c1ae48fb842bec7e2a075f'),
    'vlfeat-COPYING.txt': ('opensfm/src/third_party/vlfeat/COPYING', '33b9f7703327199088d74f884b19997a0084180f984724720095a7cb412c4d89'),
    'sensor-data-notice.txt': ('opensfm/data/sensor_data.readme.txt', 'f46b641594d0a183c69554dbcdf47c2eae25a44fb9b7f1414a2b67ff8928bc1a'),
}
PSUTIL_NOTICE_SHA256 = '24c12984500caa07ffdce19eebc06396c5e6d244b573bc6c438f4a6ef8e56c1b'


def copy_notices(notices: Mapping[str, tuple[Path, str]], target: Path) -> None:
    for name, (path, digest) in notices.items():
        if Path(name).name != name or path.is_symlink() or not path.is_file() or sha256(path) != digest:
            raise ScaffoldError(f'Missing or modified research notice: {name}')
        shutil.copy2(path, target / name)


def verify_notices(payload: Mapping[str, bytes], expected: Mapping[str, str]) -> None:
    import hashlib

    for name, digest in expected.items():
        raw = payload.get(name)
        if raw is None or hashlib.sha256(raw).hexdigest() != digest:
            raise ScaffoldError(f'Missing or modified research notice: {name}')
