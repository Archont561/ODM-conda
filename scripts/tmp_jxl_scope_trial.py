import base64
import json
import shutil
import tempfile
import urllib.request
from pathlib import Path
import yaml
from common import ROOT, sha256
from prepare_jxl_reduced_research import prepare
from prepare_jxl_vendor_scope import CRATE_SHA256, archive, prepare as transform
from private_odm_bundle import build_recipe, download_sdist
from source_graph import unpack_archive

with tempfile.TemporaryDirectory(prefix='jxl-vendor-scope-') as tmp:
    root=Path(tmp); info=yaml.safe_load((ROOT/'research/recipes/python-source-research/pillow-jxl-plugin.yaml').read_text())['source']
    sdist=root/'original.tar.gz'; download_sdist(info['url'],info['sha256'],sdist)
    crate=root/'jpegxl-src.crate'
    with urllib.request.urlopen('https://static.crates.io/crates/jpegxl-src/jpegxl-src-0.11.2.crate',timeout=90) as response:
        crate.write_bytes(response.read(100000000))
    assert sha256(crate)==CRATE_SHA256
    prepared=prepare(sdist,root/'prepared')
    fixture=(ROOT/'scripts/jxl_interop_fixture.py').read_bytes(); code=base64.b64encode(fixture).decode('ascii')
    recipe=prepared/'recipe/recipe.yaml'; text=recipe.read_text(); assert text.count('about:\n')==1
    test=("  - script:\n      interpreter: python\n      content: |\n"
          f"        ns = {{'__name__': 'jxl_interop'}}; exec(__import__('base64').b64decode('{code}'), ns)\n"
          "        ns['run'](__import__('pathlib').Path('/tmp/jxl-oxide-build/target/release/jxl-oxide'))\n"
          "    requirements:\n      run:\n        - python >=3.12,<3.13\n")
    recipe.write_text(text.replace('about:\n',test+'about:\n'))
    print('::notice::JXL-CARGO-META '+json.dumps(json.loads((prepared/'source/vendor/jpegxl-src-0.11.2/.cargo-checksum.json').read_text()) | {'files': 'omitted'},separators=(',',':')),flush=True)
    first=transform(prepared,crate,root/'first'); second=transform(prepared,crate,root/'second'); assert first==second
    a=root/'first.tar.gz'; b=root/'second.tar.gz'; archive(root/'first',a); archive(root/'second',b)
    assert sha256(a)==sha256(b); archive_hash=sha256(a)
    receiver=root/'receiver'; receiver.mkdir(); shutil.copyfile(a,receiver/'received.tar.gz')
    shutil.rmtree(prepared); shutil.rmtree(root/'first'); shutil.rmtree(root/'second'); sdist.unlink(); crate.unlink(); a.unlink(); b.unlink()
    received=receiver/'received.tar.gz'; assert sha256(received)==archive_hash
    unpack_archive(received,receiver/'tree' if False else receiver) # creates source and recipe under receiver
    assert json.loads((receiver/'VENDOR-SCOPE-MANIFEST.json').read_text())==first
    package=build_recipe(receiver/'recipe/recipe.yaml','odm-research-pillow-jxl-plugin',root/'build')
    print('::notice::JXL-SCOPED-HANDOFF '+json.dumps({'archive_sha256':archive_hash,'package':package.name,'package_sha256':sha256(package),'removed':len(first['removed']),'retained':len(first['retained']),'fixture_sha256':sha256(ROOT/'scripts/jxl_interop_fixture.py'),'original_checksum':first['original_vendor_checksum_sha256'],'modified_checksum':first['modified_vendor_checksum_sha256']},separators=(',',':')),flush=True)
