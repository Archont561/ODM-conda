# CPU dense OpenMVS: private research candidate

A **non-publishable**, CPU-only candidate is provided in
[`openmvs-dense-research`](recipes/openmvs-dense-research/recipe.yaml), distinct
from the ReconstructMesh-only research candidate. It uses the same pinned
TetraFlow source and Eigen input; it builds `DensifyPointCloud` as well as
`ReconstructMesh`, and does not build SceneRefine or SceneTexture. It retains
explicit source fingerprints, two named-input link-map checks, package tests
and a bounded package payload/notice/RPATH audit. These checks do not prove
source rights or a complete corresponding-source offer. CUDA is disabled.

[Run 43614231081](https://github.com/Archont561/ODM-conda/actions/runs/43614231081)
built and fresh-retested the package; mesh synthetic tests, CPU dense help,
`ldd`, both link-map checks and package audit passed. A fresh independent solve
then installed the built package and ran CPU `DensifyPointCloud` against the
hash-verified upstream four-image test scene from OpenMVS commit
`8e4c5f31a16e0e329132c8f26e20a8c5d7b47f53`. It produced a dense scene and a
binary PLY with **28,116 vertices**. The validator bounded count and size and
checked the first point for finite coordinates; it did not establish all-point
validity, scientific accuracy or full ODM integration. The source archive,
dataset (whose rights remain unverified), package and outputs were discarded;
no artifact was uploaded. See [evidence](openmvs-dense-research-evidence.json).

## Historical CPU compatibility blocker

ODM's pinned `stages/openmvs.py` always passes `--cuda-device -2` for CPU.
[Run 43613861226](https://github.com/Archont561/ODM-conda/actions/runs/43613861226)
showed this CPU-only candidate rejects `--cuda-device` as unrecognised, so it
**could not be substituted into the ODM stack**. That earlier standalone
test omitted the flag; it did not fix ODM or prove ODM dense processing works.
The subsequent CPU-only compatibility experiment is described below. A complete
end-to-end dataset, packaged integration and GPU support remain unvalidated. Full release source, licensing, model,
compatibility and owner gates remain open.


## CPU compatibility experiment

The research-only build 2 applies a pinned local patch that accepts ODM's
`--cuda-device -2` **only** in a CPU-only build and rejects GPU values such as
`-1` and `0`; it does not claim GPU support. [Run 43617563581](https://github.com/Archont561/ODM-conda/actions/runs/43617563581)
built, retested and audited it, verified rejection of those GPU selectors, and
ran the upstream test scene with the explicit CPU selector (28,087 points;
bounded validation). See [CPU evidence](openmvs-dense-cpucompat-evidence.json).

The same run verified and installed the earlier anchored 432-package research
lock, then explicitly overlaid the new `DensifyPointCloud` binary into its
prefix **outside Conda metadata**. Calling the installed patched ODM `run.py`
directly, bypassing its fast-only research launcher, with `--no-gpu`,
`--end-with openmvs`, low feature/point-cloud quality and 35 consecutive
Seneca images produced `scene_dense.ply` and
`scene_dense_dense_filtered.ply`. Checks verified nonempty output files, not
point count or geometric accuracy for this dataset. This is an experimental
through-OpenMVS-stage test, not an end-to-end product run, solved package set,
installed-byte audit, final release, rights clearance or GPU test. The new
package, overlay, downloaded datasets and outputs were discarded; no artifact
was uploaded. The initial stage test `43617157159` checked the wrong output
directory and failed its output assertion; the successful run checks the
upstream-defined location.

## Packaged CPU dense orthophoto integration

A distinct private [`odm-dense-research` recipe](recipes/odm-dense-research/recipe.yaml)
now requires both `openmvs-dense-research` build 3 and the private GDAL 3.12
`dem2mesh` candidate. Its relocatable launcher forces CPU, performs bounded
prefix/import checks, and rejects selected unsupported options. The restriction
list is not exhaustive and is not a security boundary. Neither package is a
production release or a complete ODM feature contract.

Initial packaged [run 43619163842](https://github.com/Archont561/ODM-conda/actions/runs/43619163842)
solved and replayed 435 package identities without an overlay, but the ODM run
failed in FPCFilter: the new OpenMVS PLY lacked the scalar `views` field that
FPCFilter expects. The historical ODM OpenMVS fork wrote per-point view counts;
the new upstream writer no longer emits them on that path.

Build 3 adds a pinned, targeted ODM PLY export: it writes actual per-point
view counts for the DensifyPointCloud dense and filtered outputs; it fails if
colors, normals or view data are missing, or any point has zero or more than
255 views. It does not replace general OpenMVS PLY serialization. It preserves
existing mesh tests and source/link/payload audits. No values are fabricated.

[Run 43619978302](https://github.com/Archont561/ODM-conda/actions/runs/43619978302)
built and fresh-retested the dense OpenMVS, dem2mesh and ODM research packages,
solved them together, installed a relocated copy of the unchanged new lock and
matched all 435 Conda identities. No binary overlay was used. The standalone
upstream-scene test validated all 27,942 PLY records for finite coordinates and
normals and nonzero view counts. The packaged launcher then completed a CPU
dense **orthophoto** pipeline on 35 Seneca images with `--skip-3dmodel`,
producing a dense PLY, orthophoto and report; the orthophoto passed existing
raster sanity checks. See [integration evidence](odm-dense-package-integration-evidence.json).
This does not test full 3D models, all ODM features, GPU, scientific accuracy,
source completeness, rights or final release. The research packages, new lock,
input datasets and outputs were discarded and not uploaded. The old artifact
was used only as an anchored source of preexisting binary packages, not as the
new solve or a final owner-retained release.

## Packaged CPU 3D model follow-up

[Run 43620723254](https://github.com/Archont561/ODM-conda/actions/runs/43620723254)
rebuilt the three research packages, solved and replayed a relocated 435-package
lock without a binary overlay, and ran the packaged ODM launcher on 35 Seneca
images with **3D model generation enabled** (`--mesh-octree-depth 8`,
`--mesh-size 100000`). It completed the CPU dense reconstruction, 3D Poisson
mesh, texturing, orthophoto and report pipeline. Bounded checks found a 3D OBJ
with 27,035 vertices, 46,442 triangular faces, 25,038 texture coordinates, one
material file and three nonempty referenced textures; coordinates were finite
and face vertex/UV indices valid. Orthophoto raster sanity also passed. Texture
image decoding, scientific/geometric accuracy, GPU and other ODM modes were not
established. The independently installed test-scene dense PLY had 28,009 finite
points with nonzero view counts. [Evidence](odm-dense-3d-integration-evidence.json)
records the exact disposable package identities and lock hash. These are fresh
builds, not the previous run's retained bytes. The new lock, packages, dataset
and outputs were discarded; no artifacts were uploaded. Rights, source
completeness and all owner release gates remain open.

### Private classification integration

[Run 43622003039](https://github.com/Archont561/ODM-conda/actions/runs/43622003039)
built the research OpenPointClass with staged, pinned LightGBM sources and no
build-time fetch. The installed classifier processed 2,500 synthetic LAZ points
(301 class 1, 2,199 class 3); this is a smoke test, not an accuracy measurement.

[Run 43622341689](https://github.com/Archont561/ODM-conda/actions/runs/43622341689)
built and retested the classifier and CPU dense packages, replayed a relocated
436-package lock without a binary overlay, then processed 35 Seneca images with
`--pc-classify`. PDAL reported 37,333 output points, classification minimum 1
and maximum 6; the run also validated raster and textured OBJ structure. The
pipeline checks classification output rather than relying on ODM's exit status:
upstream catches OpenPointClass errors. See
`odm-classification-integration-evidence.json` for package identities, limits,
and a correction to an incorrectly labelled hash in the workflow annotation.
The locked environment, binaries, model, input and outputs were discarded.

For explicit `--pc-classify`, the private launcher requires
`ODM_RESEARCH_MODEL_ROOT` to be an absolute external directory containing the
observed model at `openpointclass/v1_0_0/model.bin`; it checks the model hash
and disables automatic download in this explicit research path. No model is
packaged. This is not a general offline/security boundary. Upstream normally
catches classifier failures; build 3 propagates them when this explicit offline
model root is set and preserves the original input if the command fails or its
output is missing or empty. [Run 43624514505](https://github.com/Archont561/ODM-conda/actions/runs/43624514505)
retested build 3 with installed-module fault injection and a complete 35-image
classification pipeline (41,276 points, classification range 1–6). Fault
injection was at module level, not a full-pipeline injected crash. See
`odm-classification-failure-integration-evidence.json`. Model rights, full
source/license review, classification accuracy and production distribution remain
unresolved.

### Split/merge exploratory test

The private launcher continues to reject explicit split and image-group flags;
the restriction is not an exhaustive security boundary. In
[43624514478](https://github.com/Archont561/ODM-conda/actions/runs/43624514478),
a direct invocation of the installed app deliberately bypassed that restriction
to try local split/point-cloud merge on the 35-image Seneca set, with two
overlapping explicit groups. The relocated package replay passed, but processing
stopped with an upstream reconstruction error before a verified merge. A repeat
[43626013062](https://github.com/Archont561/ODM-conda/actions/runs/43626013062)
also failed; the precise reconstruction cause has not been isolated. Diagnostic
run [43627528100](https://github.com/Archont561/ODM-conda/actions/runs/43627528100)
failed too, and its first-error extraction accidentally captured normal feature
matching failures instead of the fatal cause. These are not split/merge passes.
The trial data, packages and lock were discarded. Next investigate the first
fatal submodel error with bounded logs, use a verified splitting fixture, and
validate at least two input clouds and the merged output before enabling split.

#### Isolated causes (follow-up)

[43630323149](https://github.com/Archont561/ODM-conda/actions/runs/43630323149)
captured the first fatal traceback: repeated nested submodels eventually caused
OpenSfM `create_tracks` to fail with `OSError: [Errno 40] Too many levels of
symbolic links`. The pinned ODM `get_submodel_argv` removes `--split` but does
not remove explicit `--split-image-groups`; each child receives that option and
is split again. This is a finding for this explicit-groups trial, not a claim
that every split configuration has the same problem.

In a **temporary source-overlay** experiment,
[43632509764](https://github.com/Archont561/ODM-conda/actions/runs/43632509764)
removed that child argument: two submodels produced point clouds, but merging
failed with exit 127, which ODM caught and logged while exiting successfully.
Upstream invokes `lasmerge`; its absence from PATH was confirmed in the next
run. A second overlay replacing it with PDAL merge
([43633295453](https://github.com/Archont561/ODM-conda/actions/runs/43633295453))
returned exit 1 and left an empty output. Its underlying error was not captured;
this does not validate a PDAL replacement. More detail and boundaries are in
`odm-split-failure-isolation.json`. The overlays were not incorporated into the
package, and split remains unsupported. Next capture the PDAL command's first
error; test any replacement for count, coordinates, attributes and CRS, and make
merge failures visible instead of accepting ODM's success exit alone.

#### PDAL offset diagnosis and bounded merge experiment

[43634979874](https://github.com/Archont561/ODM-conda/actions/runs/43634979874)
captured the earlier PDAL error: a scaled Y coordinate exceeded the LAS signed
32-bit range. An independent probe using automatic scales and offsets succeeded;
that probe alone did not validate data preservation.

In [43635826329](https://github.com/Archont561/ODM-conda/actions/runs/43635826329),
a temporary **source overlay after package replay**, not a packaged fix, removed
the recursive child grouping argument, used PDAL with fixed 0.001 coordinate
scales and automatic offsets, and changed the merge exception handler to raise.
Two submodels yielded 40,634 and 36,836 points; the merged cloud had 77,470.
Every row was compared in input order for 21 listed dimensions (coordinates
within 0.0011, other tested values equal), and GDAL reported equivalent CRS.
The explicit merge-failure handler was not fault-injected in that run. Results
and exact constraints are in `odm-split-merge-experiment-evidence.json`.

This is one point-cloud experiment, not validated support for general inputs,
extra dimensions, other scales/coordinate ranges, distributed processing,
DEM/orthophoto/3D merging, geometric accuracy or release. The launcher continues
to reject split. Next create a bounded fail-closed research implementation and
exercise negative failures and wider LAS schemas/CRS before enabling it.

#### Packaged, restricted research implementation

Build 4 of the private dense research recipe now strips `--split-image-groups`
from submodel arguments, uses a narrow PDAL point-cloud merge, and propagates
merge errors. The merge checks that at least two distinct inputs use the tested
LAS 1.4 format 7 dimension set and 0.001 scales, have finite representable
bounds and equivalent CRS; it checks output count, bounds, schema and CRS before
atomically replacing an output. Other inputs are rejected, not silently coerced.
It does not promise preservation of arbitrary LAS header metadata.

[43637992510](https://github.com/Archont561/ODM-conda/actions/runs/43637992510)
built and retested the research packages, replayed 436 locked package identities
in a relocated prefix, and invoked the **installed app directly** (the launcher
still rejects split). There were no post-replay source or binary overlays. Two
submodels produced 45,166 and 40,723 points; all 85,889 merged rows were checked
for the 21 listed dimensions, coordinate tolerance 0.0011 and equivalent CRS.
A corrupt input on merge-stage rerun returned exit 1 and preserved the previous
merged output. A generated fixture rejected incompatible point format, extra
dimension, input scale, CRS and excessive coordinate span without changing an
existing output. See `odm-packaged-split-merge-evidence.json`.

These are point-cloud-only tests on one real and a small synthetic fixture; they
do not establish correctness for general LAS metadata, geometric accuracy,
3D/DEM/orthophoto merge or distributed processing. Split is not exposed through
the research launcher yet. Rights, production recipe and release gates remain.

#### LAS metadata and raster merge follow-up

[43641416170](https://github.com/Archont561/ODM-conda/actions/runs/43641416170)
found a real build-4 limitation: merging generated inputs with GPS-time global
encoding 17, a nonzero file-source ID, a project ID and a custom VLR silently
produced default header values and dropped the VLR. Build 4 must **not** be
considered metadata-preserving for such inputs.

Build 5 fails closed unless the header has the observed PDAL defaults (global
encoding 16, zero source ID, nil project ID, PDAL system/software ID) and VLR
identifiers are limited to the recognized WKT and compression records. CRS,
schema and coordinate guards still apply. Creation date, software version and
recognized VLR contents may be rewritten; arbitrary metadata preservation is
not claimed. [43641891994](https://github.com/Archont561/ODM-conda/actions/runs/43641891994)
independently verified rejection of changed GPS encoding, source/project/system/
software IDs, custom VLR and custom EVLR while retaining the old output. It
used the checked-out research module and freshly solved PDAL/GDAL, not an
installed build-5 package. `scripts/odm_las_metadata_fixture.py` reproduces this
fixture when run with a suitable research prefix Python.

[43641892010](https://github.com/Archont561/ODM-conda/actions/runs/43641892010)
built and retested build 5 and used a relocated 436-identity replay, without
source/binary overlay. Direct app invocation (launcher bypass) processed 35
images as two submodels with `--merge all --dsm`. The point-cloud merge preserved
81,834 rows for the 21 checked dimensions, and a corrupt-input rerun failed and
preserved its prior output. Two input DSMs and two feathered orthophotos existed;
merged orthophoto metadata/statistics and basic DSM metadata/statistics checks
passed. Existence alone does not prove both input rasters contributed: pixel,
footprint-union, seam and geographic accuracy tests remain. Details, package
identities and scope are in `odm-split-raster-metadata-evidence.json`.
The launcher still rejects split; distributed processing, DTM and 3D-model merge
remain unverified. Nothing was uploaded or approved for release.

#### Raster contribution and DTM sampling

[43645580804](https://github.com/Archont561/ODM-conda/actions/runs/43645580804)
used the packaged build-5 app directly after a relocated 436-identity replay
without overlays. A 35-image local two-submodel run requested `--merge all
--dsm --dtm --pc-classify` with an explicit external model. It produced two
input DTMs and a merged DTM, as well as DSM and orthophoto outputs. Since ODM
classifies the *merged* cloud after concatenation, classification values were
allowed to change; the other 20 listed point dimensions were checked row by
row and CRS was equivalent. This does not establish classification accuracy.

A bounded nearest-neighbor grid sampled the outputs and both input rasters.
For each product, each input had exclusive valid merged samples whose values
mostly matched that input within the stated thresholds. For example, orthophoto
had 63,109 / 3,706 exclusive samples, matching within 12 DN for 100% / 91.3%;
DTM had 63,202 / 3,709, matching within 0.1 units for 100% / 99.9%.
The overlap values also differed from the first input for some samples where
inputs differed. This is evidence of contributions at sampled locations, not
proof of full-resolution footprint union or a counterfactual blend test. The
reported overlap adjacent-pixel percentiles include actual image/terrain texture:
they are **not seam-specific quality measurements**. Full statistics, package
lock hash and limitations are in `odm-raster-contribution-evidence.json`.

A prior [43644044169](https://github.com/Archont561/ODM-conda/actions/runs/43644044169)
completed the ODM pipeline but its trial incorrectly demanded that
classification remain unchanged; the corrected check explicitly allows valid
reclassification. Another [43644839205](https://github.com/Archont561/ODM-conda/actions/runs/43644839205)
completed, but its annotation quota prevented retention of all reported metrics.
No trial uploaded packages, model, inputs or outputs. The launcher remains
restricted; 3D and distributed/ClusterODM merge remain untested. Do not infer
accuracy, model rights or production release approval from these runs.

#### Controlled raster counterfactual

[43647654147](https://github.com/Archont561/ODM-conda/actions/runs/43647654147)
replayed 436 package identities in a fresh relocated prefix without source or
binary overlays and directly exercised the installed ODM orthophoto and DEM
merge functions. Two synthetic, aligned 24×32 rasters (constant 100 and 200)
overlap over 16 columns; the combined 32×32 output had all 1,024 pixels covered.
Disabling either input changed 768 pixels in each product. Equal-weight DEM
values were 100 and 200 in exclusive areas and 150 throughout overlap. With
orthophoto alphas 255 and 128, overlap was 150 in one input order but 100 in the
reverse order (512 pixels changed). A synthetic half-alpha cutline changed 32
pixels from 150 to 195. The maximum horizontal adjacent step was 50 in both
outputs for this intentionally different pair of constant inputs.

This validates the specified controlled behavior, **not** real-world seam
quality: source order affects alpha blending, and a 50-unit step in this
contrived fixture cannot establish a general acceptable threshold. Inputs were
aligned, DEM weights were manually supplied, and real distance-map generation,
geometric accuracy, distributed processing and 3D-model merge were not tested.
Evidence and the exact lock/package hashes are in
`odm-raster-counterfactual-evidence.json`; the fixture is
`scripts/odm_raster_counterfactual_fixture.py`. Data and packages were discarded.
