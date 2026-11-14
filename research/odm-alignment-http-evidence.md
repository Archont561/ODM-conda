# DEM alignment and PyODM loopback probes

These local research diagnostics do **not** validate an installed ODM package,
a real NodeODM/ClusterODM server, or a production distributed deployment. They
were performed separately from PR #113's packaged hosted tests.

## Synthetic DEM alignment and nodata

The probe ran upstream ODM 3.6.2 source commit
`47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45` from a codeload archive verified
against SHA-256 `5bdf8fe81b9ca47714e8a474139fd206b8090ac4315c2f530a58fcaef29cde5e`.
It loads `opendm/dem/merge.py` directly and stubs command/system/log/io
infrastructure, providing synthetic precomputed SciPy distance maps. Python
3.11, NumPy 2.4.6, SciPy 1.17.1 and Rasterio 1.4.4 were used. This did not
exercise ODM's map generation, its installed package, or GDAL proximity.

Two 24×24 aligned-pixel-resolution DEMs, one shifted horizontally, had one-pixel
nodata borders and constant valid heights. The independent reference resampled
both arrays and weights using Rasterio nearest-neighbor to the output grid and
computed their weighted average.

| Offset in pixels | nodata | valid values | valid expected / output | pixels differing |
|---|---:|---|---:|---:|
| 8.0 | -9999 | 100, 200 | 660 / 660 | 0 |
| 8.25 | -9999 | 100, 200 | 660 / 660 | 0 |
| 8.75 | -9999 | 100, 200 | 682 / 682 | 0 |
| 8.0 | -9999 | **0**, 200 | 660 / **484** | **176** |
| 8.0 | 0 | 100, 200 | 660 / 660 | 0 |
| 8.0 | -9999 | 100, entirely nodata | 484 / 484 | 0 |

**Observed defect:** in this source version, `dstarr[dstarr == 0.0] = src_nodata`
converts legitimate zero-height results to nodata, including the 176 pixels
exclusive to the zero-valued raster. This diagnostic did not patch or fix ODM.
The offset cases are not general proof of correct alignment: they use constant
values, common resolution/CRS, only horizontal offsets, simple bordered shapes,
and one output block. Other nodata conventions, tiling, varied surfaces and
geometries remain untested. Use caution with zero elevations; do not claim
production-ready DEM merging from these results.

Reproduce after obtaining and hash-verifying the upstream archive:
`ODM_TEST_SOURCE=/path/to/extracted/ODM PYTHONPATH=/path/to/deps python -m pytest -q tests/test_odm_dem_alignment_probe.py`.
This optional regression captures current behavior including the defect, not a
correctness endorsement. A future fix should change its expected zero-height
case and verify installed package behavior.

## PyODM loopback HTTP mock

`tests/test_pyodm_http_mock.py` passed using the exact PyODM 1.5.12 sdist
verified SHA-256 `d0433182ac6d5587786391c91d0eeafe0d78c71d618336af78964620dafe87c4`.
A disposable `127.0.0.1` HTTP server simulated selected API responses. The
actual PyODM client sent init, two multipart uploads, commit, status, download,
and removal requests; the test checked uploaded bytes, requested outputs,
completion/download/extraction of a generated zip, failed status handling and
removal. It did not run ODM, NodeODM or ClusterODM, use a packaged PyODM,
exercise scheduler/fallback/retries/disconnections/authentication/hostile
archives, or establish compatibility/security. The server is a test fake, not a
service implementation. The normal locked repository environment lacks PyODM,
so this optional test is skipped there; it ran separately with local dependencies.
