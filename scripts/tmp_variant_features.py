import ctypes as c
import glob
import json
import os
import subprocess
import sys
from pathlib import Path

prefix = Path(sys.prefix)
records = {}
for path in (prefix / 'conda-meta').glob('*.json'):
    record = json.loads(path.read_text())
    if record['name'] in ('libspatialite', 'libarchive', 'lzo', 'librttopo'):
        records[record['name']] = {k: record.get(k) for k in ('version', 'build', 'sha256')}
sp = c.CDLL(str(prefix / 'lib/libspatialite.so'))
sql = c.CDLL(str(prefix / 'lib/libsqlite3.so'))
sql.sqlite3_open.argtypes = [c.c_char_p, c.POINTER(c.c_void_p)]
sql.sqlite3_exec.argtypes = [c.c_void_p, c.c_char_p, c.c_void_p, c.c_void_p, c.POINTER(c.c_char_p)]
sql.sqlite3_close.argtypes = [c.c_void_p]
sp.spatialite_alloc_connection.restype = c.c_void_p
sp.spatialite_init_ex.argtypes = [c.c_void_p, c.c_void_p, c.c_int]
sp.spatialite_cleanup_ex.argtypes = [c.c_void_p]
db = c.c_void_p()
assert sql.sqlite3_open(b':memory:', c.byref(db)) == 0
cache = sp.spatialite_alloc_connection()
sp.spatialite_init_ex(db, cache, 0)
callback_type = c.CFUNCTYPE(c.c_int, c.c_void_p, c.c_int, c.POINTER(c.c_char_p), c.POINTER(c.c_char_p))
results = {}
def callback(_, count, values, names):
    results.update({names[i].decode(): values[i].decode() if values[i] else None for i in range(count)})
    return 0
cb = callback_type(callback)
error = c.c_char_p()
rc = sql.sqlite3_exec(db, b'SELECT spatialite_version() AS version, HasRtTopo() AS rttopo', cb, None, c.byref(error))
assert rc == 0, error.value
sql.sqlite3_close(db)
sp.spatialite_cleanup_ex(cache)
symbols = subprocess.check_output(['nm', '-D', '--defined-only', str(prefix/'lib/libspatialite.so')], text=True)
results['control_point_symbols'] = sorted(line.split()[-1] for line in symbols.splitlines() if 'ControlPoint' in line)
archive = c.CDLL(str(prefix/'lib/libarchive.so'))
archive.archive_read_new.restype = c.c_void_p
archive.archive_read_support_filter_lzop.argtypes = [c.c_void_p]
archive.archive_error_string.argtypes = [c.c_void_p]
archive.archive_error_string.restype = c.c_char_p
archive.archive_read_free.argtypes = [c.c_void_p]
a = archive.archive_read_new()
results['lzop_support_rc'] = archive.archive_read_support_filter_lzop(a)
err = archive.archive_error_string(a)
results['lzop_support_message'] = err.decode() if err else None
archive.archive_read_free(a)
print('::notice::FEATURE-PROBE '+json.dumps({'family': os.environ['FAMILY'], 'records': records, 'results': results}, sort_keys=True, separators=(',', ':')), flush=True)
