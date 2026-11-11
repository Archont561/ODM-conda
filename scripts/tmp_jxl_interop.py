import base64
import tempfile
from pathlib import Path
import yaml
from common import ROOT, sha256
from private_odm_bundle import build_recipe, download_sdist
from prepare_jxl_reduced_research import prepare

with tempfile.TemporaryDirectory(prefix='jxl-interop-') as tmp:
    work=Path(tmp)
    info=yaml.safe_load((ROOT/'research/recipes/python-source-research/pillow-jxl-plugin.yaml').read_text())['source']
    source=work/'source.tar.gz'; download_sdist(info['url'], info['sha256'], source)
    prepare(source,work/'prepared')
    recipe=work/'prepared/recipe/recipe.yaml'; text=recipe.read_text()
    fixture=(ROOT/'scripts/jxl_interop_fixture.py').read_bytes()
    decoder=Path('/tmp/jxl-oxide-build/target/release/jxl-oxide')
    assert decoder.is_file()
    code=base64.b64encode(fixture).decode('ascii')
    test=("  - script:\n      interpreter: python\n      content: |\n"
          f"        ns = {{'__name__': 'jxl_interop'}}; exec(__import__('base64').b64decode('{code}'), ns)\n"
          f"        ns['run'](__import__('pathlib').Path({str(decoder)!r}))\n"
          "    requirements:\n      run:\n        - python >=3.12,<3.13\n")
    assert text.count('about:\n') == 1
    recipe.write_text(text.replace('about:\n',test+'about:\n'))
    package=build_recipe(recipe,'odm-research-pillow-jxl-plugin',work/'build')
    print(f'::notice::INTEROP package={package.name} sha256={sha256(package)} fixture_sha256={sha256(ROOT/"scripts/jxl_interop_fixture.py")} decoder_commit=f8ae722ef2d6b782941c89517d19cfbf605c4a9d',flush=True)
