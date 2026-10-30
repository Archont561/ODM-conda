# ODM fast-orthophoto: local integration experiment

**Research only; not an ODM package or a release, license approval, or successful integration test.** TASK-13 and its production/legal dependencies remain open. Do not distribute the assembled research OpenSfM/OpenMVS packages or use this as a production launcher. The OpenSfM, OpenMVS, mvs-texturing, application source and other dependency rights and notices require review. Never publish any package from this experiment without the separate owner gates.

## What was inspected

ODM 3.6.2 commit `47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45`: the [source archive](https://codeload.github.com/OpenDroneMap/ODM/tar.gz/47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45) has SHA256 `5bdf8fe81b9ca47714e8a474139fd206b8090ac4315c2f530a58fcaef29cde5e`. `opendm/context.py` derives SuperBuild and app-root paths; `opendm/osfm.py` expects `SuperBuild/install/bin/opensfm/bin/opensfm`, whereas the research package installs `bin/opensfm` and Python modules in site-packages. `opendm/system.py` appends the SuperBuild binary directory to subprocess PATH. `run.py` reads VERSION relative to the working directory, while config, settings, report and other app resources are rooted in the source tree. Python stages are imported even for stages skipped at runtime. The entire pinned app source tree, including resources, is retained in the local staging directory, not just the entry point.

The experimental patch redirects context binary paths to an explicit prefix, stops appending SuperBuild Python paths, points OpenSfM at the packaged executable, and resolves VERSION relative to the application. `--fast-orthophoto` skips dense OpenMVS, but still requires `ReconstructMesh`, Poisson, texrecon, DEM tools and the other components in doc-11. The wrapper rejects point classification and split/merge. Additional flags and implicit paths are **not** exhaustively constrained or tested; this is not a security boundary. Some optional modes may still need unlisted dependencies or access the network. Subprocess PATH falls back to `/usr/bin:/bin`; the prefix checks cannot establish that every subprocess comes from the prefix.

## Local use

On a machine with the pinned archive and a separately assembled local prefix containing the approved-for-local-use research and production component builds **and** ODM's Python/runtime dependencies:

```sh
pixi run python scripts/odm_local_prototype.py prepare --archive /path/to/odm.tar.gz --output /path/to/odm-app
pixi run python scripts/odm_local_prototype.py check --prefix /path/to/conda-prefix --imports
pixi run python scripts/odm_local_prototype.py run --app /path/to/odm-app --prefix /path/to/conda-prefix -- --fast-orthophoto --skip-3dmodel --project-path /path/to/projects DATASET_NAME
```

The first step verifies the pinned archive and patch, extracts using the repository's guarded archive extraction, and refuses an existing destination. It never builds SuperBuild. The prefix must be supplied separately; **this repository does not yet provide a solved, complete prefix or an ODM recipe**. The check requires the MVP executables and some GDAL/PDAL tools to resolve inside that prefix. `--imports` executes a selected Python import probe with the prefix interpreter. Launch repeats both checks, prevents ambient Python paths and executes the upstream entry point using that interpreter. Checks do not validate versions, solve consistency, native dependency closure, every import, resource completeness, external subprocesses or ABI compatibility. Do not run this against untrusted input or with paths or flags that expose shell-injection risk in upstream ODM.

## Evidence and remaining work

The actual pinned archive prepared successfully. After relocating the staged app to a path containing spaces, importing the patched context resolved the app root and ReconstructMesh to the new paths. This is a path mapping check, **not** a relocated binary/Conda prefix execution test. Unit tests use synthetic files and mocks only. The local `odm-dev` prefix fails the executable check: it lacks all nine ODM-specific tools, including OpenSfM and ReconstructMesh. The research CI builds were isolated and discarded; no combined install, genuine launcher run, native relocation audit, dataset run, or ABI validation has been performed.

Next: assemble the actual local-only packages and compatible Python dependencies together without publishing them; audit solved dependencies, imports, resources and ELF relocation in both original and moved prefixes; verify launcher/help and real component dispatch; then run the dataset. Failures should remain visible rather than falling back to SuperBuild. Resolve source rights, notices and owner-controlled gates before creating a production recipe or publishing anything.

## Dataset investigation

[Seneca Aerial Dataset](https://github.com/OpenDroneMap/odm_data_seneca/tree/9220acfdca75cc5e2dd6d27fe48550c5ae0877f2) is a candidate: its repository includes [CC0 1.0](https://github.com/OpenDroneMap/odm_data_seneca/blob/9220acfdca75cc5e2dd6d27fe48550c5ae0877f2/license.txt) and identifies Ohio Department of Transportation geotagged imagery. GitHub's API lists 167 JPEGs totaling 376,389,916 bytes, so it is **not yet a suitably small verified fixture**. A spatially coherent subset might be smaller but its overlap and ability to reconstruct are untested. Confirm provenance, image rights and suitability before use or redistribution; a repository-level license is not independent proof of the uploader's authority. [Garfield RGB](https://github.com/OpenDroneMap/odm_data_garfield_msp/tree/b526478fbd39adc1d0e14229db39b9b224c8cf68) is smaller (28 JPEGs, 59,342,300 bytes) and includes CC0, but its README expressly says it does not work in ODM due to matching; do not treat it as a validated end-to-end fixture. No data was downloaded or added to this repository.

### Local assembly feasibility follow-up (2026-10-29)

With the restored locked tool environments, the `odm-dev` prefix preflight still fails because nine component executables are absent: `opensfm`, `FPCFilter`, `PoissonRecon`, `ReconstructMesh`, `dem2points`, `renderdem`, `fastrasterfilter`, `texrecon`, and `odm_orthophoto`. The check stops before Python imports; no claim about imports is made. An attempt to build the OpenSfM research package locally first hit Python certificate verification. Retrying with the system CA bundle (`SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt`) verified the pinned source archives and applied the source patch, but rattler-build could not fetch conda-forge noarch repodata (unexpected EOF) and produced no package. The temporary research build directory was removed by the runner. The previous successful owner research CI discarded its outputs, so there is still no combined prefix to test. No dataset or launcher run was attempted and TASK-13 remains open; a runner with conda-forge access and a local-only coordinated build/solve is required before testing a candidate dataset.

### Disposable combined-prefix experiment (2026-10-29)

Temporary GitHub-hosted [run 40866808464](https://github.com/Archont561/ODM-conda/actions/runs/40866808464) SHA256-verified seven previously retained artifact ZIPs and selected one package each (fpcfilter, dem2points, odm-orthophoto, fastrasterfilter, renderdem, poissonrecon-odm and mvs-texturing-odm). It also built both local-only OpenSfM and reduced OpenMVS research packages, ran their packaged and fresh tests, and passed their limited research audits. It attempted a disposable Pixi environment containing all nine packages plus GDAL/PDAL tools and exiftool. The solve failed; nothing was uploaded. A [second run](https://github.com/Archont561/ODM-conda/actions/runs/40867845237) repeated the builds and produced GDAL/PDAL solver diagnostics.

A fresh [minimal reproduction](https://github.com/Archont561/ODM-conda/actions/runs/40868856018) using only the same verified `dem2points-0.0.0.dev20220721-h873e7db_0.conda` (SHA256 `73634decaba27cd3b7a6980a9156b656ca505f97a021b261c72a095ba064f9e8`) and `renderdem-1.0-h873e7db_0.conda` (SHA256 `dc33a1fb2de90eabc0ee241f573bd14f09d4d3481f0fb813bd90f792b4f8b895`) also failed. The solver reported dem2points needs `libgdal-core >=3.11.5,<3.12.0a0`, while renderdem needs `libpdal-core >=2.10,<2.11`; available PDAL candidates did not yield a compatible GDAL 3.11 solve at the time. This is a real packaging-integration blocker, not merely a missing tool or proof that no other future combination could exist. TASK-57 tracks a consistent, rebuilt ABI selection. Do not bypass metadata or weaken ABI checks.

No combined prefix was installed: imports, prototype launcher, relocation and the candidate Seneca dataset run were **not reached**. A combined solve may uncover further constraints even after the two-package conflict is addressed. The experiment uploaded no research sources, binaries or data; rights and all release gates remain unchanged.

### Candidate common GDAL/PDAL baseline (2026-10-29)

A temporary dependency-only Pixi solver experiment on GitHub Actions tested
Python 3.12, GDAL and Python bindings, PDAL and Python-PDAL, OpenCV 4.12,
Boost 1.90, TBB 2023.1, libpng, Ceres, rasterio and exiftool. GDAL 3.13
[did not solve](https://github.com/Archont561/ODM-conda/actions/runs/40904066709)
with the selected Python binding constraints. GDAL 3.12
[did solve](https://github.com/Archont561/ODM-conda/actions/runs/40904165751):
libgdal-core 3.12.2 `hc2c0581_0`, libpdal-core 2.10.0 `h9d23c72_0`,
libopencv 4.12.0 `qt6_py312h52d6ec5_612`, py-opencv 4.12.0
`qt6_py312h598be00_612`, python-pdal 3.5.3 `np2py312hadcd02a_4`, and
TBB 2023.1.0 `haa8c3ee_2`. It was a fresh dependency-only solve, not an
installation, an exact nine-package solve or an assurance that these particular
builds remain available or suffice for a complete ODM run.

The dem2points, fastrasterfilter and odm-orthophoto recipes now request
GDAL `>=3.12,<3.13` for both host and run, with new build number 1; all four
release checks were reset for each candidate. Existing published build 0
artifacts and their historical approvals are unchanged. Rebuilding is essential:
the old binaries and their GDAL 3.11 runtime requirements were not modified.
Local shared checks passed, but a native dem2points build stopped before
compilation because conda-forge noarch repodata returned EOF. Owner native
builds, installed tests, fresh retests, audits and source bundles are required
for all three candidates, followed by a real nine-component solve, relocation,
launcher and dataset tests. Other incompatibilities may emerge. TASK-57 remains
open and no publication is authorized.

### Native candidate artifact review and remaining ABI conflict (2026-10-29)

Owner [run 40906236704](https://github.com/Archont561/ODM-conda/actions/runs/40906236704)
built the three requested build-1 candidates. Independent temporary
[inspection 40907763520](https://github.com/Archont561/ODM-conda/actions/runs/40907763520)
verified artifact `12912041865` ZIP SHA256
`c217093dfc903c34b47e67620f012385f03ecbb777c82bbe990109eb5ac12623`,
exactly the three expected packages, their upstream source hashes, all 246
source-manifest hashes per bundle and exact declared upstream notice bytes in
payload and metadata. Each passed the current package audit and an independent
fresh retest. The three package SHA256 values were dem2points
`f7beed995be059343796b2d4727706a6fbf89a4bcd448a4a85ff0ca7c2c6da8d`,
fastrasterfilter `916027e4fcbd28da4cb39f164fa19b89b60714d43712866f023b0a7efed1e8af`,
and odm-orthophoto `1ef443343ce49b8890d1a1915b54cb4c09efb3b17ad7998d4f23d091078bcaf6`.
The corresponding source-bundle hashes were
`a12acaf203ad72110a10a40f41af7b398da9db4c364ef07cc8f40c9dcee8c43a`,
`8b491eeea4afdfa6a517c692718c1c58d5f6c9c115235e4045377f686183b121`, and
`3d4fe0dd6db8bb4dbbaf80e28a4323e3659de1e5a17c26b7c2b36b353960f1db`.

**The combined solve still failed**, even for only the actual dem2points
build 1 and historical RenderDEM build 0. Rattler's generated dependency from
the build-1 host solve requires `libgdal-core >=3.12.4,<3.13.0a0`; RenderDEM
build 0 requires `libpdal-core >=2.10.2,<2.11.0a0`. The successful earlier
*dependency-only* solve instead selected GDAL 3.12.2 and PDAL 2.10.0. The
three candidates have therefore been advanced to build 2 with GDAL
`>=3.12.2,<3.12.3`, and RenderDEM to build 1 with that GDAL range and PDAL
`>=2.10.0,<2.10.1` in host and run. This coordinates actual build inputs rather
than overriding generated ABI metadata. The four new candidates remain
unbuilt; availability, a shared binary solve, all nine components and actual
ODM execution remain unverified. Owner native builds and reinspection are
required; gates remain false.

### Coordinated artifact inspection (2026-10-29)

Owner [run 40908393516](https://github.com/Archont561/ODM-conda/actions/runs/40908393516)
passed but independent [inspection 40908795526](https://github.com/Archont561/ODM-conda/actions/runs/40908795526)
confirmed artifact `12910914634`, ZIP SHA256
`fff273a42ac145811f36447824fc86e03820d13b6a6efd2f04111992100970a2`,
contains only **fastrasterfilter build 2, odm-orthophoto build 2, and
renderdem build 1**. It does not contain dem2points.

[Follow-up inspection 40908908691](https://github.com/Archont561/ODM-conda/actions/runs/40908908691)
verified each source archive and all 246 manifest entries, exact declared
upstream notice bytes in payload and metadata, current audit and a fresh
retest. Package SHA256: fastrasterfilter
`52d42537b1ed1ba80a473e4540392d90f49f95e7e6dbb930445c9a3307f859dd`,
odm-orthophoto `093c55b75981239cb31dccaf66e44e9a4d2addcfe37e31950870451d2f0bb58f`,
renderdem `451a291036f9bf11c140464d088884ec8980051c5383a667b75d1be7637fea77`.
Corresponding source-bundle SHA256 respectively:
`90c3330cf2afeafd6b49cc46779cffaf6682e97918f747cbacd0c36094a95db2`,
`651ef9bee5651c94684e0f67fd89e1f29e326c0b06414ce021fbe8dbe206dc20`, and
`411bfab9e9c99af6848e365ed20afb889d1966115f17923c17fca06517b25dce`.
All three actual packages installed together with PDAL, Python-PDAL, GDAL and
exiftool; selected libgdal-core was 3.12.2 `hc2c0581_0`, libpdal-core 2.10.0
`h9d23c72_0`. Their executable files were present. This test used Python 3.13
OpenCV dependencies, not the ODM Python 3.12 research environment. It did not
include dem2points, the other five components, relocation, a launcher or
dataset run. The owner must dispatch the dem2points build-2 candidate separately;
all release gates remain closed.

### Four-package compatibility check (2026-10-29)

Owner [run 40909632056](https://github.com/Archont561/ODM-conda/actions/runs/40909632056)
passed on `d4e40293ff9627e21f806cf7f9a31226e969576d`. Independent
[inspection 40910163219](https://github.com/Archont561/ODM-conda/actions/runs/40910163219)
confirmed artifact `12911564893`, ZIP SHA256
`2e6af14e3eaffa0631c59e875fa114b95376f17a1c7c7de4815e9fc3e7eefb87`,
contains dem2points build 2, its audit report and source bundle only. Package
SHA256 `f7077c2eb01f380503d2aa5203e20d78e824a1c4adceaa486f4cbaf22bee8cb0`;
source bundle SHA256 `9029351b2cccf4eeca82c580f7fab8c68f0f05410cae36ca003380c9d16a8ce8`.
All 246 manifest entries, declared upstream notices in payload and metadata,
package audit and isolated fresh retest passed.

The same inspection verified the earlier three package hashes and installed
all four actual packages together with Python 3.12, py-opencv 4.12, PDAL,
Python-PDAL, GDAL and exiftool. It selected libgdal-core 3.12.2 `hc2c0581_0`,
libpdal-core 2.10.0 `h9d23c72_0`, libopencv 4.12.0
`qt6_py312h52d6ec5_612` and python-pdal 3.5.3 `np2py312hadcd02a_4`;
all four executable files were present. This resolves the observed **four-package
solver conflict for this fresh environment**, not full integration: fixtures
were retested individually, not in the combined prefix, and the nine-component
solve, relocation, ODM launcher and dataset have not been run. Legal and release
gates remain unchanged.

### Nine-package local-only trials (2026-10-29)

A dependency-only [matrix](https://github.com/Archont561/ODM-conda/actions/runs/40913563570)
identified PDAL 2.10.0's trajectory plugin requirement for gflags 2.2.x;
OpenSfM was genuinely rebuilt against that ABI rather than relabeled. A further
[solve](https://github.com/Archont561/ODM-conda/actions/runs/40915095265)
selected Eigen 3.4.0, gflags 2.2.2, GDAL 3.12.2 and PDAL 2.10.0.
The [actual nine-package trial](https://github.com/Archont561/ODM-conda/actions/runs/40915195339)
verified the seven retained package identities above, rebuilt and audited local
research OpenSfM build 3 and OpenMVS build 3, installed all nine together and
passed executable and selected-import preflight. Its ODM launcher failed for
missing `pyodm`; the disposable environment did not yet include the full app
requirements. Research builds and dataset outputs were not uploaded.

A subsequent [trial](https://github.com/Archont561/ODM-conda/actions/runs/40916199152)
added application dependencies and passed launcher help. Seneca (pinned at
`9220acfdca75cc5e2dd6d27fe48550c5ae0877f2`, candidate CC0, separate
provenance review still required) reached reconstruction, which failed because
OpenSfM's `numpy.array(..., copy=False)` is incompatible with NumPy 2. OpenSfM
build 4 constrains host and runtime NumPy to 1.26.x and adds an installed
regression smoke test. [Trial 40919353247](https://github.com/Archont561/ODM-conda/actions/runs/40919353247)
reconstructed 166 images and 198,644 points, then failed in statistics because
`matplotlib.cm.get_cmap` was removed. Research build 5 adds a Matplotlib
compatibility bound and installed API smoke test. These observations do not
establish successful end-to-end orthophoto generation, relocation, legal
clearance or reproducibility. Research artifacts and outputs remain disposable;
all release gates remain closed.

[Trial 40922527022](https://github.com/Archont561/ODM-conda/actions/runs/40922527022)
passed reconstruction and generated an intermediate orthophoto, but its crop
warned and report generation failed: PDAL/GDAL could not open the PROJ database.
The output was discarded and was not independently validated. A separate
[minimal probe](https://github.com/Archont561/ODM-conda/actions/runs/40927345299)
reproduced PDAL's EPSG:4326 failure without a PROJ environment path; setting
`PROJ_DATA` or `PROJ_LIB` to the installed prefix's `share/proj` fixed that
minimal operation. The local launcher now supplies both paths for the explicit
prefix. This is not yet proof of full dataset success: corrected dataset trials
[40927462919](https://github.com/Archont561/ODM-conda/actions/runs/40927462919)
and [40927535532](https://github.com/Archont561/ODM-conda/actions/runs/40927535532)
were canceled while running. Neither final raster metadata validation nor
relocation of the full installed environment has been demonstrated.

### Published four-component combined prefix (2026-10-29)

[Disposable run 40957790376](https://github.com/Archont561/ODM-conda/actions/runs/40957790376)
installed the four published channel packages together in a fresh Linux x86-64
prefix, explicitly pinning fpcfilter 0.2 build 1, dem2points build 2,
fastrasterfilter 1.0 build 2 and odm-orthophoto build 2. The component SHA256s
matched public channel records. Python 3.12, py-opencv, PDAL, Python-PDAL,
GDAL and ExifTool were also explicitly requested; the complete 322-package
filename/hash inventory is in
[component-build2-dependency-inventory.md](component-build2-dependency-inventory.md#published-four-component-combined-install-2026-10-29).
The solve selected Python 3.12.16, libgdal-core 3.12.2 `hc2c0581_0`,
libopencv 4.12.0 `qt6_py312h52d6ec5_612`, libpdal-core 2.10.0 `h9d23c72_0`,
and python-pdal 3.5.3 `np2py312hadcd02a_4`.

All four installed functional scripts ran in the **same** prefix and passed
both their generated-data fixtures and their executable `ldd` checks; Python
imports for OpenCV, GDAL and PDAL passed. These were separate synthetic
component tests, not outputs chained across components or a full ODM pipeline.
They establish only this time-sensitive solve on GitHub-hosted Ubuntu 24.04,
not older glibc runtimes, real-world photogrammetric quality or redistribution
rights for a dependency bundle. No packages, data or research binaries were
uploaded. Previous nine-component dataset trials still require rebuilding the
local-only research packages and rerunning the corrected PROJ launcher; this
four-component check neither runs nor validates that dataset. TASK-13 remains
open.

### Corrected Seneca end-to-end trial (2026-10-29)

[Disposable run 40960012356](https://github.com/Archont561/ODM-conda/actions/runs/40960012356)
completed the `--fast-orthophoto --skip-3dmodel` command on pinned Seneca
`9220acfdca75cc5e2dd6d27fe48550c5ae0877f2`, followed by a separate
`gdalinfo -json -stats` inspection of the final orthophoto and an existence/size
check of the report. The final GeoTIFF was 9,574 × 10,488 pixels, with four
Byte bands (red, green, blue, alpha), WGS 84 / UTM zone 17N (EPSG:32617),
and geotransform `[305965.44516317715, 0.0499987673227535, 0,
4545650.771905862, 0, -0.049998859538978]`. The reported band ranges were
0–255 for each band; means were 146.074, 127.342, 151.931 and 144.614,
respectively. The TIFF was 112,786,798 bytes and the PDF report 7,233,853
bytes. Metadata, finite band statistics and a successful command do **not**
validate geospatial accuracy, visual quality, crop completeness or the report's
contents; these outputs were discarded and were not independently viewed.

The run hash-verified the four published component binaries listed in the
four-package check above and the retained local-only inputs renderdem build 1
SHA256 `451a291036f9bf11c140464d088884ec8980051c5383a667b75d1be7637fea77`,
poissonrecon-odm build 3 SHA256
`1e61c71dd24d73802d90b2db89057db1a612548949c9952767b2f765df4e93ab`,
and mvs-texturing-odm build 2 SHA256
`af287aa4cb94f5b34e1e55d202e428123a1cc6d8ddc505ee74717e23ed92c4bc`.
It rebuilt, fresh-retested and audited OpenSfM build 5 (SHA256
`363dc4650de7a08fbeffa640de28bf377ed4dec7cbefd6801be2127e4be21309`)
and OpenMVS build 3 (SHA256
`eee9c2110d3a83cf9b0fc768d0a643d42e88fd7f3c399efc84c635d07a9d28cf`)
locally. The nine-component prefix preflight and launcher help passed; the
prefix contained `share/proj/proj.db` and the corrected launcher supplied
`PROJ_DATA` and `PROJ_LIB`. It selected libgdal-core 3.12.2 `hc2c0581_0`,
libopencv 4.12.0 `qt6_py312h52d6ec5_612`, libpdal-core 2.10.0 `h9d23c72_0`
and python-pdal 3.5.3 `np2py312hadcd02a_4`.

This was one disposable Ubuntu 24.04 run using a candidate CC0 dataset;
independent dataset provenance remains unverified. It does not demonstrate
reproducibility, full-prefix relocation, older glibc support, production ODM
packaging, or complete third-party source and notice rights. In particular,
OpenMVS includes restricted source despite build exclusions; no research
packages, restricted source, dataset images or outputs were uploaded. No
release gates were changed. TASK-13 and the research-component legal reviews
remain open.

### Reduced-copy OpenMVS Seneca trial (2026-10-29)

[Disposable run 40968370151](https://github.com/Archont561/ODM-conda/actions/runs/40968370151)
at `940470bd87eef3923e7ea786c64e84d61d8542e3` completed the nine-component
pipeline on Ubuntu 24.04 using OpenMVS **built from the verified physically
reduced copy**, rather than the original-tree build in run 40960012356. Two
copies matched the 3,274-file path/content fingerprint
`e64c1718c05d58ac74051a8a0a216febbcac7144898cea022d378af427549489` and
manifest SHA256 `560cc78034924dd9fd83b02c4fba448a66612fc493b86ae8c09da6f0b338ce3b`.
The run rebuilt and fresh-retested both research components and passed their
limited audits. Local OpenMVS build 3 SHA256 was
`8a16adfb63dab049e9e15a0879abc99dd2b7164348c7defc862bca93ba1004f9`;
OpenSfM build 5 was
`31b416c0f69ef2e76afde033b4b1a6d734bf5cb714d55d43bf8cfc75f0994237`.
The other seven package hashes and selected GDAL/PDAL/OpenCV dependencies
matched the preceding successful trial listed above. They are not all released
components: renderdem, PoissonRecon, mvs-texturing, OpenSfM and OpenMVS remain
research-only in this experiment. The temporary script at the run commit records
its exact inputs and commands. It verified ODM 3.6.2 archive SHA256
`5bdf8fe81b9ca47714e8a474139fd206b8090ac4315c2f530a58fcaef29cde5e`,
checked out Seneca commit `9220acfdca75cc5e2dd6d27fe48550c5ae0877f2`,
and invoked the prototype with `--skip-3dmodel`.

Preflight, launcher help, pipeline execution and `gdalinfo -stats` passed. The
final raster had 9,667 × 10,305 pixels, four RGBA Byte bands, EPSG:32617 and
geotransform `[305959.77768083906, 0.0499969077372014, 0,
4545641.752753492, 0, -0.0499959349708179]`. All bands reported 0–255;
means were 146.064, 127.328, 151.934 and 146.098. The TIFF was 113,227,130
bytes and the PDF report 7,262,535 bytes. Dimensions and extent differ from
the prior run; these runs do not isolate the cause or establish numerical or
visual equivalence. Metadata checks do not validate visual quality, geographic
accuracy, crop completeness or report contents. Dataset provenance remains
independently unverified. Research packages, original restricted source,
dataset imagery and generated outputs were discarded, not uploaded. The
original OpenMVS archive was still fetched before reduction, and this success
does not establish corresponding-source completeness, redistribution rights,
reproducibility or a production release decision. No gates changed.

### Asset-reduced OpenSfM runtime trial (2026-10-29)

[Run 40973960114](https://github.com/Archont561/ODM-conda/actions/runs/40973960114)
at `48e6b2b` repeated the disposable nine-component reduced-OpenMVS Seneca
experiment. OpenSfM and OpenMVS packages were built, normally installed-tested,
fresh-retested and audited **before** any experiment-specific modification.
In the disposable installed prefix only, the two pinned BoW/VLAD NPZ assets
and `sensor_data.sqlite` were SHA256-verified and deleted. An installed Python
functional check confirmed the JSON fallback returned 3,708 entries, including
`acer ce-5330: 5.75`. The Seneca `--fast-orthophoto --skip-3dmodel` pipeline
then completed and generated a TIFF and report with those three assets absent.
This shows that this one scenario can operate without them; it does **not**
validate BoW/WORDS matching, VLAD retrieval, cameras absent from JSON, other
configurations, or sensor-data rights. Removing the vocabularies breaks modes
that request them. The installed prefix was modified after audit; no reduced
package or corresponding-source bundle was generated or audited.

The raster was 9,545 × 10,629 RGBA Byte, EPSG:32617, with geotransform
`[305966.33103915723, 0.0499985548731397, 0, 4545656.007730301, 0,
-0.0499959729402635]`; band ranges were 0–255, and means were 145.988,
127.301, 151.866 and 142.717. TIFF and report sizes were 112,654,068 and
7,275,876 bytes. The job hit the Actions per-step notice limit, so the bounded
metadata was recovered from its completed log by read-only [run 40977152684](https://github.com/Archont561/ODM-conda/actions/runs/40977152684).
Outputs were not uploaded or visually or geographically validated. Dimensions
differ from prior trials; causation and equivalence are not established.

The newly built OpenSfM package SHA256 was
`c12f5ec3eb5e50cc1936503dd7fb46e098ea04dc3a6e3320a0ac3a1b2f2349d6`,
and reduced-copy OpenMVS package SHA256 was
`750a0dd55e70015ee1fc3249dd63ba3128ca07b4b3322fe3b24728067e344d33`.
The other seven inputs, pinned ODM and Seneca revisions match the preceding
trial. Original research archives and all runtime assets were fetched before
the deletions; no archive, binary, dataset or generated output was uploaded.
There is no reduced OpenSfM source distribution or legal approval, and the
original recipe still installs the assets. No gates were changed.

### Reduced-source candidates and Seneca integration (2026-10-30)

Private [run 41072814562](https://github.com/Archont561/ODM-conda/actions/runs/41072814562)
built the scoped OpenSfM package from its reduced primary archive, reduced-source
PoissonRecon, and OpenMVS build 4 from verified reduced copies. Each passed its
installed and fresh package tests and applicable research audit. The nine real
packages were installed into a fresh Pixi environment alongside integration
requirements, then selected binaries/imports and the ODM prototype preflight
passed. OpenSfM's three excluded assets were absent; default mode, explicit
WORDS/BoW/VLAD rejection and JSON sensor fallback passed. The chosen core
versions included libgdal-core 3.12.2 `hc2c0581_0`, libpdal-core 2.10.0
`h9d23c72_0`, libopencv 4.12.0 `qt6_py312h52d6ec5_612`, py-opencv 4.12.0
`qt6_py312h598be00_612`, and python-pdal 3.5.3 `np2py312hadcd02a_4`.
This records selected identities, not every transitive dependency or a general
ABI/security proof.

The nine package SHA256 identities were:

| Package | SHA256 |
| --- | --- |
| fpcfilter 0.2 b1 | `8d3949bf9fdb570e30afbcd91174ee5f80e9b8cd06525a26899642bc5ed1e679` |
| dem2points 0.0.0.dev20220721 b2 | `d7876edf091b2990e1b9325e0f6cd0ae2a4e863ab5499edacf267e5d3fd4996f` |
| fastrasterfilter 1.0 b2 | `2738b09958d6b57360065ca5e68b1bcbe96a6f5c727cd0e3cdba1f8b018096c4` |
| odm-orthophoto 0.0.0.dev20250225 b2 | `c64be4380202cfe6e41cc41ac4ec171d25f2ceaaf45b666a21a2250f3b6ae614` |
| renderdem 1.0 b1 | `451a291036f9bf11c140464d088884ec8980051c5383a667b75d1be7637fea77` |
| mvs-texturing-odm 0.0.0.dev20250818 b2 | `af287aa4cb94f5b34e1e55d202e428123a1cc6d8ddc505ee74717e23ed92c4bc` |
| reduced PoissonRecon 13.8 b3 | `7e4775fed953c3e3453e02971d4f9c96396d10e882a199081b9bfcea52e2eaf1` |
| reduced-source opensfm-scoped-odm 0.5.2 b0 | `e1ab0126083e77abd922970718e347b0b641264d67161008489df5e3e287dc30` |
| reduced-copy openmvs-odm 0.0.0.dev20260516 b4 | `8a64bf79186c9078fb91b4f9ba1d3234c843e49aebb058a82184fed74efec9a0` |

The Seneca fast-orthophoto pipeline completed. Its raster was 9563 × 10541 RGBA
Byte, EPSG:32617, geotransform `[305964.5459215405, 0.0499953893421963, 0,
4545652.637375606, 0, -0.0499993851093828]`; band means were 146.24, 127.5,
152.07 and 143.513. The TIFF was 112,964,268 bytes and the report 7,327,735
bytes. A separate read-only [run 41078491919](https://github.com/Archont561/ODM-conda/actions/runs/41078491919)
recovered those bounded metadata from the completed job log. The original
archives, packages, dataset and results were discarded, not uploaded. Dataset
rights and visual/geographic quality remain unverified; this is one scenario,
not production source, license, security or release approval.

### Seneca dataset rights evidence and raster sanity (2026-10-30)

At pinned dataset commit [`9220acfdca75cc5e2dd6d27fe48550c5ae0877f2`](https://github.com/OpenDroneMap/odm_data_seneca/tree/9220acfdca75cc5e2dd6d27fe48550c5ae0877f2),
`license.txt` contains the CC0 1.0 Universal text (Git blob
`670154e3538863b2d9891fd5483160fbdfc89164`; SHA256
`36ffd9dc085d529a7e60e1276d73ae5a030b020313e6c5408593a6ae2af39673`),
and GitHub identifies the repository license as CC0-1.0. Its `README.md` (Git
blob `894cb4da57505748a511cf0d07635a7791cbfea7`, SHA256
`36aab03baf4a6eff9f989a1eb9a66d53910eceb9990c5a496f96cbb0509ac938`)
attributes the aerial dataset to the Ohio Department of Transportation and says
it was captured 2013-06-04. The pinned tree lists 167 image blobs. The license
file was added in the pinned commit by Stephen Mather in 2019; the observable
image introduction was commit `6a634677e27ce09292493d53f873599980a70a9d`
in 2016. This establishes repository statements and history, not that the
person adding the waiver controlled all image rights, or that privacy and other
non-copyright issues are resolved. Qualified review remains needed before
assuming the dataset meets TASK-13's release-quality rights criterion.

`scripts/odm_raster_sanity.py` checks positive dimensions, finite non-degenerate
geotransform, a non-empty CRS, at least three bands and finite, internally
consistent GDAL statistics; Byte values must be 0–255. Unit negative cases and
a generated 16 × 16 three-band EPSG:32617 GeoTIFF passed locally with GDAL.
These are basic numerical checks, not visual inspection, geographic accuracy,
expected-extent validation, image rights verification or a rerun of Seneca.

[Read-only run 41084604140](https://github.com/Archont561/ODM-conda/actions/runs/41084604140)
recovered the prior completed Seneca trial's GDAL summary from its job log and
applied these sanity checks successfully to its 9563 × 10541 raster metadata.
No raster was retained or re-opened; this is not a new pipeline run or visual
and geographic verification.

### Fresh nine-component Seneca and live raster sanity recheck

[Private run 41090003564](https://github.com/Archont561/ODM-conda/actions/runs/41090003564)
built and audited reduced Poisson, scoped OpenSfM and reduced-tree OpenMVS,
installed them with the six verified local components, passed the selected
preflight and scoped mode guards, and completed the pinned Seneca pipeline.
The live output was checked using `odm_raster_sanity.validate` on GDAL JSON
statistics. It reported a 9639 × 10534 RGBA Byte orthophoto, EPSG:32617, and
geotransform `[305960.43959553825, 0.0499963214392767, 0, 4545650.983157054, 0, -0.0499957661019422]`.
Per-band means were 146.252, 127.609, 152.272 and 143.298. The raster and report
were discarded; the bounded log evidence was recovered by
[run 41095611381](https://github.com/Archont561/ODM-conda/actions/runs/41095611381).
This is not visual or geographic accuracy validation, dataset-rights clearance,
complete runtime validation, or permission to release the software.

### OpenCV 4.13 private integration

[Run 41102357808](https://github.com/Archont561/ODM-conda/actions/runs/41102357808)
completed Seneca with three private OpenCV 4.13 research variants and the other
six components in a combined environment constrained to OpenVINO >=2026.0.
The live raster passed GDAL metadata/statistics checks: 9508 × 10599 RGBA Byte,
EPSG:32617; band means 146.368, 127.388, 151.957 and 142.319. Raster and
report were discarded. The exact resolved OpenVINO version was not recorded.
This is functional evidence for this run only, not visual/geographic quality,
dataset-rights clearance or release approval.

## Private Conda application candidate (earlier 2026-10-30 trial)

The version of the research-only `odm-fast-research` recipe tested in this earlier trial
packages the pinned, prefix-patched ODM 3.6.2 application and installs a
relocatable `odm-fast-research` launcher. It declares the nine component names
and the Conda runtime dependencies used for this experiment. It is limited to
`--fast-orthophoto`, rejects point classification and split/merge, and requires
five additional PyPI dependencies; it is **not a self-contained or publishable
ODM package**.

[Private run 41124481691](https://github.com/Archont561/ODM-conda/actions/runs/41124481691)
built `odm-fast-research-3.6.2-hb0f4dca_0.conda` (SHA256
`33edc1236acad9b6bb96764bfc9156d9536cc42717f1139316d31ec426fae044`)
and installed it through a loopback-only channel containing the nine actual
component archives. The candidate's Conda dependencies pulled those nine
components; the five PyPI requirements were added separately. A copied,
byte-identical lock (SHA256
`3509f09317a47e7aeef40e27a29295b2fd776e0a112364d450669e29e17b2cb6`)
was installed into a relocated prefix with isolated caches, producing 425
matching Conda records. The installed package launcher ran help and the Seneca
fast-orthophoto pipeline; final raster and report existed and metadata/statistics
sanity checks passed. This is not visual/geographic accuracy or dataset-rights
validation. The build skipped rattler's own test phase because the component
packages were not yet available in its build channel; the later relocated
integration exercised the installed package, not a separate rattler test.

This was a new private solve, not a byte-identical rebuild of the older replay.
Three published components and two retained build artifacts were retrieved by
hash; orthophoto, reduced Poisson, scoped OpenSfM and reduced OpenMVS were
privately rebuilt and individually tested/audited. The lock, archives, dataset
and output were discarded, and the temporary trial is not an automated release
pipeline. Availability of those historical retained artifacts is not guaranteed.

The earlier trial built its recipe with the repository's locked tools (network
access to conda-forge and the pinned ODM archive required):

```sh
pixi run rattler-build build --recipe research/recipes/odm-fast-research/recipe.yaml \
  --target-platform linux-64 --variant-config recipes/variants.yaml \
  --channel conda-forge --channel-priority strict --output-dir /private/odm-build \
  --test skip
```

In that earlier trial, the five PyPI dependencies were added separately. **Do not
use these older instructions against the updated recipe:** the later Conda-only
trial and its updated requirements are described below. Neither trial establishes
full ODM feature support or an offline, future-proof build.

**Publication remains blocked.** OpenMVS and OpenSfM variants are explicitly
unreviewed, production source/notice obligations and other component gates
remain open, the Conda metadata does not capture the PyPI dependencies, and the
older trial reused some production package identities with different bytes.
Distinct reviewed package identities, independently retained sources, native
validation, dependency packaging, qualified review and owner-controlled release
gates are required before publication to Prefix. No gate was changed.

## Conda-only private installation and research build identities (2026-10-30)

In this historical trial, the five previously separate PyPI distributions had
local-only Conda wheel-repack recipes (since superseded by source recipes).
Each repack takes an exact SHA256-pinned upstream wheel, installs it offline
without dependencies during its build, and declares its Conda runtime
requirements. These are **wheel repacks, not source-built packages**. In
particular the JPEG XL wheel includes a native extension and may contain bundled binary code; its
corresponding source, native dependencies, provenance and release
obligations remain unverified. `LicenseRef-Unreviewed` is intentional. Independent
[run 41129610665](https://github.com/Archont561/ODM-conda/actions/runs/41129610665)
built and fresh-tested all five imports. [Run 41132661773](https://github.com/Archont561/ODM-conda/actions/runs/41132661773)
also tested a lossless JPEG XL image round-trip. The JPEG XL test addition was
validated separately, after the combined run's immutable commit.

The OpenCV 4.13 orthophoto experiment, reduced Poisson, reduced OpenMVS and
scoped OpenSfM now use `research_...` build strings, so their Conda identities
are distinct from the earlier production-style artifacts with the same name and
version. The ODM recipe at the time required these research builds and all five
`odm-research-*` repacks. Distinct strings reduce identity collisions; they do
not make the packages authorized for publication or guarantee that rebuilding
the same recipe will produce identical bytes.

[Private integration run 41129908688](https://github.com/Archont561/ODM-conda/actions/runs/41129908688)
built the new candidates and installed ODM with **no PyPI entries or separate
PyPI additions**. It copied the lock and all 15 local archives to a different
directory, removed the original channel, and installed into a fresh prefix with
isolated caches. The byte-identical lock SHA256 was
`8fadfcfd5fdcf973491b46bcc92022eeeaa457a5eb2c156a6cb9d267e812aac0`;
all 440 Conda package identity/hash/URL records matched. The installed launcher
completed the Seneca fast-orthophoto pipeline; raster and report existence and
raster metadata/statistics sanity passed. Rattler's own test phase for the ODM
application candidate was skipped; its installed launcher and pipeline were
exercised in the later integration. The individual wheel repacks passed their
package tests during the run. As before, three published components and two
previously retained component artifacts were obtained by hash; not every
component was rebuilt in this run. Temporary binaries, lock, source archives
and imagery were discarded; the hashes are evidence, not a reusable bundle.

In that historical trial, building a private channel required the five wheel-repack recipes,
the OpenCV 4.13 variant via `scripts/prepare_opencv413_research.py`, the
reduced-source Poisson and scoped OpenSfM candidates, reduced OpenMVS, the ODM
recipe, and the remaining compatible components. The research preparers require
exact pinned inputs and a destination outside the checkout. Index those resulting
archives using `scripts/private_conda_channel.py`, serve the channel on loopback
only, and solve `odm-fast-research` with that channel before conda-forge. A
retained private Pixi lock, manifest and all exact archives are needed to replay
a particular solve. This trial still used online conda-forge and a disposable
runner; it does not establish an offline build, a publicly installable package,
full ODM modes, visual/geographic correctness or dataset rights. Normal source,
license, audit and owner-controlled release gates remain unchanged.

A final [repeat integration 41134867203](https://github.com/Archont561/ODM-conda/actions/runs/41134867203)
used the updated JPEG XL round-trip test and bumped ODM candidate build number
1 to distinguish its changed dependency metadata from the earlier build 0. It
built `odm-fast-research-3.6.2-hb0f4dca_1.conda` SHA256
`e89cf0198902e01c9b3e5970bdbf93d6081c9fea4fff2dc2c896b7fe20e23a60`,
replayed lock SHA256
`551ba9fa9d15ebdfd47dab13a629b1e8d39c60362e0ff38875af3922faa5cffe`
with 440 matching Conda records and no PyPI entries, and passed the installed
launcher, Seneca and raster sanity checks. The same limitations and disposal
policy apply. Identity changes do not make rebuilds byte-reproducible: separate
runs produced different package hashes even for some unchanged build strings.

## Source-built private Python runtime (2026-10-30)

The five earlier wheel-repack recipes have been replaced by private research
recipes under [`recipes/python-source-research`](recipes/python-source-research).
PyODM, Pysolar, pygltflib and CODEM use SHA256-pinned upstream source
distributions, build with preinstalled Conda tooling, and install with pip's
`--no-index`, `--no-build-isolation` and `--no-deps` options. Their individually
built packages and fresh import retests passed in
[run 41139276835](https://github.com/Archont561/ODM-conda/actions/runs/41139276835).
The source variants have build number 1, distinct from the earlier wheel repacks.

JPEG XL uses the SHA256-pinned source distribution and its Cargo.lock. The
private preparer `scripts/prepare_jxl_source.py` checks the source hash and
registry-only locked crate checksums, runs `cargo vendor --locked` into a new
local directory, verifies the crate set and vendor checksum metadata, and
switches the exact upstream maturin configuration from vendored to dynamic
linking. Preparation requires Cargo and access to crates.io; it must not be
mistaken for an offline source acquisition. The subsequent Conda build uses
`maturin --locked --offline --auditwheel skip` with staged crates and Conda
native libraries. [Run 41140647274](https://github.com/Archont561/ODM-conda/actions/runs/41140647274)
verified that the resulting extension's ELF `NEEDED` entries include
`libjxl.so.0.11` and `libjxl_threads.so.0.11`, and passed fresh package tests
including the lossless JPEG XL round-trip. This is targeted linkage evidence,
not a complete binary, source or legal audit. That run also exercised the later
crate-set validation; the integration run below used the preceding preparer.

For a private build, obtain the exact pinned JPEG XL source archive listed in
its recipe, then with Cargo installed and network access run:

```sh
pixi run python scripts/prepare_jxl_source.py --source /private/pillow-jxl-source.tar.gz \
  --destination /private/jxl-prepared
pixi run rattler-build build --recipe /private/jxl-prepared/recipe/recipe.yaml \
  --target-platform linux-64 --variant-config recipes/variants.yaml \
  --channel conda-forge --channel-priority strict --output-dir /private/jxl-build
```

The destination must not exist and must be outside the checkout. Build the
other four source recipes normally with rattler-build, run their tests, and
assemble them and the compatible ODM/component packages in a private channel.
The staged Cargo source tree and dependency packages are not retained here.

[Private integration run 41139889906](https://github.com/Archont561/ODM-conda/actions/runs/41139889906)
built all five source candidates, the other research variants and ODM build 2,
then installed from a loopback-only Conda channel without PyPI lock entries.
The ODM candidate was `odm-fast-research-3.6.2-hb0f4dca_2.conda`, SHA256
`3b4fac8f2755300d4765125c02b28894ff6221241c58dd87910400af5f160c06`.
A byte-identical relocated lock SHA256
`5ac9c3df78ed7fd205b199b28c05bca546caed1020f353ba2fc68611a607be7a`
produced 456 matching Conda identity/hash/URL records in the fresh prefix. The
installed ODM launcher completed the Seneca fast-orthophoto run and raster
sanity checks. ODM's rattler test phase was skipped; the installed package was
exercised by the integration. Some component inputs came from existing verified
artifacts rather than fresh builds. Outputs, original lock, sources and binaries
were discarded; this is not a retained replay bundle or a reproducible-build
claim.

The package names, `LicenseRef-Unreviewed` metadata, isolated test channel and
existing release gates remain research-only. Build success does not establish
complete corresponding sources for the Conda runtime or Rust dependencies,
notice sufficiency, Seneca dataset rights, full ODM feature coverage, native
security review or authority to publish. The five sources' build tools and
Conda dependencies were solved online; preparation/builds are not fully offline.

### TASK-92: private source build and binary replay (in progress)

`scripts/private_odm_bundle.py` is an experimental orchestration path, **not a
release or corresponding-source offer**. It attempts the fifteen source-built
private packages, creates a local channel, and retains a Pixi manifest and lock
only in a new owner-controlled directory outside the checkout. It checks the
channel package hashes, lock selection, a relocated locked installation and the
installed Conda inventory. An optional dataset runs in a temporary copy; derived
imagery is discarded. Source builds and conda-forge downloads require network
access; the bundle does **not** retain all sources, conda-forge packages, build
tools or transitive dependencies and is not an offline or bit-reproducible build.

On a trusted linux-64 machine with the repository's Pixi tools installed, use:

```sh
pixi run python scripts/private_odm_bundle.py build --destination /private/path/odm-bundle
# Optionally add --dataset /private/path/dataset to exercise ODM processing.
pixi run python scripts/private_odm_bundle.py replay --bundle /private/path/odm-bundle --manifest-sha256 <independently-recorded-sha256>
```

The destination must not exist, its parent must already exist, and it must be
outside this repository. The directory is created private to the invoking user;
keep it on access-controlled storage. Record the printed manifest SHA256 through
a separate trusted channel: the JSON file's own checksums detect accidental
changes but do **not** authenticate a bundle if an attacker can replace both
files and manifest. Replay uses a fixed loopback port from the lock; other local
users can access that HTTP endpoint while it is running, so use an isolated host
and do not treat loopback as authentication. Relocated replay needs the same
available port and access to external conda-forge binaries. Rebuilds may produce
different bytes despite identical package identities.

The restricted original OpenMVS archive, omitted assets, unresolved licenses,
notices and rights remain outside any publication approval. No package, source,
lock, dataset or output may be uploaded merely because this research build works.
Hosted end-to-end validation of this new orchestrator remains in progress; prior
TASK-91 evidence does not establish that the whole orchestration succeeds.
