import hashlib
import json
import shutil
import tempfile
from pathlib import Path
import yaml

from common import ROOT, sha256
from package_archive import read_package
from prepare_jxl_reduced_research import prepare
from private_odm_bundle import build_recipe, download_sdist

with tempfile.TemporaryDirectory(prefix='jxl-source-review-') as temp:
    root=Path(temp); info=yaml.safe_load((ROOT/'research/recipes/python-source-research/pillow-jxl-plugin.yaml').read_text())['source']
    original=root/'input.tar.gz'; download_sdist(info['url'],info['sha256'],original)
    prepared=prepare(original, root/'prepared'); source=prepared/'source'
    evidence=json.loads((ROOT/'research/pillow-jxl-locked-crates-2026-11-11.json').read_text())
    counts=0; nested=[]; names=[]
    for item in evidence['crates']:
        crate=source/'vendor'/f"{item['name']}-{item['version']}"; metadata=json.loads((crate/'.cargo-checksum.json').read_text())
        assert metadata['package']==item['sha256'] and metadata['files']
        for path,digest in metadata['files'].items():
            f=crate/path
            assert f.is_file() and not f.is_symlink() and f.resolve().is_relative_to(crate.resolve()) and sha256(f)==digest, (item['name'],path)
            counts+=1
        for path,digest in item['notice_sha256'].items():
            assert sha256(crate/path)==digest, (item['name'],path)
        for f in crate.rglob('*'):
            if f.is_file() and f.parent!=crate and f.name.upper().startswith(('LICENSE','COPYING','NOTICE','COPYRIGHT')):
                nested.append(f'{item["name"]}:{f.relative_to(crate)}')
        names.append(item['name'])
    assert len(names)==40
    print('::notice::JXL-NOTICE '+json.dumps({'crates':len(names),'checked_vendor_files':counts,'nested_notice_candidates':len(nested),'nested_sample':nested[:12]},separators=(',',':')),flush=True)
    # Private source handoff: copy the prepared source tree and recipe, remove the originals,
    # rewrite only the generated recipe's absolute source path, then build with Cargo offline.
    moved=root/'relocated'; shutil.copytree(prepared,moved); shutil.rmtree(prepared); original.unlink()
    old=str(source.resolve()); new=str((moved/'source').resolve())
    recipe=moved/'recipe/recipe.yaml'; text=recipe.read_text(); assert text.count(old)==1; recipe.write_text(text.replace(old,new))
    package=build_recipe(recipe,'odm-research-pillow-jxl-plugin',root/'rebuild')
    info,payload=read_package(package)
    notices=sorted(p for p in [*info,*payload] if any(x in p.lower() for x in ('license','licence','notice','copying','copyright')))
    print('::notice::JXL-REBUILD '+json.dumps({'package':package.name,'sha256':sha256(package),'notices':notices,'license':json.loads(info['info/about.json'])['license']},separators=(',',':')),flush=True)
