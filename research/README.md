# Experimental source staging

`source-graphs.json` is preliminary research for the six selected components,
not a completeness attestation or release authorization. Experimental local-only
OpenMVS and OpenSfM recipes are separately located under `research/recipes/`;
they are not registered production components and have not passed native builds. The plans
record immutable archives observed during research; mutable ODM references were
resolved at the time recorded in their Backlog tasks. They must be reviewed
again when selecting final release sources.

To reproduce an isolated staging smoke test (requires network access to GitHub
or a pre-populated hash-checked cache):

```sh
python scripts/stage_sources.py --component opensfm --output /tmp/opensfm-source
```

Supported experimental plan names are `dem2mesh`, `poissonrecon`, `renderdem`,
`opensfm`, `openmvs`, and `mvs-texturing`. The output directory must not exist.
Each source archive is rehashed, and extraction rejects links, unsafe paths and
nonempty staging destinations. Declared `.gitmodules` paths must be explicitly
staged; gitlink commits must still be verified separately against the Git tree,
because a source archive cannot establish them. With a local Git repository
containing the pinned primary commit, run:

```sh
python scripts/verify_gitlinks.py --component opensfm --repository /path/to/opensfm-git
```

The verifier compares all primary-tree gitlink paths and revisions with entries
marked `gitlink: true` in the plan, rejecting missing, unexpected or changed
links. It does not verify nested repository gitlinks or equivalence of the
archive with the Git tree, nor does it prove source or license completeness. The plans contain only sources
identified so far. The plan and this file are included in packaging source bundles
alongside the staging scripts; their presence does not authorize release. In particular, the staged mvs-texturing tree still contains upstream
ExternalProject download commands, and its MVE source is in a non-default path.
The Eigen archives use a GitHub mirror and are not the original GitLab
archive bytes. The texturing plan pins the exact GitLab 3.3.2 tag commit
`477d1e81928a8514d2cca6a6e1e7e478eecd8634`, which is also available on the
GitHub mirror. Its earlier GitHub tag resolves to a different commit with an
extra `.hgtags` file; the earlier local texrecon build used that older plan.
For the openMVS Eigen pin, both hosts identify the same Git commit. Original
GitLab tarball bytes, full notices and network-isolated builds remain unverified.
The source bundler recognizes the exact pinned OpenMVS and mvs-texturing
graphs. The builder has fingerprint-gated branches for both; the texturing
recipe is registered for testing, while OpenMVS recipe integration remains
unfinished. Lint rejects unrecognized external graphs, and release gates for
the provisional texturing recipe remain closed. Graph recognition is not legal
approval.

For a **research-only** archive containing the plan, all planned upstream
archives and packaging sources including the experimental patch:

```sh
python scripts/bundle_staged_sources.py --component mvs-texturing --output /tmp/texturing-research.tar.gz
```

The helper verifies hashes and stages the graph before writing a deterministic
archive and manifest. It refuses to overwrite a destination. This archive is
not a release source bundle or a source-completeness certification.

`mvs-texturing-notices.json` records hashes of 20 preliminary notice-bearing
files; `mvs-texturing-license-review.md` describes the separate MVE easyexif
notice, non-free disclaimer and outstanding review decisions. `openmvs-notices.json` records the local reduced-target dependency-trace
files plus root and third-party notices, including the excluded IBFS/TRWS
licenses; apply both OpenMVS research patches before verifying it.
`opensfm-notices.json` records root and third-party notices and selected
camera-database and vocabulary asset hashes. The OpenSfM README contains
conflicting BSD/AGPL descriptions; vocabulary provenance remains unreviewed.
The 10,000-word vocabulary was added as `bow_hahog_root_uchar.npz` in
OpenSfM commit `c686ad2e8c62664c63115968d86c605c83f8b04a` and renamed in
`d8cabec9e8a510d0c1c3a5be97dd8f6657ef09f9`; that latter commit also added the
64-word vocabulary. The pinned setup.py includes both. These Git history facts
do not identify the training data or establish asset rights.
All inventories are evidence, not legal approval or complete obligations.

To verify the texturing inventory against the matching staged tree, run:

```sh
python scripts/verify_staged_notices.py --tree /tmp/texturing-source
```

This checks the listed bytes only; it does not establish a complete inventory
or decide license obligations.

`patches/mvs-texturing-offline.patch` is a configure-only experiment against
the pinned mvs-texturing archive. It replaces active ExternalProject targets
with checks for staged sources and removes `-march=native`. Configuration was
initially smoke-tested with temporary dependency stubs. A subsequent local
research build linked `texrecon` against locally built MVE libraries and the
restored TBB runtime, using matching-version upstream TBB headers. This was not
a network-isolated or installed-package validation. A real TBB development
package, complete source and license review, native CI build and installed-prefix
functional test remain required.

