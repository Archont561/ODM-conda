import hashlib
import sys
import traceback
sys.excepthook = lambda typ,value,tb: print("::error::" + " ".join(traceback.format_exception(typ,value,tb)).replace("\n", " | "),flush=True)
import subprocess
import tempfile
from pathlib import Path

root=Path.cwd()
with tempfile.TemporaryDirectory(prefix='odm-wheel-research-') as tmp:
    dest=Path(tmp)
    for recipe in [root/'research/recipes/python-wheel-research/pillow-jxl-plugin.yaml']:
        result = subprocess.run(['rattler-build','build','--recipe',str(recipe),'--target-platform','linux-64','--variant-config',str(root/'recipes/variants.yaml'),'--channel','conda-forge','--channel-priority','strict','--output-dir',str(dest),'--log-style','plain'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        print(result.stdout,flush=True)
        if result.returncode:
            print('::error::BUILD FAILED '+result.stdout[-3500:].replace('\n',' | '),flush=True)
            result.check_returncode()
        name='odm-research-'+recipe.stem
        result=list((dest/'linux-64').glob(name+'-*.conda'))
        assert len(result)==1,(name,result)
        subprocess.run(['rattler-build','test','--package-file',str(result[0]),'--channel','conda-forge','--output-dir',str(dest/'retest'),'--log-style','plain'],check=True)
        print('::notice::WHEEL REPACK PASS '+result[0].name+' '+hashlib.sha256(result[0].read_bytes()).hexdigest(),flush=True)
# Re-run after dependency correction.
