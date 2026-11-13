from pathlib import Path
p=Path('research/recipes/python-source-research/codem.yaml')
s=p.read_text();anchor='''    requirements:
      run:
        - python >=3.12,<3.13
about:'''
assert s.count(anchor)==1
code='''        import json
        import re
        for file in sorted((Path(sys.prefix) / 'conda-meta').glob('*.json')):
            obj = json.loads(file.read_text())
            if obj.get('name') in ('hdf5', 'libpdal-core', 'libpdal-hdf', 'libpdal-icebridge'):
                print('::notice::DEPENDENCY ' + ' '.join(str(obj.get(k, '')) for k in ('name', 'version', 'build')))
        for lib in sorted((Path(sys.prefix) / 'lib').glob('libpdal_plugin_reader_*.so')):
            if lib.name not in ('libpdal_plugin_reader_hdf.so', 'libpdal_plugin_reader_icebridge.so'):
                continue
            result = subprocess.run(['ldd', str(lib)], capture_output=True, text=True, check=True)
            missing = [line.strip() for line in result.stdout.splitlines() if 'not found' in line]
            print('::notice::PLUGIN ' + lib.name + ' ' + '; '.join(missing))
'''
p.write_text(s.replace(anchor,code+anchor))
