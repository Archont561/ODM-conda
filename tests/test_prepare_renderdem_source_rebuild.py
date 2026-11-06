import hashlib
import io
import json
import tarfile

import pytest

from common import ScaffoldError
from prepare_renderdem_source_rebuild import prepare


def digest(data):
    return hashlib.sha256(data).hexdigest()


def add(tar, name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    tar.addfile(info, io.BytesIO(data))


def bundle(tmp_path, *, alter=False, extra=False, unsafe=False):
    source_data = io.BytesIO()
    with tarfile.open(fileobj=source_data, mode='w:gz') as tar:
        add(tar, 'upstream/CMakeLists.txt', b'project(renderdem)')
    raw = source_data.getvalue()
    commit = 'a' * 40
    recipe = (f'context:\n  source_sha256: "{digest(raw)}"\nsource:\n'
              f'  url: https://codeload.github.com/OpenDroneMap/RenderDEM/tar.gz/{commit}\n'
              '  sha256: ${{ source_sha256 }}\n').encode()
    files = {'packaging/recipes/renderdem/recipe.yaml': recipe,
             'packaging/scripts/build_component.py': b'# builder\n',
             'upstream/renderdem.tar.gz': raw}
    manifest = {'schema_version': 1, 'component': 'renderdem',
                'upstream': {'commit': commit, 'sha256': digest(raw)},
                'files': {name: digest(value) for name, value in files.items()}}
    path = tmp_path / 'source.tar.gz'
    with tarfile.open(path, 'w:gz') as tar:
        for name, value in files.items():
            add(tar, name, b'changed' if alter and name.endswith('build_component.py') else value)
        add(tar, 'SOURCE-MANIFEST.json', json.dumps(manifest).encode())
        add(tar, 'README-SOURCE.txt', b'source')
        if extra:
            add(tar, 'packaging/unlisted', b'extra')
        if unsafe:
            add(tar, '../escape', b'escape')
    return path


def test_prepare_local_source_recipe(tmp_path):
    archive = bundle(tmp_path)
    result = prepare(archive, digest(archive.read_bytes()), tmp_path / 'staged')
    assert '  path: ' in result.read_text()
    assert '  url:' not in result.read_text()
    assert (tmp_path / 'staged/upstream-source/CMakeLists.txt').read_bytes() == b'project(renderdem)'
    assert (tmp_path / 'staged/packaging/scripts/build_component.py').read_bytes() == b'# builder\n'


@pytest.mark.parametrize('options', [{'alter': True}, {'extra': True}, {'unsafe': True}])
def test_rejects_invalid_bundle(tmp_path, options):
    archive = bundle(tmp_path, **options)
    with pytest.raises(ScaffoldError):
        prepare(archive, digest(archive.read_bytes()), tmp_path / 'staged')
    assert not (tmp_path / 'staged').exists()


def test_requires_trusted_digest_and_fresh_destination(tmp_path):
    archive = bundle(tmp_path)
    with pytest.raises(ScaffoldError):
        prepare(archive, '0' * 64, tmp_path / 'staged')
    destination = tmp_path / 'staged'
    destination.mkdir()
    (destination / 'keep').write_text('keep')
    with pytest.raises(ScaffoldError):
        prepare(archive, digest(archive.read_bytes()), destination)
    assert (destination / 'keep').read_text() == 'keep'
