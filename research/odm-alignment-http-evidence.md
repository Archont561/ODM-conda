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
exclusive to the zero-valued raster. The initial diagnostic did not patch ODM;
the private research recipe fix and its limited verification are described below.
The offset cases are not general proof of correct alignment: they use constant
values, common resolution/CRS, only horizontal offsets, simple bordered shapes,
and one output block. Other nodata conventions, tiling, varied surfaces and
geometries remain untested. Use caution with zero elevations; do not claim
production-ready DEM merging from these results.

Reproduce after obtaining and hash-verifying the upstream archive:
`ODM_TEST_SOURCE=/path/to/extracted/ODM PYTHONPATH=/path/to/deps python -m pytest -q tests/test_odm_dem_alignment_probe.py`.
The regression first confirms the defect in pristine upstream source, then
applies all five research recipe patches, runs the repository's installer into a
temporary prefix, and probes the copied application. The installer copy is not
a built or solved Conda package.

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

## Private research fix and local verification

Research recipe build 6 applies `0005-dem-zero-elevation.patch`: it marks nodata
from zero accumulated contribution weight, rather than testing the elevation
value. The coverage mask follows the same nearest-neighbor indices as the output
for the merger's low-distance interpolation path. The restricted launcher and
release gates are unchanged; upstream ODM and other recipes are not modified.

Against the verified upstream archive, the optional regression applied all five
patches and copied the patched application using `build_odm_dense_research.install`.
The same probe was then run against the copied app, with synthetic precomputed
maps and stubbed ODM command/system/io/log imports. The zero-valued-source case
preserved all 660 expected valid pixels (baseline 484); an equal-weight -100/100
case preserved 660 (baseline 548). All seven reference cases matched. A separate
artificial low-distance interpolation case preserved all 484 valid zeros including
the interpolated center, while retaining nodata borders (baseline lost all 484).
That first regression was source/installer-copy verification, not a Conda
package test. Subsequent packaged verification is documented below. No result
establishes general merge quality or release readiness.

### Build 6 packaged replay

[Hosted run 43657926454](https://github.com/Archont561/ODM-conda/actions/runs/43657926454)
rebuilt the private dependencies and `odm-dense-research` build 6, retested the
package, solved a fresh environment and replayed its identical lock and all 436
package identities in a second relocated prefix. Tests called the installed ODM
modules with no source or binary overlay. Each of three synthetic 8×8 cases
(zero-valued sources, -100/100 cancellation, and artificially low-distance
interpolation) preserved all 36 valid zero pixels and 28 nodata border pixels.
A separate installed generated-distance test matched independently calculated
weights over 660 valid pixels. See `odm-zero-elevation-package-evidence.json`.

This is not an end-to-end dataset run, real seam or accuracy validation, generic
nodata proof, source-rights clearance or release approval. The private packages,
lock and inputs were discarded; their recorded hashes alone cannot reproduce the
solve. The first rebuild attempt [43656702342](https://github.com/Archont561/ODM-conda/actions/runs/43656702342)
failed before ODM build because the temporary build path caused pip to emit a
CODEM shell shebang rejected by its recipe; the successful run used a shorter path.

### Real imagery, controlled zero intervention

[Hosted run 43712848391](https://github.com/Archont561/ODM-conda/actions/runs/43712848391)
rebuilt build 6 and replayed 436 package identities in a fresh prefix without
source or binary overlays. Invoking the installed app directly (deliberately
bypassing the launcher's split restriction), it processed 35 Seneca images in
two overlapping groups without classification, producing two point clouds,
84,987 merged points, two DSM inputs and a merged 2865×2153 DSM and orthophoto.
The unmodified merged DSM range was 213.636–234.926, so this is **not a natural
zero-elevation site**.

For a controlled counterfactual, copies of the two real-derived DSMs were
merged using fresh generated proximity maps. One 8×8 patch in a safely exclusive
valid region was changed from approximately 217.512–217.523 to zero; all 64
mapped output pixels remained valid zeros. The comparison merge of unmodified
copies remained nonzero. This exercises a real-derived geometry and surrounding
values with an artificial intervention, not real zero terrain, overlap-zero
behavior, accuracy, general seam quality, distributed processing or a 3D merge.
The fixture is `scripts/odm_real_dem_zero_fixture.py`; run identity, scope and
rights caveats are recorded in `odm-real-data-zero-evidence.json`. The imagery,
rasters, packages and lock were discarded, not uploaded. Dataset rights remain
unverified and the restricted launcher is unchanged.

### SRTM-format zero values in overlap

[Hosted run 43718084794](https://github.com/Archont561/ODM-conda/actions/runs/43718084794)
rebuilt and retested the private ODM research package, then replayed 436 matching
package identities in a relocated prefix without overlays. The installed DEM
merger generated distance maps and merged two overlapping, aligned crops of the
same unmodified `N10W110.hgt` raster sample. Except for adding nodata borders,
the samples were not altered. All 64,516 valid output pixels matched the
original crop, including 64,042 zeros (31,530 in overlap) and 474 positive
pixels. This is an SRTM-format raster, **not** a drone-image reconstruction.
Both crops come from the same raster, so this does not validate two independent
submodels or conflicting source values. The grid is geographic EPSG:4326.

The raster was retrieved from Rasterio commit
[`124e23f4060678460f39a0d838ac8c83b6fe2fe7`](https://github.com/rasterio/rasterio/tree/124e23f4060678460f39a0d838ac8c83b6fe2fe7/tests/data),
archive SHA-256 `7c668fd7868fbf8addcad0b1f993259d3d4f65f9f8990099e67e31fb1f595362`.
Its test-data README asserts CC0 1.0 for test images, and its introducing commit
calls it a small SRTM 3 file. Neither attribution authority, original provenance
nor rights were independently cleared or owner-approved. Zero-valued ocean or
background cells are not proof of measured natural zero-elevation land. The
fixture does not establish geometric accuracy, real seam quality, general DEM
handling or release readiness. The inputs, packages and lock were discarded;
`odm-srtm-zero-overlap-evidence.json` retains metrics and limitations, not data.
The earlier attempt [43716283877](https://github.com/Archont561/ODM-conda/actions/runs/43716283877)
passed build/replay but failed before the SRTM test because a GitHub CLI binary
response was rejected as invalid UTF-8; the successful retry decoded API base64.
