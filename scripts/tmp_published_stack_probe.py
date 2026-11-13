import base64,gzip,json,re,subprocess,tempfile
from pathlib import Path
import private_odm_bundle as mod
from common import sha256
from run_private_odm_workflow import DATASET_URL,DATASET_COMMIT,download_crate

PUBLISHED={
 'fpcfilter':('fpcfilter-v0.2-b1','fpcfilter-0.2-h873e7db_1.conda','8d3949bf9fdb570e30afbcd91174ee5f80e9b8cd06525a26899642bc5ed1e679'),
 'dem2points':('dem2points-v0.0.0.dev20220721-b2','dem2points-0.0.0.dev20220721-h873e7db_2.conda','d7876edf091b2990e1b9325e0f6cd0ae2a4e863ab5499edacf267e5d3fd4996f'),
 'fastrasterfilter':('fastrasterfilter-v1.0-b2','fastrasterfilter-1.0-h873e7db_2.conda','2738b09958d6b57360065ca5e68b1bcbe96a6f5c727cd0e3cdba1f8b018096c4'),
}
old_build=mod.build_recipe
old_configure=mod.configure_odm_research_recipe
with tempfile.TemporaryDirectory(prefix='odm-published-probe-') as temp:
 root=Path(temp); dataset=root/'seneca'; crate=root/'jpegxl-src.crate'; released=root/'released'; released.mkdir()
 subprocess.run(['git','init',str(dataset)],check=True)
 subprocess.run(['git','-C',str(dataset),'fetch','--depth=1',DATASET_URL,DATASET_COMMIT],check=True)
 subprocess.run(['git','-C',str(dataset),'checkout','--detach','FETCH_HEAD'],check=True)
 if subprocess.check_output(['git','-C',str(dataset),'rev-parse','HEAD'],text=True).strip()!=DATASET_COMMIT: raise ValueError('dataset mismatch')
 download_crate(crate)
 for tag,filename,digest in PUBLISHED.values():
  subprocess.run(['gh','release','download',tag,'--repo','Archont561/ODM-conda','--pattern',filename,'--dir',str(released)],check=True)
  if sha256(released/filename)!=digest: raise ValueError('published package mismatch: '+filename)
 def build_recipe(recipe,name,work,**kwargs):
  if name in PUBLISHED:
   tag,filename,digest=PUBLISHED[name]; package=work/'output'/'linux-64'/filename; package.parent.mkdir(parents=True)
   import shutil; shutil.copyfile(released/filename,package)
   if sha256(package)!=digest: raise ValueError('copied package mismatch')
   return package
  return old_build(recipe,name,work,**kwargs)
 def configure(recipe,**kwargs):
  old_configure(recipe,**kwargs)
  text=recipe.read_text()
  for name,(_,filename,_) in PUBLISHED.items():
   build='h873e7db_1' if name=='fpcfilter' else 'h873e7db_2'
   pat=rf'^(    - {re.escape(name)} ==[^\n ]+) research_\*$'
   text,count=re.subn(pat,lambda m:m.group(1)+' '+build,text,flags=re.M)
   if count!=1: raise ValueError('unexpected ODM dependency '+name)
  before='  number: 5\n  string: research_tetraflow_${{ hash }}_5'
  after='  number: 6\n  string: research_published_tetraflow_${{ hash }}_6'
  if text.count(before)!=1: raise ValueError('unexpected ODM identity')
  recipe.write_text(text.replace(before,after))
 mod.build_recipe=build_recipe; mod.configure_odm_research_recipe=configure
 bundle=root/'bundle'
 mod.build(bundle,mod.PORT,dataset,runtime_profile='reduced',reduced_jxl=True,vendor_scope_crate=crate,openmvs_variant='tetraflow')
 inv=json.loads((bundle/'conda-inventory.json').read_text())
 records={p['name']:p for p in inv['packages'] if p['name'] in PUBLISHED}
 if set(records)!=set(PUBLISHED): raise ValueError('missing selected published package')
 for name,rec in records.items():
  if rec['sha256']!=PUBLISHED[name][2] or rec['build'] not in ('h873e7db_1','h873e7db_2'): raise ValueError('selected package mismatch: '+name)
 report={'scope':'ephemeral research integration with three exact previously published binaries; not a release solve, rights or full ODM approval', 'dataset_commit':DATASET_COMMIT, 'records':[{k:p[k] for k in ('name','version','build','sha256')} for p in sorted(records.values(),key=lambda x:x['name'])], 'total_inventory_count':len(inv['packages']), 'inventory_sha256':sha256(bundle/'conda-inventory.json'),'lock_sha256':sha256(bundle/'pixi.lock'),'manifest_sha256':sha256(bundle/'private-bundle.json')}
 data=base64.b64encode(gzip.compress(json.dumps(report,sort_keys=True).encode(),mtime=0)).decode()
 for i in range(0,len(data),1800): print('::notice::RECORD%03d '%(i//1800)+data[i:i+1800],flush=True)
