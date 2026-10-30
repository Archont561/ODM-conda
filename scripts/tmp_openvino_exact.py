import hashlib,json,tarfile,zipfile,tempfile,urllib.request,os
import zstandard,yaml
from pathlib import Path
records=json.loads(Path('research/odm-private-lock-replay-inventory.json').read_text())['conda_inventory']['packages']
records=[x for x in records if 'openvino' in x['name']]
assert len(records)==13
out=[]
for p in records:
    with tempfile.TemporaryDirectory() as tmp:
        f=Path(tmp)/'p.conda';h=hashlib.sha256()
        with urllib.request.urlopen(p['binary_package_url'],timeout=120) as r,f.open('wb') as o:
            while b:=r.read(1024*1024): h.update(b);o.write(b)
        assert h.hexdigest()==p['sha256'], (p['name'],h.hexdigest(),p['sha256'])
        with zipfile.ZipFile(f) as z:
            names=[x for x in z.namelist() if x.startswith('info-') and x.endswith('.tar.zst')]; assert len(names)==1
            with z.open(names[0]) as src,zstandard.ZstdDecompressor().stream_reader(src) as s,tarfile.open(fileobj=s,mode='r|') as tar:
                files={}
                for m in tar:
                    if m.isfile() and (m.name.startswith('info/licenses/') or m.name in ('info/index.json','info/about.json','info/recipe/meta.yaml','info/recipe/meta.yaml.template')):
                        assert m.size<15_000_000
                        files[m.name]=tar.extractfile(m).read()
        index=json.loads(files['info/index.json']);about=json.loads(files['info/about.json'])
        assert index['name']==p['name'] and index['version']==p['version'] and index['build']==p['build']
        recipe=files.get('info/recipe/meta.yaml',b'').decode()
        rendered=yaml.safe_load(recipe) if recipe else {}
        extras=rendered.get('extra',{}) or {}
        out.append({'name':p['name'],'build':p['build'],'sha256':p['sha256'],'license':index.get('license'),'about_license':about.get('license'),'source':rendered.get('source'),'recipe_sha256':hashlib.sha256(recipe.encode()).hexdigest(),'feedstock_commit':extras.get('recipe-maintainers') and extras.get('feedstock-name'), 'extra':extras,'notice_sha256':{k:hashlib.sha256(v).hexdigest() for k,v in files.items() if k.startswith('info/licenses/')}})
        print('inspected',p['name'],flush=True)
Path('/tmp/openvino-records.json').write_text(json.dumps(out))
