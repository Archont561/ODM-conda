"""Keep the bounded native provenance evidence anchored and coherent."""
import hashlib
import json
from pathlib import Path


def test_native_review_inventory_matches_known_scope():
    root=Path(__file__).resolve().parents[1]
    path=root/'research/pillow-jxl-native-package-evidence.json'
    raw=path.read_bytes()
    assert hashlib.sha256(raw).hexdigest()=='5e507d4f5e3ab3f4dd13db8a3709e6e9073dec2dd4a660c030755edde4d550c5'
    data=json.loads(raw); records={x['name']:x for x in data['packages']}
    assert set(records)=={'libjxl','libhwy','libbrotlidec','libbrotlienc','libbrotlicommon','libgcc','libstdcxx'}
    assert data['run']==43086211426
    assert records['libjxl']['sha256']=='0c8a78c6a42a6e4c6de3a5e82d692f60400d43f4cc80591745f28b37daad9c70'
    assert len(records['libjxl']['source'])==3
    assert {'info/licenses/LICENSE','info/licenses/third_party/skcms/LICENSE'}==set(records['libjxl']['notices'])
    assert 'libbrotlidec.so.1' in records['libjxl']['elf_needed']['lib/libjxl.so.0.11.2']
    assert records['libstdcxx']['license']=='GPL-3.0-only WITH GCC-exception-3.1'