`patches/mve-baseline-cpu.patch` is a research patch against the pinned MVE
archive that removes its unconditional GNU `-mpopcnt` option. Together with
the texturing offline patch, a local GCC 12 build using `-march=x86-64
-mno-popcnt` produced `texrecon` and passed the generated-scene fixture. The
70 MVE object files and the resulting executable contained no POPCNT
instructions in an `objdump` inspection; 25 texturing compile commands also
used the requested baseline flags. This covers only the inspected build output,
not its dynamically linked libraries, other compiler instructions, an isolated
Conda build or a package audit. Both patches remain research-only.

A generated-scene **research-only** texrecon fixture is available after building
an executable from the pinned sources:

```sh
python scripts/texrecon_fixture.py --executable /absolute/path/to/texrecon
```

It checks the output geometry, texture references and PNG structure. The fixture
skips both seam-leveling stages and inherits the caller's runtime library path.
A successful run against a research binary is not package validation.

For an OpenSfM tree with its eight native bindings already built, a preliminary
import and geometry smoke test can be run with:

```sh
python scripts/opensfm_fixture.py /absolute/path/to/opensfm-source-root
```

It imports the bindings from that exact tree, checks an equatorial ECEF
conversion and an identity pose. To check the four runtime assets listed in the
pinned upstream setup script, independently run:

```sh
python scripts/opensfm_assets_fixture.py /absolute/path/to/opensfm-source-root
# Alternatively pass the installed site-packages directory containing opensfm/.
```

The asset checker verifies the exact bytes of the two vocabulary files, sensor
JSON and camera calibration YAML, and rejects symlinked or missing files. It
does not establish asset provenance or permission to distribute them. Neither
check is a dataset, source-completeness or release test.

`patches/opensfm-ceres-config.patch` is a research patch that selects the Ceres
CMake package and propagates its target requirements to native-module consumers.
It applies to the pinned OpenSfM source and was tested in a mixed local
GCC/Pixi environment against Ceres 2.2 and Python 3.12; it is not part of a
production recipe and has not been validated with an isolated package build.

For a locally built OpenMVS `ReconstructMesh`, the following **research-only**
fixture generates and decimates a cube, then checks the resulting PLY geometry:

```sh
python scripts/openmvs_fixture.py --executable /absolute/path/to/ReconstructMesh
```

The fixture exercises mesh import and cleaning, not point-cloud reconstruction,
relocation or an installed package. It inherits the caller's library paths and
does not establish a baseline CPU, ABI, source-completeness or license review.

To test **point-cloud reconstruction** with a local research OpenMVS build,
use the exact upstream test data from the pinned OpenMVS source tree:

```sh
python scripts/openmvs_pointcloud_fixture.py --executable /path/to/ReconstructMesh \
  --dataset /path/to/openmvs/apps/Tests/data
```

The fixture verifies the scene and four image hashes, copies them into a
fresh temporary directory, reconstructs the scene's sparse point cloud and
checks the resulting binary PLY geometry. It uses `--archive-type 1` to avoid
OpenMVS's automatic attempt to load a separate same-name PLY. The upstream test
data is not included in this repository; its licensing and redistribution
status remain unreviewed. This is not an installed-prefix test, a test of a
separate dense PLY input, or an isolated Conda build.

`patches/openmvs-visibility-check.patch` is an **experimental** safety patch for
the pinned OpenMVS source. A plain separate PLY without camera visibility, and
a PLY whose `views` field contains scalar counts rather than camera indices,
caused the unpatched research build to segfault. The patch avoids treating
scalar counts as camera IDs and rejects reconstruction without valid per-point
camera visibility. With the patched research executable, use the fixture above
with `--check-visibility-rejection` to run both negative cases as well as the
positive scene test. It does not make arbitrary PLY point clouds reconstructible,
establish general malformed-input safety, or replace an installed-package test.

A fully generated scene avoids redistributing the unreviewed upstream test
images. With the experimental visibility patch applied, run:

```sh
python scripts/openmvs_synthetic_fixture.py --executable /absolute/path/to/ReconstructMesh
```

It generates two images, calibrated camera poses, and 400 visible points in an
OpenMVS v3 interface scene; it validates a reconstructed mesh and checks clean
rejection of separate PLY clouds lacking camera IDs, both with and without
scalar view counts. On the local patched research build it produced 53 vertices
and 46 faces. This is not an installed-prefix test or evidence that a separate
PLY with camera IDs is supported.

