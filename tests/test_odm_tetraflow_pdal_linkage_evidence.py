import json
from pathlib import Path


def test_private_stack_linkage_evidence_is_specific_and_scoped():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'research/odm-tetraflow-pdal-linkage-evidence.json').read_text())
    selected = {record['name']: record for record in data['selected_dependencies']}
    assert selected['libgdal-core']['version'] == '3.12.2'
    assert selected['libpdal-core']['version'] == '2.10.0'
    assert selected['hdf5']['version'] == '1.14.6'
    assert data['inventory_package_count'] == 432
    plugins = {record['name']: record for record in data['plugins']}
    assert len(plugins) == 17
    assert {'libpdal_plugin_reader_hdf.so', 'libpdal_plugin_reader_icebridge.so'} <= plugins.keys()
    assert all(not entry['missing'] and entry['ldd_returncode'] == 0 for entry in plugins.values())
    assert 'not full runtime' in data['scope']
