import io, json, tarfile, zipfile
import pytest
import zstandard
from common import ScaffoldError
from private_conda_channel import create


def make_package(path, name='pkg'):
    index=json.dumps({'name':name,'version':'1','build':'b0','subdir':'linux-64','depends':[]}).encode()
    out=io.BytesIO()
    with tarfile.open(fileobj=out,mode='w') as t:
        info=tarfile.TarInfo('info/index.json'); info.size=len(index); t.addfile(info,io.BytesIO(index))
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('metadata.json','{"conda_pkg_format_version":2}')
        z.writestr('info-pkg.tar.zst',zstandard.ZstdCompressor().compress(out.getvalue()))
        z.writestr('pkg-pkg.tar.zst',b'not inspected')


def test_channel_hashes_and_does_not_mutate_package(tmp_path):
    package=tmp_path/'pkg-1-b0.conda'; make_package(package)
    report=create([package],tmp_path/'channel',root=tmp_path/'repository')
    info=json.loads((tmp_path/'channel/linux-64/repodata.json').read_text())['packages.conda'][package.name]
    assert info['sha256']==report[0]['sha256'] and (tmp_path/'channel/linux-64'/package.name).read_bytes()==package.read_bytes()
    assert json.loads((tmp_path/'channel/noarch/repodata.json').read_text())['packages.conda']=={}
    with pytest.raises(ScaffoldError): create([package],tmp_path/'channel',root=tmp_path/'repository')


def test_channel_refuses_duplicate_and_filename_mismatch(tmp_path):
    package=tmp_path/'bad-1-b0.conda'; make_package(package)
    with pytest.raises(ScaffoldError): create([package],tmp_path/'bad',root=tmp_path/'repository')
    assert not (tmp_path/'bad').exists()
