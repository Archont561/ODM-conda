# OpenMVS and OpenSfM: preliminary license review

Review date: 2026-10-28. Scope: the **local-only** linux-64 research recipes
at PR #35, not upstream projects in general. This is engineering triage, not
legal advice, a complete dependency audit, owner approval, or permission to
redistribute. Both recipes remain `LicenseRef-Unreviewed` and outside the
production release machinery. Checksums, source plans and preliminary notice
inventories are in `source-graphs.json`, `openmvs-notices.json` and
`opensfm-notices.json`; path references below refer to those exact pinned trees.
The OpenSfM graph also includes vmem 1.0.2, pinned by URL and SHA256 in its
recipe. Source archives and generated research packages must not be published
based on this review.

## Decision

**Neither component is ready for distribution.** OpenMVS's restricted files in
the original archive, incomplete binary-specific notices and corresponding
source plan are blockers. OpenSfM has unresolved data rights and inconsistent
license evidence, including third-party headers in vmem. Both need a review of
the actual resolved dependency graph, notices and copyleft compliance; neither
successful native build establishes those matters. Do not change the license
field to a definitive SPDX expression yet.

## OpenMVS: reduced ReconstructMesh only

- Pinned OpenMVS `8e4c5f31a16e0e329132c8f26e20a8c5d7b47f53` has an AGPL v3
  root license and `COPYRIGHT.md` identifies OpenMVS as AGPL. The recipe
  modifies and compiles it, so a distribution review must address the AGPL
  source, notice and modification requirements. AGPL section 13 may also
  require an offer of corresponding source to remote users interacting with a
  modified version over a network; assess the actual deployment and operator.
- The staged VCG fork `3fe55c6fa48ca111dab31eaa594ecab33913a8f1` includes GPL
  v3 license text; individual headers such as `vcg/complex/complex.h` and
  `vcg/space/point3.h` say GPL version 2 or later. These are examples, not a
  license classification of every included VCG file. The pinned Eigen tree
  includes multiple license texts; the build defines `EIGEN_MPL2_ONLY`, but
  the actual included code and MPL notices/source obligations still need review.
- `libs/Math/IBFS/license.txt` permits **research use only** and requests a
  citation. `libs/Math/TRWS/LICENSE.TXT` permits only non-commercial use and
  distribution under its terms. Both are in the *original downloaded source
  archive*. The research patch excludes IBFS and TRWS compilation and several
  MVS translation units; a previous local reduced build had no observed IBFS or
  MRFEnergy symbols. This is evidence for that build, not proof about every
  generated binary, header, static link or corresponding-source obligation.
  In particular, do not publish the original archive or assume that including
  those files in a corresponding-source bundle is permissible. Determine an
  appropriately authorized, complete source distribution or obtain permissions;
  confirm that exclusions are legally and technically sufficient.
- `COPYRIGHT.md` lists Boost, BSD and MPL-licensed bundled materials. The
  recipe's binary is built using CGAL headers (`SceneReconstruct.cpp` and
  `libs/MVS/CMakeLists.txt`) as well as Boost and other packages. The current
  conda-forge CGAL feedstock describes its package as GPL3/LGPL3, not an
  individual-header determination. Review the *actual resolved CGAL version*,
  used headers and corresponding license notices; assess GMP, MPFR, OpenCV,
  TBB, compiler runtimes, and all other actual linked/static dependencies.
  A feedstock description is not a substitute for a build-specific SBOM.
- The updated research builder copies the OpenMVS copyright inventory, VCG
  license text, and Eigen MPL-2.0 and licensing README, in addition to packaging
  MIT and upstream LICENSE. It still does not demonstrate a complete set of
  VCG, Eigen, OpenMVS third-party and CGAL notices or corresponding source. The research
  audit checks payload and ELF RPATH, not license completeness. Do not treat
  its pass as satisfying those obligations.

## OpenSfM

- The pinned ODM fork `c5328439465e6ace011f39077d1077d7b1cdd65d` has an AGPL v3
  root LICENSE; its README says ODM fork changes are AGPLv3 while retaining an
  upstream statement that OpenSfM is BSD-style and the LICENSE file is BSD.
  Review file-level provenance and rights and resolve this inconsistent wording
  with the relevant maintainers; do not infer that all files are solely BSD or
  assign a final whole-package SPDX expression from the root text alone.
- Bundled AKAZE and pybind11 notices have BSD-3-Clause terms; VLFeat's COPYING
  has BSD-2-Clause terms. The research builder copies those notices. They do
  not replace the need to review other files and actual resolved Conda
  dependencies (including Ceres, SuiteSparse, OpenCV and Python packages).
  `licenses.csv` records old dependency versions and is not a current SBOM.
