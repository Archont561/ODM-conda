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
