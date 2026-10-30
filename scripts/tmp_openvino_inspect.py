import hashlib, json, os, subprocess, tempfile, io, tarfile, zipfile, urllib.request, zlib, base64
from pathlib import Path
import zstandard

names=['libopenvino','libopenvino-auto-batch-plugin','libopenvino-auto-plugin','libopenvino-hetero-plugin','libopenvino-intel-cpu-plugin','libopenvino-intel-gpu-plugin','libopenvino-intel-npu-plugin','libopenvino-ir-frontend','libopenvino-onnx-frontend','libopenvino-paddle-frontend','libopenvino-pytorch-frontend','libopenvino-tensorflow-frontend','libopenvino-tensorflow-lite-frontend']
with tempfile.TemporaryDirectory(dir=os.environ['RUNNER_TEMP']) as d:
    root=Path(d)
    subprocess.run(['pixi','init','--format','pixi','--scm','github','--channel','conda-forge','--platform','linux-64',str(root)],check=True)
    subprocess.run(['pixi','add','--manifest-path',str(root/'pixi.toml'),'python >=3.12,<3.13','libopencv >=4.13,<5','py-opencv >=4.13,<5','libopenvino >=2026.0'],check=True)
    out=[]
    for filename in sorted((root/'.pixi/envs/default/conda-meta').glob('libopenvino*.json')):
        item=json.loads(filename.read_text());url=item['url']; digest=item['sha256']
        assert url.startswith('https://conda.anaconda.org/conda-forge/')
        with urllib.request.urlopen(url) as response: raw=response.read()
        assert hashlib.sha256(raw).hexdigest()==digest
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            info=next(n for n in z.namelist() if n.startswith('info-') and n.endswith('.tar.zst'))
            with tarfile.open(fileobj=zstandard.ZstdDecompressor().stream_reader(io.BytesIO(z.read(info))),mode='r|') as t:
                files={}; fields={}
                for entry in t:
                    if entry.isfile() and (entry.name.startswith('info/licenses/') or entry.name in ('info/index.json','info/about.json','info/recipe/meta.yaml')):
                        b=t.extractfile(entry).read()
                        if entry.name.startswith('info/licenses/'): files[entry.name]=hashlib.sha256(b).hexdigest()
                        elif entry.name.endswith('.json'): fields[entry.name]=json.loads(b)
                        else: fields['recipe_sha256']=hashlib.sha256(b).hexdigest()
        index=fields['info/index.json']; about=fields['info/about.json']
        out.append({'name':item['name'],'version':item['version'],'build':item['build'],'sha256':digest,'url':url,'index_license':index.get('license'),'about_license':about.get('license'),'feedstock_sha':about.get('extra',{}).get('sha'),'declared_license_files':about.get('license_file'),'info_licenses':files,'rendered_recipe_sha256':fields.get('recipe_sha256')})
    assert len(out)==13
    encoded=base64.b64encode(zlib.compress(json.dumps(out,sort_keys=True,separators=(',',':')).encode(),9)).decode()
    print(f'RESULT_COUNT {len(out)} CHUNKS {(len(encoded)+2999)//3000}',flush=True)
    for i in range(0,len(encoded),3000): print(f'OPENVINO_CHUNK_{i//3000:02d} {encoded[i:i+3000]}',flush=True)
    print('::notice::INSPECTED '+str(len(out))+' solver-selected OpenVINO packages; metadata licenses '+str(sum(bool(x['index_license']) for x in out))+'; info/licenses present '+str(sum(bool(x['info_licenses']) for x in out)),flush=True)
