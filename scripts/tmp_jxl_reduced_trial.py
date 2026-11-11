import json
import shutil
import tarfile
import tempfile
from pathlib import Path
from common import sha256
from jxl_reduced_candidate import EXCLUDED, make_candidate
from package_archive import read_package
from prepare_jxl_source import SOURCE_SHA256, prepare
from private_odm_bundle import build_recipe, download_sdist
from source_graph import unpack_archive

URL='https://files.pythonhosted.org/packages/0a/0e/77af926bdf99bac7f1decdca8102b13945a2e2aa9c716ce617e36bcd82d3/pillow_jxl_plugin-1.3.4.tar.gz'
with tempfile.TemporaryDirectory(prefix='jxl-reduced-trial-') as tmp:
    root=Path(tmp); original=root/'upstream.tar.gz'; download_sdist(URL,SOURCE_SHA256,original)
    candidate=root/'candidate.tar.gz'; result=make_candidate(original,candidate)
    unpack=root/'candidate';unpack.mkdir();unpack_archive(candidate,unpack)
    recorded=json.loads((unpack/'CANDIDATE-MANIFEST.json').read_text()); assert recorded==result
    for name, item in recorded['files'].items(): assert sha256(unpack/name)==item['sha256']
    assert not any((unpack/name).exists() for name in recorded['excluded_files'])
    prepared=prepare(original,root/'prepared'); source=prepared/'source'; reduced=root/'prepared-reduced';shutil.copytree(prepared,reduced)
    reduced_source=reduced/'source'
    for name, expected in EXCLUDED.items():
        path=reduced_source/'test/images'/name
        assert sha256(path)==expected
        path.unlink()
    for name, info in recorded['files'].items():
        if name != 'pyproject.toml': assert sha256(reduced_source/name)==info['sha256'], name
    recipe=reduced/'recipe/recipe.yaml'; text=recipe.read_text(); before=json.dumps(str(source.resolve())); after=json.dumps(str(reduced_source.resolve())); assert text.count(before)==1; recipe.write_text(text.replace(before,after))
    packages={}
    for label,path in (('original',prepared/'recipe/recipe.yaml'),('reduced',recipe)):
        pkg=build_recipe(path,'odm-research-pillow-jxl-plugin',root/label)
        info,payload=read_package(pkg)
        packages[label]={'name':pkg.name,'sha256':sha256(pkg),'payload':payload,'info':info}
    a=packages['original']['payload']; b=packages['reduced']['payload']
    changed=sorted(name for name in a.keys()|b.keys() if a.get(name)!=b.get(name))
    import hashlib
    elf={label:{name:hashlib.sha256(data).hexdigest() for name,data in p['payload'].items() if data[:4]==b'\x7fELF'} for label,p in packages.items()}
    summary={'original_source_sha256':SOURCE_SHA256,'candidate_sha256':sha256(candidate),'retained_count':len(recorded['files']),'excluded_count':len(EXCLUDED),'packages':{k:{key:v[key] for key in ('name','sha256')} for k,v in packages.items()},'payload_identical':not changed,'changed_payload_paths':changed,'elf_sha256':elf,'scope':'Temporary local-only experiment; no source, packages, image or outputs uploaded; not a source offer or legal approval.'}
    print('::notice::JXL-REDUCED '+json.dumps(summary,sort_keys=True,separators=(',',':')),flush=True)
