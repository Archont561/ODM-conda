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

### Retained-tree and native dependency review (2026-10-29)

The earlier `research/openmvs-notices.json` is a historical trace inventory,
not a complete license inventory. Reconstructed pinned OpenMVS/VCG/Eigen
archives with all four research patches and compared its 499 path/hash entries
with a newly reduced tree: **495 match**, two restricted license files are
absent with their excluded IBFS/TRWS directories, and two retained files differ
because the later `0004-ply-view-indices.patch` changed them. Their current
SHA256s are `d07e58ada4e7ae2d295adb49dd0140bd517b41be414823e7c3b5a5d9b82e5a41`
for `apps/ReconstructMesh/ReconstructMesh.cpp` and
`99f02ac60fc613567ea0854471eb8bc0b9e0614d5002a8505c20f30c8a041f83`
for `libs/MVS/PointCloud.cpp`. The OpenMVS root, VCG and Eigen root/MPL2 and
COPYING.README entries match. The older inventory reflects an earlier patch
state; do not use it as an exact-byte manifest for this reduced tree. This
comparison neither identifies every applicable notice nor proves the origins of
retained code. Local manifest bytes depend on recorded file modes; the
path/content fingerprint is the comparable value.

A separate [disposable native review run 40969462242](https://github.com/Archont561/ODM-conda/actions/runs/40969462242)
at `3058c62005a6e8a053c6f0d1e52327400c31090a` built the verified reduced copy,
passed its fresh retest and limited package audit, and examined its actual host
prefix metadata and Ninja dependency database. Selected host records were:

| Package | Version/build | SHA256 | Metadata license |
| --- | --- | --- | --- |
| cgal-cpp | 6.2.1 `hec4b13c_0` | `232ea63938c3582460c5767e118fc205963bc0d8c331885b2020ef1c5d0c83a5` | GPL3/LGPL3 |
| libboost | 1.90.0 `h1101c1b_3` | `868cae2463765495b59ebc1146bd4089f2983439a1ac469eec36b09575b47162` | BSL-1.0 |
| libboost-devel | 1.90.0 `hdab9b82_3` | `0d9008828401ba26fd0f0c0e81cc1a617ecaacd00855cc5273b97acf2e4e9cb7` | BSL-1.0 |
| eigen | 5.0.1 `h19c2612_3` | `e134dba3ad3523573d5902ff1222a4033372089ea31efa99e6adaf0aa18f904a` | MPL-2.0 |
| eigen-abi | 5.0.1.80 `hf414acd_3` | `2c0ae975516a66f50a525666dd128dd82e27aec6370d1a846b1390f3fbc03a98` | MPL-2.0 |
| gmp | 6.3.0 `hfd2156b_3` | `f36c336efc874f346a53a9011f67e997f9faac505562cc18c13b6d399cfe61c7` | GPL-2.0-or-later OR LGPL-3.0-or-later |
| mpfr | 4.2.2 `ha2cb11d_1` | `0be79ef2ee536e0c5d3ddb4a52bbae9f26d08560623299f33db2f4c4a17c525a` | LGPL-3.0-only |

These are host records, not a full runtime or corresponding-source inventory;
in particular the existence of host Eigen does not establish whether it or the
pinned Eigen headers were selected. Ninja's recorded dependency paths included
806 distinct `CGAL/` and 2,112 distinct `boost/` host headers, including
`CGAL/AABB_tree.h` and `CGAL/AABB_traits_3.h`. This trace is not proof of
specific compiled code, all required files, or a complete license expression.
As a reviewer lead, the corresponding CGAL upstream [6.2.1 AABB_tree.h](https://github.com/CGAL/cgal/blob/v6.2.1/AABB_tree/include/CGAL/AABB_tree.h)
and [AABB_traits_3.h](https://github.com/CGAL/cgal/blob/v6.2.1/AABB_tree/include/CGAL/AABB_traits_3.h)
identify `GPL-3.0-or-later OR LicenseRef-Commercial`; exact byte correspondence
to the installed package headers was not independently checked. File-level
CGAL terms and any commercial grant, Boost exceptions or other per-file terms,
VCG/Eigen notices and modified source, transitive native dependencies and the
actual corresponding-source boundary require qualified review. Metadata labels
are not a substitute for that review. No package or original archive was
uploaded; no legal or release gate was changed.

### OpenSfM asset and vmem provenance leads (2026-10-29)

The 10,000-word vocabulary was introduced as `bow_hahog_root_uchar.npz` in
[c686ad2](https://github.com/mapillary/OpenSfM/commit/c686ad2e8c62664c63115968d86c605c83f8b04a)
([PR 429](https://github.com/mapillary/OpenSfM/pull/429)) and renamed in
[d8cabec](https://github.com/mapillary/OpenSfM/commit/d8cabec9e8a510d0c1c3a5be97dd8f6657ef09f9).
That rename commit also adds the 64-word vocabulary; [PR 466](https://github.com/mapillary/OpenSfM/pull/466)
describes it as trained. History does not identify the training data or prove
rights to distribute either model. The sensor database README credits Gregor
Brdnik and calls its database simplified BSD; contributions and detailed data,
the bundled SQLite database, and fork-specific terms still need investigation.

For the exact hash-verified vmem 1.0.2 sdist, `posix.py` and `utils.py` match
byte-for-byte the files in vmem commit [ce5e7bf](https://github.com/pierotofy/vmem/commit/ce5e7bf4901c6c51786fd92b9be12ddec835032b):
SHA256 `174a7c475334f6dd525ba21dd982d720710c0321e2255e047a7571f5b9d94bb6`
and `17135d5f5b53e5525d2fff6be1369a19af2219b3ceb8cce68045c60ba74f0594`,
respectively. The first implementation [ab0f32e](https://github.com/pierotofy/vmem/commit/ab0f32e524db5803e3e6d29015572c241c5378c7)
had no copyright headers; [169d714](https://github.com/pierotofy/vmem/commit/169d714e56eda9460058ae6814356ac9735b9140)
and ce5e7bf later added Rodola BSD-style headers to `posix.py` and `utils.py`.
The original `utils.py` `usage_percent` AST matches psutil `_common.py` at
[93e1c46](https://github.com/giampaolo/psutil/commit/93e1c468ab4ac7922472114b3aeeacda2c8676a1);
original `posix.py` functions are similar to psutil `_pslinux.py` with
procfs/page-size changes and removed fields or warnings, but are not AST
identical. Similarity is a provenance lead, not proof of copying or a legal
conclusion. vmem's GPL metadata/README and psutil's BSD notice remain
conservatively included; exact applicability and license compatibility remain
for qualified review. No OpenSfM gate is changed.

A follow-up [run 40970246461](https://github.com/Archont561/ODM-conda/actions/runs/40970246461)
at `3bca88e` repeated the build, retest and audit and counted file markers in
the first 10,000 bytes of the traced host headers. Of the 806 CGAL paths, 93
identified `GPL-3.0-or-later OR LicenseRef-Commercial`, 683
`LGPL-3.0-or-later OR LicenseRef-Commercial`, 29 `LGPL-3.0-or-later`, and one
`BSL-1.0`. Of 2,112 Boost paths, 1,840 referenced the Boost Software License;
272 had neither an SPDX marker nor that phrase in the scanned prefix. This is
an automated marker count, not a file-by-file license analysis or evidence of
license grant selection. The traced Eigen dependencies were 251 paths under
the retained vendored Eigen tree and zero under the host prefix in this run;
this does not cover unrecorded tools or a different solve/build.

Installed `CGAL/AABB_tree.h` and `CGAL/AABB_traits_3.h` SHA256s were
`55d57cfd3ab1ea62373150eb28410e05560a9614ea915598b7afabe6622a9904` and
`c16821483935696c2c6d9a7b1173d025183c599975b8f06a2500884b33fd30bc`.
Their upstream tag counterparts hash to
`10d72986ffe39d5afdf74918e8f59312a41d2aecc0fdebca15f0757632aa292c` and
`430d8fbd6e08982b1fe93b15a18122725e98dfb4ae065c6303618572d0d9a863`;
they are not byte-identical, and the differences were not inspected. Review
the exact installed header contents and package source rather than assuming the
upstream tag alone represents them. The legal and corresponding-source
questions above remain unresolved.

### Sensor database composition investigation

The pinned `sensor_data.sqlite` SHA256 is
`45e7b0ed2d9978ae236ae522497514ded59ffd83f76bc0180555a36b2562fa31`.
ODM fork commit [cca015d](https://github.com/OpenDroneMap/OpenSfM/commit/cca015d1b11c276d1ff61526b0d460f6544c7c7b)
added it on 2022-12-13 and made `opensfm/sensors.py` prefer SQLite over JSON,
falling back to JSON on absence or query failure. It has 7,523 `id,focal`
rows. The pinned `sensor_data.json` has 3,708 entries; after lowercasing JSON
keys, every one appears in SQLite with an exactly equal numeric value and there
are 3,815 additional SQLite keys (no lowercase collisions). The 3,610-entry
`sensor_data_detailed.json` is separate; this comparison is not a complete
row-by-row provenance assessment.

A historical [AliceVision cameraSensors.db](https://github.com/alicevision/AliceVision/blob/b36931179c2299801ace912ac98561daa3f18456/src/aliceVision/sensorDB/cameraSensors.db)
was last changed before the SQLite import in commit
[b369311](https://github.com/alicevision/AliceVision/commit/b36931179c2299801ace912ac98561daa3f18456);
its SHA256 is `86969c1eed031294065f65d94a49d83560f78c7524f18a04eee24dbce3fc316e`.
Parsing its semicolon-separated make/model/focal entries, lowercasing, using
model alone when it starts with make and otherwise joining make and model, and
retaining the first valid occurrence yields 7,445 distinct keys. Of the 3,815
SQLite-only keys, **3,814 match** this historical database exactly in both key
and numeric value; the sole unmatched key is `hasselblad l2d-20c`. The
AliceVision file itself includes source fields naming multiple websites and
user contributions. The observed match is strong evidence of shared data,
not proof of direct copying or authority to sublicense those sources.

The later 2025 [DroneDB merge script](https://github.com/DroneDB/DroneDB/blob/8871193e0042b1821c964a1110c6561e950f1cdc/data/create_sensor_data.py)
combines OpenSfM JSON, AliceVision database and a DroneDB additions file using
the same broad normalization and first-source precedence, but its public commit
postdates the 2022 SQLite import and cannot establish the historical generation
procedure. The source rights and exact originating version must be reviewed
independently; the old OpenSfM sensor README's simplified-BSD statement cannot
by itself clear the additional SQLite content. Earlier source history traces the
initial JSON/detailed data and README to [62815d3](https://github.com/mapillary/OpenSfM/commit/62815d39e796ddc04389d9b59c76bada86dc1404)
and their relocation to [9011fd3](https://github.com/mapillary/OpenSfM/commit/9011fd352c650418dfb8cd327f6b8a7dc3a7915a);
subsequent contributions also need review.

For the vocabularies, PR 429 and PR 466 explain the use of the assets but do
not identify a training corpus or provide a model-specific grant. A focused
inspection of the pinned OpenSfM `bow.py`, configuration, executable scripts
and documentation did not reveal a vocabulary training-data manifest. This is
a bounded search, not proof that no provenance record exists. The two trained
assets' rights and possible replacement with independently sourced and trained
vocabularies remain open.

### Installed CGAL/tag comparison and file-level leads

[Disposable run 40972161000](https://github.com/Archont561/ODM-conda/actions/runs/40972161000)
at `461c88b` repeated the build and compared the 806 traced installed CGAL
headers against the public v6.2.1 tag archive (SHA256
`4a0713351882989dda8b6bbfa942d5013b994f297fbebe1096ce664a92aff1a0`).
One was byte-identical and 805 differed. For the two sampled AABB headers,
the complete unified diff consists of expansion of `$URL$` and `$Id$` to
v6.2.1-specific metadata; the `GPL-3.0-or-later OR LicenseRef-Commercial`
SPDX line is unchanged. This explains those two sample mismatches, **not** all
805 differences; the other files have not been individually compared.

The exact 93 traced installed paths whose first 10,000 bytes contained the
GPL-or-commercial SPDX marker are listed in
`research/openmvs-cgal-gpl-header-trace.json`, linked to the exact host package
and run. This is a bounded reviewer lead: header dependency recording and
markers do not by themselves establish linked code, commercial licensing,
applicability of a particular grant, source obligations or notice sufficiency.
The other CGAL marker groups and Boost headers still require review.

The prior simple Boost string search has false negatives: for example, the
upstream 1.90.0 [`archive_exception.hpp`](https://github.com/boostorg/serialization/blob/boost-1.90.0/include/boost/archive/archive_exception.hpp)
wraps “Boost Software” and “License” across two lines, so the exact phrase is
absent despite its explicit license reference. Exact correspondence between
that upstream file and installed bytes has not been checked. The 272 unmarked
by the simple scanner must not be described as unlicensed or automatically
cleared. No source archives or binaries from the experiment were uploaded.

[Run 40974576156](https://github.com/Archont561/ODM-conda/actions/runs/40974576156)
repeated the same reduced build and compared all 806 traced installed CGAL
headers to the tag after normalizing expanded `$URL: ...$` and `$Id: ...$`
keywords. **805 matched after that normalization; one, `CGAL/version.h`, still
differed.** The first-10,000-byte SPDX markers matched for all 806 mapped
headers. This does not describe or justify the `version.h` difference, prove
that every possible header was traced, or establish a license grant or
corresponding-source completeness. No input or output files were uploaded.

[Disposable Seneca run 40973960114](https://github.com/Archont561/ODM-conda/actions/runs/40973960114)
verified that one installed fast-orthophoto scenario completed with the two
vocabulary assets and SQLite removed from its temporary prefix, using the
3,708-entry JSON sensor fallback. See `research/odm-fast-orthophoto-prototype.md`
for raster metadata and limitations. The package audit ran before removal; no
reduced package was created. BoW/VLAD modes would need replacement assets or a
clearly scoped unsupported-mode policy, and the original source archive still
contains the removed assets. This is a technical route to explore, not resolution
of asset rights, corresponding-source obligations or release approval.

The remaining `CGAL/version.h` mismatch was examined in [run 40978864742](https://github.com/Archont561/ODM-conda/actions/runs/40978864742),
which installed the same hash-identified CGAL 6.2.1 host package and compared
it to the pinned v6.2.1 tag archive. Beyond expanded URL/Id keywords, the
installed header reports Git hash `28811b671a12b5caa9e3688569dadbc6b3728fe6`
in place of upstream tag's placeholder `abcdef`, and release date `20260903`
in place of `20260608`; the version macro and LGPL-or-commercial SPDX marker
match. Installed SHA256 is
`9341bb068b6a12340594870fd9a625f6d9e428c4875cfec9d772e96d3990572b`,
upstream tag SHA256 is
`85e3082bcadd8ed8665f00718d2a314d4bcb1a11b64dae3585a640147747e4f8`.
The package metadata lists `share/doc/CGAL/LICENSE`, `LICENSE.GPL` and
`LICENSE.LGPL` plus an icon license. These observations do not establish
package source correspondence, which license option applies, the completeness
of notices or entitlement to distribute; qualified review remains open.

GitHub's annotated v6.2.1 tag object points to commit
[`28811b671a12b5caa9e3688569dadbc6b3728fe6`](https://github.com/CGAL/cgal/commit/28811b671a12b5caa9e3688569dadbc6b3728fe6),
the same hash embedded in the installed header; the commit author date is
2026-09-03. This explains the relationship to the tagged revision but does not
independently establish the provenance or completeness of the package's entire
source tree or accompanying notices.

### Scoped OpenSfM local-only research package

`research/recipes/opensfm-scoped-odm/recipe.yaml` defines a separate Linux
research package, not a production component. It builds from the same pinned
OpenSfM/pybind11/vmem research graph, then derives an installed package copy
without the two vocabularies or the SQLite sensor database. The transformation
verifies the three excluded hashes and exact `dataset.py` input, refuses
symlinks and overlapping paths, and preserves the original staged source. A
guard in dataset configuration explicitly rejects WORDS matching and positive
BoW/VLAD neighbor settings. The JSON sensor database remains, so cameras absent
from it may behave differently. Direct callers bypassing dataset configuration,
runtime mutation of configuration, other matching modes, complete relocation
and other operating systems remain outside this validation.

The scoped artifact has its own asset checks and a solver constraint excluding
co-installation with `opensfm-odm`, because both install the same executable
and Python module paths. This does not replace or weaken the original package's
audit. [Run 40980422096](https://github.com/Archont561/ODM-conda/actions/runs/40980422096)
built the initial scoped recipe, passed installed and fresh functional tests
and the distinct scoped audit; outputs were discarded. The original upstream
archives containing all three removed assets are still fetched and no reduced
corresponding-source archive is produced. This evidence does not resolve
rights in the remaining JSON, vmem, dependencies or model data, or authorize
redistribution. No release gates changed.

The guarded runtime was also exercised on the Seneca pipeline in
[run 40979586923](https://github.com/Archont561/ODM-conda/actions/runs/40979586923).
Default settings and three unsupported configurations were tested before the
pipeline; it completed and produced a 9521 × 10546 RGBA Byte EPSG:32617 raster
(110,476,182 bytes) and a 7,327,141-byte report. This run modified a disposable
prefix, not the final distinct package; outputs were discarded, and dataset
rights and visual/geographic quality were not independently validated.

The later distinct scoped package built, passed installed and fresh tests and
its separate audit in [run 40982191066](https://github.com/Archont561/ODM-conda/actions/runs/40982191066)
at `910804f`; its discarded package SHA256 was
`55ffe458560964100848b9b50df6238341c07ee025bf84760dba7b874cd7aaa0`.
Its packaged source notice identifies the omitted assets and unsupported modes.

A separate [run 40980893166](https://github.com/Archont561/ODM-conda/actions/runs/40980893166)
built and installed the actual scoped package (earlier revision `eb4fef2`, before
the later solver constraint and notice text), verified its omissions and mode
guards, and completed the Seneca pipeline. Its discarded scoped package SHA256
was `bef5d8d3b315169126a5a37f7c9ad274c13f2407a7968e763c080dc262ce189a`;
the resulting raster was 9539 × 10546 RGBA Byte EPSG:32617 (113,385,888 bytes),
with a 7,355,235-byte report. Outputs were discarded. This is functional
integration evidence, not visual/geographic validation or clearance of dataset
or software rights; the final isolation/notice changes were separately built and
audited as noted above.

For a repeatable disposable build, select `opensfm-scoped` in the
**Local-only Open component research build** workflow, or run locally:
`RESEARCH_COMPONENT=opensfm-scoped pixi run python scripts/run_open_research.py`.
The workflow does not upload its packages or sources. The existing `all` choice
continues to select the original OpenMVS and full OpenSfM research recipes.

### Local follow-up: scoped source and reduced-tree inventory

`scripts/opensfm_reduced_candidate.py` verifies the pinned original archive and
the three individual asset hashes, removes them, and writes a deterministic
local-only source archive with per-file hashes and modes. Two local runs on
2026-10-30 produced identical SHA256
`3f36288338532cee3bf5797b3031868b06b0a29eeb1adbd44905f1f3bf2f2fef`
(581 retained files; modes depend on the staged filesystem). The original
archive was fetched privately, not included or uploaded. At that point this was **not a buildable replacement** for the scoped recipe:
that recipe fetched the original, and its runtime transformation required the
three assets to be present before removal. A later private build is described below. The archive also omits separate pybind11,
vmem and other dependency sources, the guard and packaging changes. Its
manifest and exclusions are not a corresponding-source or rights determination.

Re-staged the exact OpenMVS/VCG/Eigen graph locally, applied the four research
patches and reproduced the 3274-file reduced fingerprint
`e64c1718c05d58ac74051a8a0a216febbcac7144898cea022d378af427549489`.
`scripts/openmvs_notice_inventory.py` generated
`research/openmvs-reduced-notice-inventory.json`: 17 notice-like filenames,
495 of 499 historical trace entries match; two excluded notices are absent and
two patch-modified files differ. The report identifies the previously inspected
CGAL host package and 93 traced GPL-or-commercial marker paths; other selected
host package identities appear in the earlier table above. Filename matching
misses embedded notices and may have false positives, and the historical trace
is neither the full dependency graph nor complete corresponding source. All
qualified source, rights and notice reviews remain open.

[Private run 41066302285](https://github.com/Archont561/ODM-conda/actions/runs/41066302285)
built the actual full and scoped OpenSfM research packages, separately audited
them, then used their local Conda channel metadata in three Pixi solves. Each
package solved independently; requesting both was rejected with both package
names in the solver output. This tests the scoped constraint on linux-64 for
those builds, not arbitrary package-manager versions or forced installations.
Packages and source inputs were discarded and no artifacts were uploaded.

### Reduced-source scoped package and shipped-notice comparison

[Private run 41068961668](https://github.com/Archont561/ODM-conda/actions/runs/41068961668)
reproduced the reduced OpenSfM candidate SHA256
`3f36288338532cee3bf5797b3031868b06b0a29eeb1adbd44905f1f3bf2f2fef`,
prepared a local-path recipe and built the scoped package from that source.
The builder checks the patched, staged 874-file graph fingerprint
`74c5be8ef66a189a8001816e7564e6b83144856dff176ca2674798f7b809b6d9`
including separately pinned pybind11 and vmem sources, and checks the assets
are absent before applying the configuration guard. The package passed its
installed and fresh functional tests and scoped audit; its discarded SHA256 was
`0c1bf13c2ab66aa5c21b8e41e924d98a9402f0acb674793921264a22caa0e3e6`.
No Seneca dataset test was run on this particular package. The original archive
was privately fetched to validate the candidate, and other source and legal
obligations are not resolved. No artifacts were uploaded.

The same run built the actual OpenMVS package from the previously fingerprinted
reduced tree and compared the 17 filename-based candidates against actual
payload and Conda metadata. Five match shipped license payload bytes; 12 do
not, and no `info/licenses/` files were present. Results and package hash are
in `research/openmvs-package-notice-comparison.json`. The candidate list includes
a script and contributor agreements, so non-matches do not imply each must be
shipped; it also misses embedded notices and transitive dependency terms.
The package passed installed/fresh tests and the existing research audit. This
is an inventory, not notice sufficiency, source completeness or release approval.

### OpenMVS unmatched-notice triage (2026-10-30)

`research/openmvs-notice-gap-triage.json` classifies all 12 unmatched
filename candidates from the prior package comparison against the historical
499-entry trace. It finds `libs/Math/LMFit/lmmin.cpp` and `lmmin.h` in the
trace, while LMFit's `COPYING` was absent from the prior research package.
The hash-recorded `COPYING` is a concrete notice lead. Research recipe build 4
now conservatively copies that exact file into the payload and declares it,
the root notices, VCG license and two Eigen notices under `about.license_file`;
the local audit checks their exact hashes in Conda `info/licenses/`. These
changes are not a legal conclusion or proof of a complete notice set.

Five other unmatched candidates are root Eigen license files; 251 paths under
`_external/eigen/Eigen/` occur in the historical trace, so applicability of
those texts still needs file-level review. The remaining candidates are in
benchmark, unsupported Eigen, VCG documentation or maintenance-script paths;
no matching paths from those subtrees occur in that historical trace. Absence
from this particular trace does **not** prove those files cannot be used or that
notices are unnecessary. The classification includes a relicense script and
contributor agreements because the original scan was filename-based.

Build 4 renders and focused local audit tests pass. Its native build, installed
and fresh tests, package audit and metadata verification are **not yet run**:
GitHub/API/codeload TLS handshakes failed in this session, preventing the
private workflow from being pushed or started. Build 3 evidence cannot certify
build 4. TASK-54 and the release gates remain open.

An offline synthetic `rattler-build` 0.68.0 package confirmed that the six
nested `license_file` paths are copied into `info/licenses/`, and the new
hash-based metadata verifier accepted those six synthetic bytes and rejected a
missing LMFit-style entry. This checks the packaging mechanism only; it is not
an actual OpenMVS build or validation of the staged notice bytes.
