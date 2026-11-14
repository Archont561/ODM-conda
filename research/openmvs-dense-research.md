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
