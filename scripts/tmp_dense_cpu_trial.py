import json, os, subprocess, sys, tempfile, urllib.request, tarfile, shutil
from pathlib import Path
from common import ROOT, run, sha256
from package_archive import read_package
from private_odm_bundle import build_recipe, loopback, verify, inventory_identities
from inventory_conda_environment import inventory
from private_conda_channel import create
from openmvs_pointcloud_fixture import DATASET_FILES, verify_dataset
from openmvs_dense_dataset_fixture import test_dense

with tempfile.TemporaryDirectory(prefix='dense-trial-') as tmp:
    root=Path(tmp)
    package=build_recipe(ROOT/'research/recipes/openmvs-dense-research/recipe.yaml','openmvs-dense-research',root)
    run([sys.executable,str(ROOT/'scripts/audit_openmvs_dense_research.py'),str(package)])
    info,_=read_package(package);idx=json.loads(info['info/index.json'])
    archive=root/'old-openmvs.tar.gz'
    urllib.request.urlretrieve('https://codeload.github.com/OpenDroneMap/openMVS/tar.gz/8e4c5f31a16e0e329132c8f26e20a8c5d7b47f53',archive)
    if sha256(archive)!='949d420d4506ccd0189574252c8214acce666de837e400e44682e8ddc13e666b':raise ValueError('dataset source archive mismatch')
    dataset=root/'dataset';dataset.mkdir()
    with tarfile.open(archive,'r:gz') as tar:
        prefix='openMVS-8e4c5f31a16e0e329132c8f26e20a8c5d7b47f53/apps/Tests/data/'
        for name in DATASET_FILES:
            item=tar.getmember(prefix+name)
            if not item.isfile() or item.size>10*1024*1024:raise ValueError('invalid dataset entry')
            target=dataset/name;target.parent.mkdir(parents=True,exist_ok=True)
            with tar.extractfile(item) as stream, target.open('wb') as out:shutil.copyfileobj(stream,out)
    verify_dataset(dataset)
    channel=root/'channel';create([package],channel)
    project=root/'pixi-project'
    with loopback(channel,48179) as url:
        run(['pixi','init','--format','pixi','--scm','github','--channel',url,'--channel','conda-forge','--platform','linux-64',str(project)])
        run(['pixi','add','--manifest-path',str(project/'pixi.toml'),'openmvs-dense-research'])
    scene=root/'scene';scene.mkdir()
    count=test_dense(project/'.pixi/envs/default/bin/DensifyPointCloud',dataset,scene)
    print('::notice::STANDALONE_CPU_PASS '+str(count),flush=True)
    bundle=Path('/tmp/odm-research-bundle')
    anchor='81da120940a5236657854b51b9713aae0e40dbd11199a51859197837e21c3c7b'
    port=verify(bundle,expected_manifest_sha=anchor)
    full=root/'full-project';full.mkdir()
    for name in ('pixi.toml','pixi.lock'):shutil.copy2(bundle/name,full/name)
    env=os.environ.copy();env['HOME']=str(root/'home');env['XDG_CACHE_HOME']=str(root/'cache');env['RATTLER_CACHE_DIR']=str(root/'cache/rattler');Path(env['HOME']).mkdir()
    with loopback(bundle/'channel',port):run(['pixi','install','--manifest-path',str(full/'pixi.toml'),'--locked'],env=env)
    prefix=full/'.pixi/envs/default'
    if inventory_identities(inventory(prefix))!=inventory_identities(json.loads((bundle/'conda-inventory.json').read_text())):raise ValueError('baseline inventory mismatch')
    # Research-only explicit overlay: the baseline package has no dense binary.
    # Do not claim a solved production package or changed baseline lock.
    dense=prefix/'bin/DensifyPointCloud'
    if dense.exists() or dense.is_symlink():raise ValueError('unexpected preexisting dense executable')
    _,payload=read_package(package);dense.write_bytes(payload['bin/DensifyPointCloud']);dense.chmod(0o755)
    linkage=subprocess.run(['ldd',str(dense)],capture_output=True,text=True,check=True)
    if 'not found' in linkage.stdout+linkage.stderr:raise ValueError('missing dense native dependency')
    seneca=root/'seneca';run(['git','init',str(seneca)]);run(['git','-C',str(seneca),'fetch','--depth=1','https://github.com/OpenDroneMap/odm_data_seneca.git','9220acfdca75cc5e2dd6d27fe48550c5ae0877f2']);run(['git','-C',str(seneca),'checkout','--detach','FETCH_HEAD'])
    if subprocess.check_output(['git','-C',str(seneca),'rev-parse','HEAD'],text=True).strip()!='9220acfdca75cc5e2dd6d27fe48550c5ae0877f2':raise ValueError('dataset commit mismatch')
    images=sorted((seneca/'images').glob('*.jpg'))[:35]
    if len(images)!=35:raise ValueError('insufficient Seneca images')
    projects=root/'projects';dest=projects/'dataset/images';dest.mkdir(parents=True)
    for img in images:shutil.copy2(img,dest/img.name)
    env.pop('PYTHONPATH',None);env.pop('PYTHONHOME',None);env.pop('LD_LIBRARY_PATH',None)
    env['PYTHONNOUSERSITE']='1';env['ODM_NO_GPU']='1';env['ODM_CONDA_LOCAL_PREFIX']=str(prefix);env['PROJ_DATA']=env['PROJ_LIB']=str(prefix/'share/proj');env['PATH']=str(prefix/'bin')+os.pathsep+os.defpath
    app=prefix/'share/odm-conda/odm-fast-research/app/run.py'
    command=[str(prefix/'bin/python'),'-s','-E',str(app),'--end-with','openmvs','--no-gpu','--pc-quality','lowest','--feature-quality','low','--max-concurrency','2','--project-path',str(projects),'dataset']
    run(command,env=env)
    outputs=list((projects/'dataset/openmvs').glob('*.ply'))
    if not outputs or not any(p.stat().st_size>1000 for p in outputs):raise ValueError('ODM produced no dense PLY')
    print('::notice::ODM_DENSE_STAGE_PASS '+json.dumps({'images':len(images),'outputs':[p.name for p in outputs],'overlay':True}),flush=True)
    report={'dense_point_count':count,'filename':package.name,'sha256':sha256(package),'depends':idx['depends'],'scope':'research-only, CPU scene and ODM dense stage with explicit binary overlay, not full ODM, accuracy, rights or release approval'}
    print('::notice::DENSE_REPORT '+json.dumps(report,sort_keys=True),flush=True)
