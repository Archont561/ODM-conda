# ODM linux-64: initial runtime dependency mapping

This mapping examines pinned ODM 3.6.2 commit
`47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45` (archive SHA256
`5bdf8fe81b9ca47714e8a474139fd206b8090ac4315c2f530a58fcaef29cde5e`)
and the current repository recipes. It is **not** a solved environment, complete
command enumeration, proof of package availability/compatibility, rights review,
or an approved production dependency contract.

## Dense reconstruction and dem2mesh: concrete blockers

| ODM call | Current candidate | Actual gap / next validation |
| --- | --- | --- |
| `DensifyPointCloud` from `stages/openmvs.py`, via `opendm/context.py` | `openmvs-tetraflow-research` | The [builder](../scripts/build_openmvs_tetraflow_research.py) restricts `apps/CMakeLists.txt` to ReconstructMesh, removes SceneDensify.cpp, and installs **only ReconstructMesh**. Its synthetic mesh and fast-orthophoto evidence does not provide or test DensifyPointCloud. A separate dense-capable source/build must be designed, reviewed, built and tested with actual scene, images and a full ODM run. The source/rights blockers in the release inventory remain. |
| `dem2mesh` from `opendm/mesh.py` | [registered recipe](../recipes/dem2mesh/recipe.yaml), linux-64, build 1 | Host and run require `libgdal-core >=3.11,<3.12`, which excludes GDAL 3.12.2 used by the [TetraFlow/PDAL research solve](odm-tetraflow-pdal-linkage-evidence.json). This is a metadata-constraint conflict, not a newly run solver. Build and test a distinct research candidate against the chosen GDAL baseline before considering a production rebuild; do not loosen installed binary metadata. All four release gates remain false. |
| `dem2points` / `PoissonRecon` / `ReconstructMesh` / `texrecon` | Published or reduced research component recipes | Paths are present in upstream mesh stages but testing individual tools or fast-orthophoto does not validate every 3D path. Choose exact package identities, review scope/rights and run complete 2.5D and 3D datasets. |

## Additional external tools and model

* Classification runs PDAL SMRF then `pcclassify` with OpenPointClass. Upstream
  [`External-OpenPointClass.cmake`](https://github.com/OpenDroneMap/ODM/blob/47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45/SuperBuild/cmake/External-OpenPointClass.cmake)
  pins OpenPointClass commit `dd6a560a1d43cb709f7b220b19a436e25a889e3e`,
  PDAL, Eigen 3.4 and `WITH_GBT=ON`. No matching registered recipe was found
  in this repository. A GitHub lookup for a conda-forge `pcclassify` or
  `openpointclass` feedstock returned 404; that is **not** proof no package
  exists under another name. Investigate source, license, model, ABI and build.
* `opendm/opc.py` requests `vehicles-vegetation-buildings.zip` from the
  OpenPointClass v1.1.3 GitHub release and passes cache version `v1.0.0` to
  `get_model` as `model.bin`. `opendm/ai.py` caches under application-relative
  `storage/models`, downloads when absent and extracts a ZIP. The model hash,
  rights, safe extraction, writable cache and offline policy are not established.
  Failure is caught and logged by upstream classification, so an exit-success
  pipeline alone cannot establish that model-based classification happened.
* `opendm/entwine.py` uses `entwine build`, falling back to `untwine` for EPT;
  COPC calls `untwine`, and `opendm/ogctiles.py` additionally calls `entwine
  convert`. [entwine-feedstock](https://github.com/conda-forge/entwine-feedstock)
  and [untwine-feedstock](https://github.com/conda-forge/untwine-feedstock)
  exist; their relevant linux-64 builds, CLI compatibility and ABI with the final
  lock have not been validated. Test EPT, COPC and 3D tiles independently.
* GDAL, PDAL, ExifTool and other utilities are used by stages. The fast preflight
  list is a useful starting point, not exhaustive; command paths and plugin
  dependencies must be checked against the actual final installed prefix.

## Python requirements

[Machine-readable name comparison](odm-python-requirement-map.json) maps every
upstream pinned `requirements.txt` entry to an apparent direct run declaration
in the fast research recipe, including research-only aliases for five source
packages. Reproduce with
`pixi run python scripts/map_odm_python_requirements.py`. A missing direct
entry is **not** evidence of an absent transitive package, and an existing
name is not proof the upstream pinned version or ABI was selected.

The fast recipe does not directly declare `rawpy`; upstream imports it in
`opendm/ai.py` and `opendm/get_image_size.py`. A
[rawpy-feedstock](https://github.com/conda-forge/rawpy-feedstock) exists, but
its exact usable version, LibRaw linkage and image format behavior need a final
solve and tests. The name comparison also exposes upstream direct requirements
not explicitly declared by the fast recipe, including numpy, Pillow, pyproj,
rasterio, scipy and PyYAML. These may be installed transitively; inspect the
**actual final lock**, rather than assuming availability or absence.

The research aliases for CODEM, PyODM, Pysolar, pygltflib and the JXL plugin
are not production approvals. GitHub feedstocks exist for CODEM, Pysolar,
ExifRead and fpdf2, but this observation does not establish the upstream
version, channel availability, native compatibility or rights for a release.
The `pillow-jxl-plugin`, `pyodm`, and `vmem` feedstock name lookups returned
404; alternate package names or channels have not been excluded.

## Required next experiment

Build a **separate, non-publishable** dem2mesh candidate against the existing
GDAL 3.12.2 research baseline, run its functional fixture and audit, and solve
it together with the exact retained ODM research lock where available. A new
solve or rebuilt package is a new candidate, not a replay of the old lock.
Then develop a dense-capable OpenMVS research build without bypassing source,
linkage, audit or release safeguards. No publication or owner approval is
implied by these experiments.

### Disposable GDAL 3.12 dem2mesh experiment

[Run 43527760101](https://github.com/Archont561/ODM-conda/actions/runs/43527760101)
built a separate `research_873e7db_1` candidate by changing the **staged copy**
of the recipe's host and run bounds to `libgdal-core >=3.12.2,<3.12.3`.
The packaged functional test, fresh package retest and standard package audit
passed. Its generated constraints include both that explicit bound and the
rattler-generated GDAL ABI bound. No production recipe or gate was changed.

The job downloaded the earlier research bundle and verified its manifest
against the previously recorded SHA256
`81da120940a5236657854b51b9713aae0e40dbd11199a51859197837e21c3c7b`.
It installed the unchanged old lock and matched its 432 package identities,
then **made a new solve** adding dem2mesh from a temporary channel. The new
433-record installed inventory had one addition (dem2mesh) and no removed
records; the installed dem2mesh functional fixture passed in that full-stack
prefix. The candidate SHA256 was
`0dac6bca08120c8eb746a35a8f3b313f7e5a88ff85ffb7757408d6e4dfc9aed5`.
See [bounded evidence](odm-dem2mesh-gdal312-research-evidence.json). The new
package and lock were discarded, and no artifact was uploaded in this run.
This is not an ODM mesh pipeline, a byte-for-byte installed-file audit,
corresponding-source verification, license approval or a final release solve.

A [CPU dense research follow-up](openmvs-dense-research.md) builds both native
tools and passed a bounded standalone dense scene test. It found an ODM CLI
blocker: the CPU-only binary rejects the `--cuda-device -2` flag ODM passes.
A follow-up CPU-only compatibility patch passed an experimental ODM run through the dense stage with an explicit binary overlay. It is not a complete ODM run, solved release package or release approval.
