import hashlib,json,re,subprocess,tarfile,tempfile,urllib.request
from pathlib import Path
payload=json.load(open('research/tetraflow-srpm-payload-evidence.json'))['source_rpms']
records={x['filename']:x for x in json.load(open('research/tetraflow-sysroot-rpm-evidence.json'))['source_rpm_checks']}
def extract(rpm,name,dest,expected):
 p=subprocess.Popen(['rpm2cpio',str(rpm)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 with dest.open('wb') as f:
  q=subprocess.run(['cpio','--quiet','-i','--to-stdout',name],stdin=p.stdout,stdout=f,stderr=subprocess.PIPE)
 p.stdout.close(); err=p.stderr.read(); rc=p.wait()
 if q.returncode or rc: raise ValueError('rpm2cpio/cpio failed '+str(err[:100]))
 h=hashlib.sha256()
 with dest.open('rb') as f:
  while b:=f.read(1024*1024): h.update(b)
 if h.hexdigest()!=expected: raise ValueError('member sha mismatch: '+name)
with tempfile.TemporaryDirectory() as tmp:
 d=Path(tmp)
 for record in payload:
  name=record['source_rpm']; rpm=d/'source.rpm'
  try:
   urllib.request.urlretrieve(records[name]['url'],rpm)
   if hashlib.sha256(rpm.read_bytes()).hexdigest()!=record['source_rpm_sha256']: raise ValueError('RPM hash mismatch')
   specname=next(iter(record['specs'])); spec=d/'spec'; extract(rpm,specname,spec,record['specs'][specname]['sha256'])
   text=spec.read_text(encoding='utf8'); lines=text.splitlines()
   patch_decls=[l.strip() for l in lines if re.match(r'^\s*Patch\d*\s*:',l,re.I)]
   prep=[l.strip() for l in lines if re.match(r'^\s*%(?:prep|setup|autosetup|autopatch|patch\d*)\b',l,re.I)]
   build=[l.strip() for l in lines if re.match(r'^\s*%(?:build|install|check)\b',l,re.I)]
   result={'source_rpm':name,'spec_sha256':record['specs'][specname]['sha256'],'patch_declaration_count':len(patch_decls),'patch_declaration_examples':patch_decls[:4], 'prep_directive_count':len(prep),'prep_examples':prep[:12], 'build_directives':build[:12],'nested_archives':[]}
   result['patch_samples']=[]
   for patch_name,patch_meta in sorted(record['sample_patches'].items()):
    patch_file=d/'patch'; extract(rpm,patch_name,patch_file,patch_meta['sha256'])
    text_patch=patch_file.read_text(encoding='utf8',errors='replace'); patch_lines=text_patch.splitlines()
    targets=[l[4:] for l in patch_lines if l.startswith('+++ ')][:20]
    result['patch_samples'].append({'name':patch_name,'sha256':patch_meta['sha256'],'targets':targets,'added_lines':sum(l.startswith('+') and not l.startswith('+++') for l in patch_lines),'removed_lines':sum(l.startswith('-') and not l.startswith('---') for l in patch_lines),'subject':next((l[:180] for l in patch_lines if l.startswith('Subject:')),None)})
    patch_file.unlink()
   archive_name=next(k for k in record['archives'] if k.startswith(('glibc-2.28.tar','linux-4.18.0-513.24.1')))
   archive=d/'nested'; extract(rpm,archive_name,archive,record['archives'][archive_name]['sha256'])
   counts={'files':0,'dirs':0,'links':0,'other':0}; roots=set(); notices=[]; unsafe=0
   with tarfile.open(archive,'r:*') as tar:
    for n,m in enumerate(tar):
     if n>1000000: raise ValueError('nested member limit')
     parts=Path(m.name).parts
     if m.name.startswith('/') or '..' in parts or '\\' in m.name: unsafe+=1
     roots.add(parts[0] if parts else '')
     if len(roots)>12: raise ValueError('unexpected roots')
     typ='files' if m.isfile() else 'dirs' if m.isdir() else 'links' if m.issym() or m.islnk() else 'other'; counts[typ]+=1
     base=Path(m.name).name.lower()
     if len(parts)<=2 and any(t in base for t in ('license','licence','copying','copyright','notice')): notices.append(m.name)
   result['nested_archives'].append({'name':archive_name,'sha256':record['archives'][archive_name]['sha256'],'counts':counts,'roots':sorted(roots),'unsafe_path_count':unsafe,'root_notice_candidates':notices[:30]})
   print('::notice::SPECRESULT '+json.dumps(result,sort_keys=True),flush=True)
  except Exception as e:
   print('::notice::SPECERROR '+json.dumps({'name':name,'error':str(e)[:250]}),flush=True)
  finally:
   for n in ('source.rpm','spec','nested'): (d/n).unlink(missing_ok=True)
