import json

import pytest

from capture_renderdem_build_inventory import capture
from common import ScaffoldError


def record(prefix, name='pkg', digest='a' * 64):
    metadata = prefix / 'conda-meta'
    metadata.mkdir(parents=True)
    (metadata / f'{name}.json').write_text(json.dumps({'name': name, 'version': '1', 'build': 'b', 'sha256': digest, 'url': 'https://user:secret@example.org/pkg.conda?token=secret'}))


def create_build(tmp_path):
    root = tmp_path / 'bld/rattler-build_renderdem_123'
    record(root / 'build_env')
    record(root / 'host_env_placehold')
    package_dir = tmp_path / 'linux-64'
    package_dir.mkdir()
    (package_dir / 'renderdem-1.0-h873e7db_1.conda').write_bytes(b'package')
    return root


def test_capture_sanitizes_and_identifies_package(tmp_path):
    create_build(tmp_path)
    result = capture(tmp_path, {'version': '1.0'})
    assert result['package'] == 'renderdem-1.0-h873e7db_1.conda'
    assert len(result['package_sha256']) == 64
    assert result['environments']['host']['packages'][0]['binary_package_url'] == 'https://example.org/pkg.conda'
    assert 'secret' not in json.dumps(result)


def test_capture_fails_on_ambiguous_or_missing_environment(tmp_path):
    root = create_build(tmp_path)
    (root / 'host_env_second').mkdir()
    with pytest.raises(ScaffoldError, match='exactly one'):
        capture(tmp_path, {'version': '1.0'})


def test_capture_rejects_missing_record_hash(tmp_path):
    root = create_build(tmp_path)
    path = root / 'build_env/conda-meta/pkg.json'
    item = json.loads(path.read_text())
    item['sha256'] = None
    path.write_text(json.dumps(item))
    with pytest.raises(ScaffoldError, match='SHA256'):
        capture(tmp_path, {'version': '1.0'})


def test_release_wires_inventory_before_binary_upload():
    import yaml
    from common import ROOT
    data = yaml.safe_load((ROOT / '.github/workflows/release.yml').read_text())
    build = data['jobs']['build']['steps']
    runs = [s.get('run', '') for s in build]
    assert 'pixi run build --component "$COMPONENT" --keep-renderdem-build' in runs
    assert 'pixi run stage-release --component "$COMPONENT" --capture-renderdem-inventory' in runs
    publish = data['jobs']['publish']['steps']
    checksum = next(s['run'] for s in publish if s.get('name') == 'Verify checksums and artifact counts')
    assert 'build-host-inventory[.]json' in checksum
    assert 'sha256sum --strict --check SHA256SUMS' in checksum
    source = next(i for i, s in enumerate(publish) if s.get('name') == 'Make source available BEFORE distributing the channel binary')
    upload = next(i for i, s in enumerate(publish) if s.get('name') == 'Publish to existing channel with OIDC and attestation')
    assert source < upload
    assert 'attach_once build-host-inventory.json' in publish[source]['run']
