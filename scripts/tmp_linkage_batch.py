import json,re,subprocess,tarfile,tempfile,zipfile
from pathlib import Path
import zstandard
from conda_build_provenance import inspect

packages=list(Path('/tmp/odm-tetra-link').glob('linux-64/openmvs-tetraflow-research-*.conda'))
if len(packages)!=1: raise ValueError('unexpected packages')
package=packages[0]; meta=inspect(package); old=json.loads(Path('research/tetraflow-build-input-inventory.json').read_text())
with tempfile.TemporaryDirectory() as tmp:
 binary=Path(tmp)/'ReconstructMesh'
 with zipfile.ZipFile(package) as z:
  member=next(n for n in z.namelist() if n.startswith('pkg-') and n.endswith('.tar.zst'))
  with z.open(member) as f, zstandard.ZstdDecompressor().stream_reader(f) as zr, tarfile.open(fileobj=zr,mode='r|') as tar:
   matches=0
   for m in tar:
    if m.name=='bin/ReconstructMesh' and m.isfile() and m.size<256*1024*1024:
     binary.write_bytes(tar.extractfile(m).read());matches+=1
   if matches!=1: raise ValueError('missing or duplicate binary')
 dynamic=subprocess.check_output(['readelf','-d',str(binary)],text=True)
 versions=subprocess.check_output(['readelf','-V',str(binary)],text=True)
 needed=re.findall(r'\(NEEDED\).*?\[(.*?)\]',dynamic)
 glibc=sorted(set(re.findall(r'\bGLIBC_\d+(?:\.\d+)+\b',versions)))
 names=('sysroot_linux-64','kernel-headers_linux-64','gcc_impl_linux-64','libgcc','cgal-cpp')
 def pick(x): return {p['name']:p['sha256'] for k in ('build','host') for p in x[k] if p['name'] in names}
 result={'package':meta['output'],'needed':needed,'glibc_version_names':glibc,'selected_binary_inputs':pick(meta),'previous_trial_selected_inputs':pick(old),'scope':'one fresh research output; ELF metadata, not full runtime dependency or static linkage proof'}
 print('::notice::LINKRESULT '+json.dumps(result,sort_keys=True),flush=True)