- The sensor-data readme attributes its first database to Gregor Brdnik and
  claims a simplified BSD license. Check the contributor's grant, subsequent
  data contributions and the exact notice/license needed. The two bundled
  bag-of-words NPZ vocabulary assets have pinned hashes and repository history,
  but their authorship, training dataset provenance and rights for redistribution
  remain unverified. A hash or passing asset test does not establish rights.
- vmem 1.0.2 metadata says GPLv3-or-later and its README says GPLv3; its LICENSE
  contains GPL v3 text. However, `vmem/posix.py` and `vmem/utils.py` carry
  Giampaolo Rodola' copyright notices referring to a BSD-style license in
  LICENSE, while the sdist's LICENSE is GPL text. Trace those files and their
  original applicable BSD notice and obtain clarification as needed. The updated research builder carries the GPL text and a conservatively
  included historical psutil BSD-3-Clause notice. The exact provenance, other
  applicable notices and GPL/BSD interaction remain unresolved. OpenSfM imports vmem, so do not treat its terms as irrelevant.
  Evaluate the applicable GPL version/permissions and AGPL combination for the
  actual distribution with qualified review.

## Evidence and remaining release work

- [OpenSfM research run 40757042542](https://github.com/Archont561/ODM-conda/actions/runs/40757042542)
  passed build, fresh retest and limited leak/RPATH audit at `6f92c55`.
- [OpenMVS research run 40759635611](https://github.com/Archont561/ODM-conda/actions/runs/40759635611)
  passed the same checks at `a656bdb`. Both workflows delete temporary outputs
  and upload no artifacts. Neither audit is a license or release approval.
- Before any proposed release, inventory actual source and binary inputs and
  dependency versions, trace static/header inclusion and dynamic dependencies,
  supply all required notices and complete corresponding source and build
  instructions using sources whose redistribution is authorized, resolve the
  identified asset and grant questions, review network-service obligations,
  and have the owner and qualified legal reviewer approve the precise scope.
  A fresh review is needed if pins, recipe, bundled files or dependencies change.

### vmem provenance follow-up (2026-10-28)

The exact pinned vmem sdist SHA256 remains
`95fe9ba737edea8e5737fb9ddda7031d7ca62fd53f53c1c4e95195f3c7d801fd`.
The upstream vmem README describes it as a replacement for psutil's
`virtual_memory`. The sdist `vmem/utils.py` function `usage_percent` has the
same Python AST as the function of that name in psutil `_common.py` at
[psutil commit 93e1c468ab4ac7922472114b3aeeacda2c8676a1](https://github.com/giampaolo/psutil/tree/93e1c468ab4ac7922472114b3aeeacda2c8676a1)
(the latest commit returned by the GitHub API before vmem's 2021-04-14 first
source commit). The two vmem files retain a 2009 Giampaolo Rodola' BSD-style
header. At that psutil commit, [LICENSE](https://github.com/giampaolo/psutil/blob/93e1c468ab4ac7922472114b3aeeacda2c8676a1/LICENSE)
is BSD-3-Clause text, SHA256
`24c12984500caa07ffdce19eebc06396c5e6d244b573bc6c438f4a6ef8e56c1b`.
The AST comparison supports provenance investigation; it does **not** prove
that this is the exact source revision or the only applicable third-party
notice, nor does it settle the GPL/BSD treatment of the combined package. A
reviewer should trace both files and retain all applicable original notices;
the updated research recipe carries this exact psutil license alongside the
vmem GPL text as a conservative notice, not as proof of provenance. No
redistribution approval is inferred.

### Additional reduced-link evidence

The local-only OpenMVS builder now requests a GNU linker map for the actual
`ReconstructMesh` executable and fails if the map is missing or unrecognizable,
if expected MVS/Math and reconstruction inputs are absent, or if it names IBFS,
TRWS, MRFEnergy, or excluded dense/refine/texture objects. The map stays in the
temporary build tree; a SHA256 is printed after a successful check. Tests cover
negative cases and a real small GNU C++ link map. Owner-dispatched [run 40762858939](https://github.com/Archont561/ODM-conda/actions/runs/40762858939)
at commit `4dba9fe141c22c4791f44a2ce330ef00bb6b5811` passed the native
build with this guard, installed tests, fresh retest and limited audit; its
temporary outputs were removed. Matching named link inputs cannot rule out equivalent code, prove a
complete dependency inventory, or authorize distribution of the original source
archive. TASK-54 and the release restrictions remain open.

### Notice reconciliation in research build 1

Both research recipes now use build number 1 because their payloads change.
OpenMVS adds its COPYRIGHT.md, the exact pinned VCG LICENSE.txt, and Eigen's
COPYING.MPL2 and COPYING.README. OpenSfM adds the historical psutil BSD-3-Clause
notice at commit `93e1c468ab4ac7922472114b3aeeacda2c8676a1`, conservatively
included based on the noted vmem file headers and function similarity.
The builder checks the individual SHA256 values before copying; the limited
research audit rejects a missing or modified added notice. See
`research/notices/psutil-2021-BSD-3-Clause.txt` and
`scripts/research_license_notices.py`. These additions neither assert that
all notices are complete nor replace rights/provenance review. Owner-dispatched local-only build 1 runs [40779149681](https://github.com/Archont561/ODM-conda/actions/runs/40779149681)
(OpenMVS) and [40779183804](https://github.com/Archont561/ODM-conda/actions/runs/40779183804)
(OpenSfM) passed native builds, fresh retests and limited research audits at
commit `147b0584b42977b1f52e6cc65aeeb56ce1a99fc7`. Temporary packages and
sources were removed; no artifacts were uploaded. These tests do not resolve
the remaining licensing and redistribution questions.


### Local photogrammetry batch follow-up (2026-10-29)

OpenSfM, pybind11, vmem, OpenMVS, VCG and Eigen pinned archives were fetched
and hash-verified locally. Exact staged research trees passed their respective
fingerprints after the recipe patches, and OpenSfM's four runtime asset hashes
matched. This is byte identity only; it establishes neither rights nor complete
corresponding source. OpenSfM remains `LicenseRef-Unreviewed` with asset and
vmem rights unresolved; OpenMVS archives still include restricted IBFS/TRWS.

The unregistered production OpenMVS builder omitted `openmvs_fixture.py`,
which the installed synthetic fixture imports. It now copies the helper, with a
regression test; this is not production recipe integration or native production
validation. Research audit now checks exact name, version, build, linux-64 and
a small critical set of declared runtime dependencies for both research
packages. Dependency names are not version/ABI or full dependency verification.
The existing research workflow offers `all`, running both local-only builds and
retests sequentially with separate temporary directories and no artifacts.
Owner dispatch is needed to verify the strengthened audit against real packages.
No release gates were changed.

Owner-dispatched [run 40848319389](https://github.com/Archont561/ODM-conda/actions/runs/40848319389)
selected `all` at commit `7f0e5c575c620916596b5c08e16f5ee530527b4d` and
passed both sequential local-only package builds, installed tests, fresh retests
and strengthened research audits. Temporary outputs were discarded. This does
not establish production readiness, full dependency or ABI review, rights,
complete notices, corresponding-source compliance or release approval.

### OpenMVS restricted-source alternatives (2026-10-29)

The pinned OpenMVS archive was re-fetched and verified at SHA256 `949d420d4506ccd0189574252c8214acce666de837e400e44682e8ddc13e666b`. In its `SceneReconstruct.cpp`, the default defines `DELAUNAY_MAXFLOW_IBFS`; the existing research patch disables that macro, selecting the existing Boost Graph Boykov-Kolmogorov alternative instead. The same patch removes IBFS/TRWS globbed files from the Math target and excludes `SceneDensify.cpp`, `SceneTexture.cpp` and `SceneRefine.cpp` from the reduced MVS target. The source tree still contains IBFS and TRWS, and omitted scene files reference TRWS; the previously passing named-link guard only addresses specified binary inputs. The replacement also introduces Boost headers whose actual version, license, corresponding source and other obligations require review.

One possible route is to obtain affirmative rights-holder permission for distribution of the exact original archives and terms. Another is to investigate a separately generated, precisely defined reduced source tree excluding restricted files and unused references, retaining all required notices, patches, build scripts and dependencies. The latter is **not** an implemented or approved source bundle: stripping the original archive may itself require rights analysis, and a reproducible tree and full corresponding-source sufficiency would need qualified review and a fresh native rebuild. Upstream [commit 58117204](https://github.com/OpenDroneMap/openMVS/commit/58117204c86bbb11a0b25b26a8987676cf11274d) removed many TRWS files but modified IBFS; it is not the pinned fork and is not evidence of an unrestricted replacement or ODM compatibility. Neither route is permission to distribute the original source or research binary. TASK-54 remains open.

### Disposable reduced-tree build experiment (2026-10-29)

A hash-verified copy of the pinned OpenMVS archive was examined locally. Its
`libs/Math/IBFS` and `libs/Math/TRWS` directories contain 20 regular files in
total. For [local-only run 40965276525](https://github.com/Archont561/ODM-conda/actions/runs/40965276525),
the temporary workflow at commit `0e3db8858eeb588702c7c0a62a68e24b0edcccf2`
first used the existing exact patched-tree graph check, then deleted those two
directories and the excluded `SceneDensify.cpp`, `SceneRefine.cpp` and
`SceneTexture.cpp` from the **disposable staged tree before CMake**. The normal
reduced-target builder then compiled `ReconstructMesh`, checked its GNU link
map for named restricted and excluded inputs, ran installed and fresh retests,
and passed the limited package audit. No source, archive or package was uploaded.
The retained 3,274-file tree fingerprint was
`e64c1718c05d58ac74051a8a0a216febbcac7144898cea022d378af427549489`,
computed by the existing path/content fingerprint after ignoring rattler's
verified generated root files; it includes the staged VCG and Eigen trees,
does not include modes or directory entries, and is **not an archive hash**.

This demonstrates feasibility of this specific reduced build, not that it is
an acceptable corresponding-source distribution: original archives were
fetched before pruning, no independently reproducible distribution archive or
manifest was produced, and no rights-holder permission or legal decision was
obtained. The patch and remaining source can still contain references to the
excluded implementations; deleting named paths does not prove no restricted
code exists elsewhere. CMake configuration, synthetic fixtures and a named-input
link-map check do not establish complete behavior, downstream compatibility,
license provenance, complete notices or independent source sufficiency. The
experiment excludes densification, texturing and refinement and is not the full
OpenMVS product. A future candidate must define and independently verify a
reproducible source transformation and complete build/source/notice inventory,
review the Boost/CGAL/VCG/Eigen and other inputs, obtain qualified review of
modification and distribution rights, and repeat native and integration tests.
The original archive and research package remain **not authorized for
redistribution**, and all TASK-54 criteria and release gates remain open.

### Reproducible local-only reduced tree (2026-10-29)

`scripts/openmvs_reduced_tree.py` prepares a **local-research-only** copy from
the exact staged graph with all four research patches applied. It verifies the
existing OpenMVS/VCG/Eigen graph fingerprint before copying; excludes the named
IBFS and TRWS directories and the three excluded scene implementations; requires
existing root, VCG and Eigen notices; and checks the retained 3,274-file
path/content fingerprint from the preceding experiment. It refuses an existing
or overlapping destination and symlinks, leaves its input unchanged, and emits
a sorted JSON manifest of retained paths, SHA256s and file modes. File modes
are recorded in the manifest but are **not** part of the existing tree
fingerprint. The manifest does not assert the legal provenance or completeness
of any file. It produces neither a distribution archive nor approval to share
its output. Given an already staged exact research tree, the local-only tool is:

```sh
pixi run python scripts/openmvs_reduced_tree.py \
  --source /path/to/verified-patched-research-tree \
  --destination /path/to/new-local-only-tree > /path/to/local-manifest.json
```

[Disposable run 40967069992](https://github.com/Archont561/ODM-conda/actions/runs/40967069992)
created two separate copies from the same verified staged input; their manifests
were identical. The shared path/content fingerprint was
`e64c1718c05d58ac74051a8a0a216febbcac7144898cea022d378af427549489`,
and SHA256 of the canonical JSON manifest (sorted keys, compact separators)
was `560cc78034924dd9fd83b02c4fba448a66612fc493b86ae8c09da6f0b338ce3b`.
The experiment switched the research build's CMake source to the first reduced
copy, then built ReconstructMesh, passed the named-input link-map guard,
installed tests, a fresh retest and limited package audit. The temporary CI
workflow and all copies, packages and fetched archives were discarded; the
exact temporary builder adaptation is available in the run's commit
`f576151137d4f0b2398c25a6dda09dc385a3d564`. Unit tests exercise deterministic
copying and reject invalid input, symlinks, overlapping/existing destinations
and unexpected reduced fingerprints.

Two copies in one run demonstrate deterministic transformation of that input,
not a guarantee across filesystems or future toolchains. The original full
archive is still required to prepare the staged input and is not approved for
distribution. The limited notice checks cover only known root/VCG/Eigen notices,
not all retained files or transitive dependencies; named path removal does not
rule out copied restricted code elsewhere. A distributable corresponding-source
plan, full notices/provenance, permissions and qualified review remain open.
No recipe, component gate or publication status is changed.
