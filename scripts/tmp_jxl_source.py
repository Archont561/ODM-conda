import hashlib
import subprocess
import sys
import tempfile
import traceback
import urllib.request
from pathlib import Path
from prepare_jxl_source import prepare

sys.excepthook=lambda typ,val,tb: print('::error::'+''.join(traceback.format_exception(typ,val,tb)).replace('\n',' | '),flush=True)
root=Path.cwd()
with tempfile.TemporaryDirectory(prefix='odm-jxl-source-') as tmp:
    rootdir=Path(tmp)
    archive=rootdir/'source.tar.gz'
    urllib.request.urlretrieve('https://files.pythonhosted.org/packages/0a/0e/77af926bdf99bac7f1decdca8102b13945a2e2aa9c716ce617e36bcd82d3/pillow_jxl_plugin-1.3.4.tar.gz',archive)
    staged=prepare(archive,rootdir/'prepared')
    dest=rootdir/'output'
    args=['rattler-build','build','--recipe',str(staged/'recipe/recipe.yaml'),'--target-platform','linux-64','--variant-config',str(root/'recipes/variants.yaml'),'--channel','conda-forge','--channel-priority','strict','--output-dir',str(dest),'--log-style','plain']
    res=subprocess.run(args,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    print(res.stdout,flush=True)
    if res.returncode:
        print('::error::JPEG XL BUILD FAILED '+res.stdout[-3500:].replace('\n',' | '),flush=True)
        res.check_returncode()
    matches=list((dest/'linux-64').glob('odm-research-pillow-jxl-plugin-*.conda'));assert len(matches)==1
    # Inspect the packaged native extension rather than assuming its linkage.
    import zipfile, tarfile, zstandard
    with zipfile.ZipFile(matches[0]) as z:
        payload=next(n for n in z.namelist() if n.startswith('pkg-') and n.endswith('.tar.zst'))
        with z.open(payload) as src, zstandard.ZstdDecompressor().stream_reader(src) as stream, tarfile.open(fileobj=stream,mode='r|') as tar:
            extensions=[]
            for member in tar:
                if member.isfile() and member.name.endswith('.so') and 'pillow_jxl' in member.name:
                    target=rootdir/'jxl-extension.so'; target.write_bytes(tar.extractfile(member).read()); extensions.append(target)
            assert len(extensions)==1,extensions
    info=subprocess.check_output(['readelf','-d',str(extensions[0])],text=True)
    needed=[line.strip() for line in info.splitlines() if '(NEEDED)' in line]
    print('::notice::JPEG XL EXTENSION NEEDED '+'; '.join(needed),flush=True)
    assert any('[libjxl.so.' in line for line in needed),needed
    assert not any('libjxl-' in line for line in needed),needed
    res=subprocess.run(['rattler-build','test','--package-file',str(matches[0]),'--channel','conda-forge','--output-dir',str(rootdir/'retest'),'--log-style','plain'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    print(res.stdout,flush=True)
    if res.returncode:
        print('::error::JPEG XL RETEST FAILED '+res.stdout[-3500:].replace('\n',' | '),flush=True)
        res.check_returncode()
    print('::notice::JPEG XL SOURCE BUILD PASS '+matches[0].name+' '+hashlib.sha256(matches[0].read_bytes()).hexdigest(),flush=True)
