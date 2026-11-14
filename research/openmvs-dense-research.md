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
