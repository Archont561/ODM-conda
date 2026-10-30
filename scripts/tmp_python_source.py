import hashlib
import subprocess
import tempfile
from pathlib import Path

root = Path.cwd()
with tempfile.TemporaryDirectory(prefix='odm-source-research-') as tmp:
    dest = Path(tmp)
    for recipe in sorted((root/'research/recipes/python-source-research').glob('*.yaml')):
        result = subprocess.run(['rattler-build','build','--recipe',str(recipe),'--target-platform','linux-64','--variant-config',str(root/'recipes/variants.yaml'),'--channel','conda-forge','--channel-priority','strict','--output-dir',str(dest),'--log-style','plain'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        print(result.stdout,flush=True)
        if result.returncode:
            print('::error::SOURCE BUILD FAILED '+result.stdout[-3500:].replace('\n',' | '),flush=True)
            result.check_returncode()
        matches=list((dest/'linux-64').glob('odm-research-'+recipe.stem+'-*.conda'))
        assert len(matches)==1
        result=subprocess.run(['rattler-build','test','--package-file',str(matches[0]),'--channel','conda-forge','--output-dir',str(dest/'retest'),'--log-style','plain'],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        print(result.stdout,flush=True)
        if result.returncode:
            print('::error::RETEST FAILED '+result.stdout[-3500:].replace('\n',' | '),flush=True)
            result.check_returncode()
        print('::notice::SOURCE BUILD PASS '+matches[0].name+' '+hashlib.sha256(matches[0].read_bytes()).hexdigest(),flush=True)
