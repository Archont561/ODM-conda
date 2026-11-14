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
**cannot yet be substituted into the ODM stack**. The successful standalone
test omits the flag; it does not fix ODM or prove ODM dense processing works.
A future candidate must deliberately resolve the CLI contract and test the
actual ODM invocation and a real dense end-to-end dataset; do not silently
ignore options or claim GPU support. Full release source, licensing, model,
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
