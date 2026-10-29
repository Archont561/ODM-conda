"""Poisson's link evidence must reject the bundled PNG archive."""
import pytest

from common import ScaffoldError
from poisson_linkage import verify_poisson_link_map, verify_poisson_package_evidence


def test_link_map_requires_host_shared_png_and_rejects_bundled_archive(tmp_path):
    prefix = tmp_path / 'host'
    (prefix / 'lib').mkdir(parents=True)
    (prefix / 'lib/libpng.so').write_bytes(b'host library')
    link_map = tmp_path / 'link.map'
    text = (f'Memory Configuration\nLinker script and memory map\n'
            f'LOAD Bin/Linux/PoissonRecon.o\nLOAD {prefix}/lib/libpng.so\nOUTPUT(Bin/Linux/PoissonRecon elf64-x86-64)\n')
    link_map.write_text(text)
    result = verify_poisson_link_map(link_map, prefix)
    assert result['map_sha256'] and 'libpng.so' in result['link_inputs']
    for bad in (text + 'LOAD Bin/Linux/libmypng.a\n',
                text + 'Bin/Linux/libmypng.a(pngread.o)\n',
                text.replace(str(prefix), '/untrusted'),
                text.replace('libpng.so', 'libpng.a'),
                text.replace('PoissonRecon.o', 'other.o')):
        link_map.write_text(bad)
        with pytest.raises(ScaffoldError):
            verify_poisson_link_map(link_map, prefix)


def test_map_rejects_missing_truncated_or_escaping_host_library(tmp_path):
    prefix = tmp_path / 'host'
    (prefix / 'lib').mkdir(parents=True)
    link_map = tmp_path / 'link.map'
    with pytest.raises(ScaffoldError):
        verify_poisson_link_map(link_map, prefix)
    link_map.write_text('LOAD Bin/Linux/PoissonRecon.o\n')
    with pytest.raises(ScaffoldError):
        verify_poisson_link_map(link_map, prefix)
    external = tmp_path / 'outside.so'
    external.write_bytes(b'outside')
    (prefix / 'lib/libpng.so').symlink_to(external)
    link_map.write_text(f'Memory Configuration\nLinker script and memory map\nLOAD Bin/Linux/PoissonRecon.o\nLOAD {prefix}/lib/libpng.so\nOUTPUT(a.out)\n')
    with pytest.raises(ScaffoldError, match='host-prefix'):
        verify_poisson_link_map(link_map, prefix)


def test_real_gnu_link_map(tmp_path):
    import shutil
    import subprocess

    cc = shutil.which('gcc')
    if not cc:
        pytest.skip('gcc not available')
    host = tmp_path / 'host'
    (host / 'lib').mkdir(parents=True)
    (tmp_path / 'png.c').write_text('int sample_png(void) {return 4;}\n')
    (tmp_path / 'main.c').write_text('int sample_png(void); int main(void) {return sample_png();}\n')
    subprocess.run([cc, '-fPIC', '-shared', str(tmp_path / 'png.c'), '-o', str(host / 'lib/libpng.so')], check=True)
    subprocess.run([cc, '-c', str(tmp_path / 'main.c'), '-o', str(tmp_path / 'PoissonRecon.o')], check=True)
    path = tmp_path / 'real.map'
    subprocess.run([cc, str(tmp_path / 'PoissonRecon.o'), f'-L{host}/lib', '-lpng', f'-Wl,-Map={path}', '-o', str(tmp_path / 'a.out')], check=True)
    assert 'libpng.so' in verify_poisson_link_map(path, host)['link_inputs']


def test_packaged_evidence_requires_dynamic_png_and_safe_inventory():
    evidence = {'map_sha256': 'a' * 64, 'link_inputs': ['PoissonRecon.o', 'libpng.so']}
    verify_poisson_package_evidence(evidence, ['libpng16.so.16'])
    for bad, needed in ((evidence, []),
                        ({**evidence, 'link_inputs': ['PoissonRecon.o', 'libmypng.a', 'libpng.so']}, ['libpng16.so.16']),
                        ({**evidence, 'link_inputs': ['PoissonRecon.o', '/tmp/libpng.so']}, ['libpng16.so.16']),
                        ({**evidence, 'map_sha256': 'bad'}, ['libpng16.so.16'])):
        with pytest.raises(ScaffoldError):
            verify_poisson_package_evidence(bad, needed)
