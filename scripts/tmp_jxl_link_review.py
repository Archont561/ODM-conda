import json
import os
import subprocess
import tempfile
from pathlib import Path
from common import sha256
from package_archive import read_package
from prepare_jxl_source import prepare, SOURCE_SHA256
from private_odm_bundle import build_recipe, download_sdist
URL='https://files.pythonhosted.org/packages/0a/0e/77af926bdf99bac7f1decdca8102b13945a2e2aa9c716ce617e36bcd82d3/pillow_jxl_plugin-1.3.4.tar.gz'
with tempfile.TemporaryDirectory(prefix='jxl-link-review-') as tmp:
    root=Path(tmp); src=root/'source.tar.gz'; download_sdist(URL,SOURCE_SHA256,src); prepare(src,root/'prepared')
    source=root/'prepared/source'
    for name in ('jpegxl-rs-0.11.2+libjxl-0.11.1','jpegxl-sys-0.11.2+libjxl-0.11.1'):
        file=source/'vendor'/name/'LICENSE'; text=file.read_text()
        assert len(text)<5000
        print('::notice::CRATE-LICENSE '+json.dumps({'crate':name,'sha256':sha256(file),'text':text},separators=(',',':')),flush=True)
    package=build_recipe(root/'prepared/recipe/recipe.yaml','odm-research-pillow-jxl-plugin',root/'build')
    info,payload=read_package(package)
    libs=[(p,b) for p,b in payload.items() if b[:4]==b'\x7fELF']
    assert len(libs)==1, [p for p,_ in libs]
    name,data=libs[0]; elf=root/'extension.so'; elf.write_bytes(data)
    dynamic=subprocess.check_output(['readelf','-d',str(elf)],text=True)
    lines=[x.strip() for x in dynamic.splitlines() if any(k in x for k in ('NEEDED','RPATH','RUNPATH'))]
    notice=[p for p in info|payload if 'license' in p.lower() or 'copying' in p.lower() or 'notice' in p.lower()]
    print('::notice::JXL-LINK '+json.dumps({'package':package.name,'sha256':sha256(package),'elf':name,'elf_sha256':sha256(elf),'dynamic':lines,'notice_paths':sorted(notice)},sort_keys=True,separators=(',',':')),flush=True)
