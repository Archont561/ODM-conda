"""Poisson's link evidence must reject the bundled PNG archive."""
import pytest

from common import ScaffoldError
from poisson_linkage import verify_poisson_link_map, verify_poisson_package_evidence


def test_link_map_requires_host_shared_png_and_rejects_bundled_archive(tmp_path):
    prefix = tmp_path / 'host'
    (prefix / 'lib').mkdir(parents=True)
    (prefix / 'lib/libpng.so').write_bytes(b'host library')
    (prefix / 'lib/libjpeg.so').write_bytes(b'host jpeg')
    link_map = tmp_path / 'link.map'
    text = (f'Memory Configuration\nLinker script and memory map\n'
            f'LOAD Bin/Linux/PoissonRecon.o\nLOAD {prefix}/lib/libpng.so\nLOAD {prefix}/lib/libjpeg.so\nOUTPUT(Bin/Linux/PoissonRecon elf64-x86-64)\n')
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
    (prefix / 'lib/libjpeg.so').write_bytes(b'host jpeg')
    external = tmp_path / 'outside.so'
    external.write_bytes(b'outside')
    (prefix / 'lib/libpng.so').symlink_to(external)
    link_map.write_text(f'Memory Configuration\nLinker script and memory map\nLOAD Bin/Linux/PoissonRecon.o\nLOAD {prefix}/lib/libpng.so\nLOAD {prefix}/lib/libjpeg.so\nOUTPUT(a.out)\n')
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
    (tmp_path / 'jpeg.c').write_text('int sample_jpeg(void) {return 3;}\n')
    (tmp_path / 'main.c').write_text('int sample_png(void); int sample_jpeg(void); int main(void) {return sample_png()+sample_jpeg();}\n')
    subprocess.run([cc, '-fPIC', '-shared', str(tmp_path / 'png.c'), '-o', str(host / 'lib/libpng.so')], check=True)
    subprocess.run([cc, '-fPIC', '-shared', str(tmp_path / 'jpeg.c'), '-o', str(host / 'lib/libjpeg.so')], check=True)
    subprocess.run([cc, '-c', str(tmp_path / 'main.c'), '-o', str(tmp_path / 'PoissonRecon.o')], check=True)
    path = tmp_path / 'real.map'
    subprocess.run([cc, str(tmp_path / 'PoissonRecon.o'), f'-L{host}/lib', '-lpng', '-ljpeg', f'-Wl,-Map={path}', '-o', str(tmp_path / 'a.out')], check=True)
    assert 'libpng.so' in verify_poisson_link_map(path, host)['link_inputs']


def test_packaged_evidence_requires_dynamic_png_and_safe_inventory():
    evidence = {'map_sha256': 'a' * 64, 'link_inputs': ['PoissonRecon.o', 'libpng.so', 'libjpeg.so']}
    verify_poisson_package_evidence(evidence, ['libpng16.so.16', 'libjpeg.so.8'])
    for bad, needed in ((evidence, []),
                        ({**evidence, 'link_inputs': ['PoissonRecon.o', 'libmypng.a', 'libpng.so']}, ['libpng16.so.16', 'libjpeg.so.8']),
                        ({**evidence, 'link_inputs': ['PoissonRecon.o', '/tmp/libpng.so']}, ['libpng16.so.16', 'libjpeg.so.8']),
                        ({**evidence, 'map_sha256': 'bad'}, ['libpng16.so.16', 'libjpeg.so.8'])):
        with pytest.raises(ScaffoldError):
            verify_poisson_package_evidence(bad, needed)


@pytest.mark.parametrize('extra', ['libpng.a', 'libpng16.a', 'LIBPNG16.A', 'libmypng.a'])
def test_packaged_evidence_rejects_static_png_even_with_shared_png(extra):
    evidence = {'map_sha256': 'a' * 64, 'link_inputs': ['PoissonRecon.o', 'libpng.so', extra]}
    with pytest.raises(ScaffoldError, match='shared-libpng'):
        verify_poisson_package_evidence(evidence, ['libpng16.so.16', 'libjpeg.so.8'])


def test_jpeg_link_map_requires_prefix_shared_library_and_rejects_static_and_bundled(tmp_path):
    prefix = tmp_path / 'host'
    (prefix / 'lib').mkdir(parents=True)
    for name in ('libpng.so', 'libjpeg.so'):
        (prefix / 'lib' / name).write_bytes(b'host library')
    link_map = tmp_path / 'link.map'
    text = (f'Memory Configuration\nLinker script and memory map\n'
            f'LOAD Bin/Linux/PoissonRecon.o\nLOAD {prefix}/lib/libpng.so\n'
            f'LOAD {prefix}/lib/libjpeg.so\nOUTPUT(a.out)\n')
    link_map.write_text(text)
    assert 'libjpeg.so' in verify_poisson_link_map(link_map, prefix)['link_inputs']
    for bad in (text.replace(f'LOAD {prefix}/lib/libjpeg.so\n', ''),
                text.replace(str(prefix / 'lib/libjpeg.so'), '/untrusted/libjpeg.so'),
                text + 'LOAD JPEG/jchuff.o\n', text + 'LOAD Bin/Linux/libjpeg.a\n',
                text + 'LOAD Bin/Linux/libjpeg.a(jchuff.o)\n'):
        link_map.write_text(bad)
        with pytest.raises(ScaffoldError):
            verify_poisson_link_map(link_map, prefix)
    (prefix / 'lib/libjpeg.so').unlink()
    outside = tmp_path / 'outside.so'
    outside.write_bytes(b'outside')
    (prefix / 'lib/libjpeg.so').symlink_to(outside)
    link_map.write_text(text)
    with pytest.raises(ScaffoldError):
        verify_poisson_link_map(link_map, prefix)


def test_package_jpeg_evidence_is_fail_closed():
    evidence = {'map_sha256': 'b'*64, 'link_inputs': ['PoissonRecon.o', 'libpng.so', 'libjpeg.so']}
    needed = ['libpng16.so.16', 'libjpeg.so.8']
    verify_poisson_package_evidence(evidence, needed)
    for bad, deps in ((evidence, ['libpng16.so.16']),
                      ({**evidence, 'link_inputs': ['PoissonRecon.o', 'libpng.so']}, needed),
                      ({**evidence, 'link_inputs': evidence['link_inputs'] + ['libjpeg.a']}, needed),
                      ({**evidence, 'link_inputs': evidence['link_inputs'] + ['LIBJPEG.A']}, needed)):
        with pytest.raises(ScaffoldError):
            verify_poisson_package_evidence(bad, deps)