`patches/openmvs-reconstruct-only.patch` is an experimental **ReconstructMesh
only** build variant. The original OpenMVS build compiled and linked IBFS,
whose bundled license says research use only; its dense source also uses TRWS,
whose bundled license limits distribution to non-commercial purposes. The
patch selects the upstream Boost max-flow branch and excludes the dense,
texture and refine translation units and the IBFS/TRWS Math build and install
entries. It does not provide those excluded OpenMVS tools.

A local GCC 12 reduced-target build with this patch and the visibility patch
passed the generated-scene, upstream-scene and cube fixtures. Its unstripped
ReconstructMesh executable had no `IBFS::` or `MRFEnergy` symbols according to
`nm -C`; the inspected Math archive lacked IBFS objects and the MVS archive
lacked the excluded dense/texture/refine objects (the CUDA-disabled
`SceneRefineCUDA.cpp.o` remained). This is not an exhaustive binary or legal
analysis. The original upstream archive **still contains** IBFS and TRWS files;
its redistribution and corresponding-source obligations require separate review
(TASK-54), even if the binary excludes their code. No package is approved.

### Research source-graph checks (not recipes)

`opensfm_graph_policy.py` checks the pinned primary and pybind11 source graph,
research Ceres patch, and exact patched tree. It can also scan both downloaded
archives when `--primary-archive` and `--pybind-archive` are supplied together:

```sh
python scripts/opensfm_graph_policy.py --tree /path/to/patched/opensfm \
  --primary-archive /path/to/opensfm.tar.gz --pybind-archive /path/to/pybind11.tar.gz
```

The scan permits the exact root `.gitmodules` file and two exact pybind11 files
containing fetch operations (`tests/CMakeLists.txt` and `tools/FindCatch.cmake`)
only after the complete archives match their pinned hashes. This is an inventory
exception, not evidence that tests or downloads are disabled. The production
source bundler does not enable the `.gitmodules` exception for OpenSfM. Gitlink
revision verification is separate; an archive fingerprint cannot prove it.

The OpenMVS and OpenSfM graph checkers recognize rattler-build 0.68's generated
work-root files only with exact expected source metadata. Their expected patch
filenames match the experimental research recipes; neither recipe is registered
as a production component or has passed an isolated native build. Neither check
grants source redistribution or license approval.

The pybind11 subproject can be configured separately with tests explicitly off:

```sh
cmake -S research/pybind11-tests-disabled -B /tmp/pybind-test-off -G Ninja \
  -DPYBIND11_SOURCE=/absolute/path/to/opensfm/opensfm/src/third_party/pybind11
cmake --build /tmp/pybind-test-off
```

First verify the full source graph and archives as described above. This
standalone harness forces `PYBIND11_TEST` and `BUILD_TESTING` off and
`FETCHCONTENT_FULLY_DISCONNECTED` on. It was configured with the pinned pybind11
2.13.6 source and local CMake 3.31/GCC 12; the test subdirectory was not
configured. It is not the full OpenSfM configuration, and it neither disables
other possible fetches nor establishes kernel network isolation.

### Local-only OpenMVS and OpenSfM recipes

`research/recipes/openmvs-odm` builds the **reduced ReconstructMesh target only**;
`research/recipes/opensfm-odm` builds the eight native bindings and installs the
Python package, CLI and data assets, plus ODM's pinned `vmem` 1.0.2 dependency.
The vmem sdist contains GPLv3 text and a GPLv3-or-later classifier; its exact
license grant and compatibility remain unreviewed. Both recipes are experimental and their declared
`LicenseRef-Unreviewed` is a warning, not a license conclusion. Do **not**
distribute their packages, cached archives or copied data. They are deliberately
absent from the production component list and build/release workflows.

With a locked Pixi environment and Conda/source network access, run a complete
local research build, fresh retest and limited leak/RPATH audit with:

```sh
RESEARCH_COMPONENT=openmvs pixi run python scripts/run_open_research.py
RESEARCH_COMPONENT=opensfm pixi run python scripts/run_open_research.py
```

Each run uses a temporary directory and removes its research packages and
source archive copies afterwards; rattler or Conda may keep their own local
caches. The owner can dispatch **Local-only Open component research build**
once the workflow file is present on the default branch; GitHub does not expose
new dispatch workflows from an unmerged branch. That workflow uploads neither
packages nor source archives. The research audit
is separate from, and does not replace, the production release audit. Passing
builds will not resolve licensing, asset provenance, offline/network isolation,
relocation beyond checked ELF RPATHs, or a full OpenSfM dataset run. No native
Conda build of these recipes has yet passed.
