import json, subprocess, sys, tempfile, urllib.request, tarfile, shutil
from pathlib import Path
from common import ROOT, run, sha256
from package_archive import read_package
from private_odm_bundle import build_recipe, loopback
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
    report={'dense_point_count':count,'filename':package.name,'sha256':sha256(package),'depends':idx['depends'],'scope':'research-only, CPU upstream test scene, not full ODM, accuracy, rights or release approval'}
    print('::notice::DENSE_REPORT '+json.dumps(report,sort_keys=True),flush=True)
