"""Temporary read-only native candidate verification; no artifact uploads."""
import hashlib,json,os,subprocess,tempfile,zipfile
from pathlib import Path
import yaml
from common import config
from package_archive import read_package
from audit_package import audit

ROOT=Path.cwd()
ARTIFACTS=[(12910914634,'fff273a42ac145811f36447824fc86e03820d13b6a6efd2f04111992100970a2'),(12911564893,'2e6af14e3eaffa0631c59e875fa114b95376f17a1c7c7de4815e9fc3e7eefb87')]
PACKAGES={'fastrasterfilter':'52d42537b1ed1ba80a473e4540392d90f49f95e7e6dbb930445c9a3307f859dd','odm-orthophoto':'093c55b75981239cb31dccaf66e44e9a4d2addcfe37e31950870451d2f0bb58f','dem2points':'f7077c2eb01f380503d2aa5203e20d78e824a1c4adceaa486f4cbaf22bee8cb0'}

def command(*args):
    result=subprocess.run([str(a) for a in args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    if result.returncode:
        print('::error::'+result.stdout[-7000:].replace('\n',' | '),flush=True)
        result.check_returncode()
    return result.stdout

def main():
  with tempfile.TemporaryDirectory() as temp:
    root=Path(temp); files={}
    for artifact,digest in ARTIFACTS:
      zipped=root/f'{artifact}.zip'
      with zipped.open('wb') as out:
        subprocess.run(['gh','api',f'repos/Archont561/ODM-conda/actions/artifacts/{artifact}/zip'],stdout=out,check=True)
      assert hashlib.sha256(zipped.read_bytes()).hexdigest()==digest
      with zipfile.ZipFile(zipped) as z:
        for name in z.namelist():
          for component in PACKAGES:
            if name.startswith('output/linux-64/'+component+'-') and name.endswith('.conda'):
              p=root/Path(name).name; p.write_bytes(z.read(name)); files[component]=p
    assert set(files)==set(PACKAGES)
    for name,p in files.items():
      assert hashlib.sha256(p.read_bytes()).hexdigest()==PACKAGES[name]
      result=audit(name,config()['components'][name],p)
      info,payload=read_package(p)
      notices=sorted(x for x in payload if x.startswith('share/licenses/'))
      print('::notice::PACKAGE '+json.dumps({'name':name,'sha256':PACKAGES[name],'needed':result['elf_needed'],'rpath':result['rpath'],'notices':notices,'payload':sorted(payload)},sort_keys=True),flush=True)
      project=root/name
      command('pixi','init','--format','pixi','--scm','github','-c','conda-forge','-p','linux-64',project)
      command('pixi','add','--manifest-path',project/'pixi.toml','--no-install',p)
      lock=yaml.safe_load((project/'pixi.lock').read_text())
      records=lock['packages']
      items=[]
      for row in records:
        url=row.get('conda','')
        if url.startswith('https://conda.anaconda.org/conda-forge/'):
          items.append([url.rsplit('/',1)[-1],row.get('sha256'),row.get('license')])
      print('::notice::SOLVE '+json.dumps({'component':name,'records':items},separators=(',',':')),flush=True)
if __name__=='__main__':main()
