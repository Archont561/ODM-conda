import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
from inventory_conda_environment import inventory

root = Path(os.environ['RUNNER_TEMP'])/'renderdem-output'
dirs = list((root/'bld').glob('rattler-build_renderdem_*'))
assert len(dirs) == 1
build = dirs[0]/'build_env'
host = list(dirs[0].glob('host_env_*'))
assert len(host) == 1
packages = list((root/'linux-64').glob('renderdem-1.0-*.conda'))
assert len(packages) == 1
raw = json.dumps({'candidate': packages[0].name, 'candidate_sha256': hashlib.sha256(packages[0].read_bytes()).hexdigest(), 'build': inventory(build), 'host': inventory(host[0]), 'scope': 'Research build on temporary workflow commit; not final release build. Binary package URLs and metadata do not establish source or rights.'}, indent=2, sort_keys=True).encode()
encoded = base64.b64encode(gzip.compress(raw, mtime=0)).decode()
chunks = [encoded[i:i+2700] for i in range(0, len(encoded), 2700)]
assert len(chunks) <= 40
print(f'::notice::BUILD-INFO chunks={len(chunks)} sha256={hashlib.sha256(raw).hexdigest()}', flush=True)
for i, chunk in enumerate(chunks): print(f'::notice::BUILD-CHUNK-{i:02d} {chunk}', flush=True)
