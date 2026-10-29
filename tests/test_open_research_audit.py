"""Research artifacts must reject leaked sources even though they are never uploaded."""
import pytest

from common import ScaffoldError
from audit_open_research import verify_payload


def test_research_audit_rejects_unexpected_checkout_and_sources(monkeypatch):
    import audit_open_research as audit
    monkeypatch.setattr(audit, "OPENMVS_NOTICES", {})
    payload = {
        'bin/ReconstructMesh': b'\x7fELFbinary',
        'share/odm-conda/openmvs-odm/functional_test.py': b'test',
        'share/odm-conda/openmvs-odm/openmvs_synthetic_fixture.py': b'test',
        'share/odm-conda/openmvs-odm/openmvs_pointcloud_fixture.py': b'test',
        'share/odm-conda/openmvs-odm/openmvs_fixture.py': b'test',
        'share/odm-conda/openmvs-odm/texrecon_fixture.py': b'test',
        'share/odm-conda/openmvs-odm/SOURCE.txt': b'LOCAL RESEARCH ONLY',
        'share/licenses/openmvs-odm/packaging-MIT.txt': b'notice',
        'share/licenses/openmvs-odm/upstream-LICENSE.txt': b'notice',
    }
    verify_payload('openmvs-odm', payload)
    payload['share/odm-conda/openmvs-odm/.git/config'] = b'leaked'
    with pytest.raises(ScaffoldError, match='leak'):
        verify_payload('openmvs-odm', payload)


def test_research_package_identity_and_runtime_dependencies_fail_closed():
    from audit_open_research import verify_index

    index = {'name': 'opensfm-odm', 'version': '0.5.2', 'build_number': 5, 'subdir': 'linux-64',
             'depends': ['python >=3.12,<3.13', 'numpy', 'py-opencv >=4.12,<4.13',
                         'ceres-solver', 'suitesparse', 'gflags', 'glog', 'libgomp', 'rasterio', 'rawpy']}
    verify_index('opensfm-odm', index)
    for changed in ({**index, 'version': '9.9'}, {**index, 'build_number': 0},
                    {**index, 'depends': [d for d in index['depends'] if not d.startswith('numpy')]},
                    {**index, 'depends': 'python numpy'}, {**index, 'subdir': 'osx-arm64'}):
        with pytest.raises(ScaffoldError):
            verify_index('opensfm-odm', changed)
