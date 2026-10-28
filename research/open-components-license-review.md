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
- The current research builder copies packaging MIT and upstream LICENSE into
  the OpenMVS package, but not a demonstrated complete set of VCG, Eigen,
  OpenMVS third-party and CGAL notices or corresponding source. The research
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
  original applicable BSD notice and obtain clarification as needed. The builder
  copies the GPL text, but this discrepancy and any required upstream BSD notice
  remain unresolved. OpenSfM imports vmem, so do not treat its terms as irrelevant.
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
