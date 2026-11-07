import ctypes as c
import json
import os
import subprocess
import sys
from pathlib import Path

prefix = Path(sys.prefix)
family = os.environ['FAMILY']

def read_archive():
    lib = c.CDLL(str(prefix/'lib/libarchive.so'))
    lib.archive_read_new.restype = c.c_void_p
    for name in ('archive_read_support_filter_all', 'archive_read_support_format_all', 'archive_read_free'):
        getattr(lib, name).argtypes = [c.c_void_p]
    lib.archive_read_open_filename.argtypes = [c.c_void_p, c.c_char_p, c.c_size_t]
    lib.archive_read_next_header.argtypes = [c.c_void_p, c.POINTER(c.c_void_p)]
    lib.archive_read_data.argtypes = [c.c_void_p, c.c_void_p, c.c_size_t]
    lib.archive_read_data.restype = c.c_ssize_t
    lib.archive_error_string.argtypes = [c.c_void_p]
    lib.archive_error_string.restype = c.c_char_p
    a = lib.archive_read_new()
    lib.archive_read_support_filter_all(a)
    lib.archive_read_support_format_all(a)
    rc = lib.archive_read_open_filename(a, os.fsencode(os.environ['FIXTURE']), 10240)
    entry = c.c_void_p()
    if rc == 0:
        rc = lib.archive_read_next_header(a, c.byref(entry))
    value = None
    if rc == 0:
        buffer = c.create_string_buffer(256)
        length = lib.archive_read_data(a, buffer, len(buffer))
        value = buffer.raw[:length].decode() if length >= 0 else None
        if length < 0: rc = length
    error = lib.archive_error_string(a)
    result = {'rc': rc, 'value': value, 'error': error.decode() if error else None}
    lib.archive_read_free(a)
    print(json.dumps(result))

if len(sys.argv) > 1:
    read_archive()
    sys.exit(0)

records = {}
for path in (prefix/'conda-meta').glob('*.json'):
    rec = json.loads(path.read_text())
    if rec['name'] in ('libspatialite', 'libarchive', 'lzo', 'librttopo'):
        records[rec['name']] = {k: rec.get(k) for k in ('version', 'build', 'sha256')}
assert ('lzo' in records) == (family == 'full')
assert ('librttopo' in records) == (family == 'full')
sp = c.CDLL(str(prefix/'lib/libspatialite.so'))
sql = c.CDLL(str(prefix/'lib/libsqlite3.so'))
sql.sqlite3_open.argtypes = [c.c_char_p, c.POINTER(c.c_void_p)]
sql.sqlite3_exec.argtypes = [c.c_void_p, c.c_char_p, c.c_void_p, c.c_void_p, c.POINTER(c.c_char_p)]
sql.sqlite3_free.argtypes = [c.c_void_p]
sql.sqlite3_close.argtypes = [c.c_void_p]
sp.spatialite_alloc_connection.restype = c.c_void_p
sp.spatialite_init_ex.argtypes = [c.c_void_p, c.c_void_p, c.c_int]
sp.spatialite_cleanup_ex.argtypes = [c.c_void_p]
db = c.c_void_p()
assert sql.sqlite3_open(b':memory:', c.byref(db)) == 0
cache = sp.spatialite_alloc_connection()
sp.spatialite_init_ex(db, cache, 0)
rows = []
cbtype = c.CFUNCTYPE(c.c_int, c.c_void_p, c.c_int, c.POINTER(c.c_char_p), c.POINTER(c.c_char_p))
def callback(_, count, values, names):
    rows.append([values[i].decode() if values[i] else None for i in range(count)])
    return 0
cb = cbtype(callback)
def execute(statement):
    rows.clear()
    error = c.c_char_p()
    rc = sql.sqlite3_exec(db, statement.encode(), cb, None, c.byref(error))
    message = error.value.decode() if error.value else None
    if error.value: sql.sqlite3_free(error)
    return {'rc': rc, 'rows': list(rows), 'error': message}
assert execute('SELECT InitSpatialMetaData(1)')['rows'] == [['1']]
topology = execute("SELECT CreateTopology('probe', 4326, 0, 0)")
node = None
if family == 'full':
    assert topology['rc'] == 0 and topology['rows'] == [['1']], topology
    node = execute("SELECT ST_AddIsoNode('probe', NULL, MakePoint(1, 2, 4326))")
    assert node['rc'] == 0 and node['rows'] == [['1']], node
    assert execute('SELECT count(*) FROM probe_node')['rows'] == [['1']]
else:
    assert topology['rc'] != 0 and 'no such function' in (topology['error'] or ''), topology
sql.sqlite3_close(db)
sp.spatialite_cleanup_ex(cache)
control = {'api_available': hasattr(sp, 'gaiaCreateControlPoints')}
if family == 'full':
    assert control['api_available']
    sp.gaiaCreateControlPoints.argtypes = [c.c_int, c.c_int, c.c_int, c.c_int]
    sp.gaiaCreateControlPoints.restype = c.c_void_p
    sp.gaiaAddControlPoint2D.argtypes = [c.c_void_p, c.c_double, c.c_double, c.c_double, c.c_double]
    sp.gaiaFreeControlPoints.argtypes = [c.c_void_p]
    handle = sp.gaiaCreateControlPoints(8, 0, 1, 0)
    assert handle
    control['added'] = [sp.gaiaAddControlPoint2D(handle, *point) for point in [(0., 0., 10., 20.), (1., 0., 11., 20.), (0., 1., 10., 21.)]]
    assert all(control['added']), control
    sp.gaiaFreeControlPoints(handle)
else:
    assert not control['api_available']

def run_read(path):
    env = os.environ.copy(); env['PATH'] = path
    result = subprocess.check_output([sys.executable, __file__, 'read'], env=env, text=True)
    return json.loads(result.strip().splitlines()[-1])
without = run_read(os.environ['EMPTY_PATH'])
with_helper = run_read('/usr/bin:/bin')
expected = 'ODM variant archive fixture\n'
assert with_helper['rc'] == 0 and with_helper['value'] == expected, with_helper
if family == 'full':
    assert without['rc'] == 0 and without['value'] == expected, without
else:
    assert without['rc'] != 0, without
print('::notice::OPERATION-TEST '+json.dumps({'family':family,'records':records,'topology':topology,'node':node,'control_points':control,'lzop_without_helper':without,'lzop_with_helper':with_helper},separators=(',',':'),sort_keys=True),flush=True)
