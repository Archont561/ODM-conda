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
