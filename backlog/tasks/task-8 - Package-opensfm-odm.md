---
id: TASK-8
title: Package opensfm-odm
status: In Progress
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-28 19:08'
labels:
  - component
  - opensfm-odm
milestone: m-6
dependencies: []
priority: high
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upstream: https://github.com/OpenDroneMap/OpenSfM
Reference in selected ODM build: c5328439465e6ace011f39077d1077d7b1cdd65d
Next work: Python/C++ recipe, Python/NumPy ABI pins, vendored sources, imports, and an SfM dataset test.
Read the exact ODM reference recorded in components.json before choosing source revisions. This is planned work, not an existing recipe or a supported package.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The source graph is pinned to immutable commits and archive checksums, with ODM-required patches reviewed.
- [ ] #2 A real recipe declares build/host/run dependencies, carries the applicable notices/source, and passes installed-prefix functional tests.
- [ ] #3 components.json, source staging, artifact audits and human release gates are extended intentionally; no placeholder package is published.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Preliminary source research (2026-10-28): ODM pins OpenSfM commit `c5328439465e6ace011f39077d1077d7b1cdd65d`; codeload archive SHA256 `2bd9ec9ed20c5b426ff2808734e0a8849e2375038e378105f97128e48d704f8e`. Its `.gitmodules` declares pybind11 at `opensfm/src/third_party/pybind11`, gitlink `a2e59f0e7065404b44dfe92a28aca47ba1378dc4`; it is not included in the main codeload archive. ODM recursively initializes submodules, builds against Ceres, OpenCV and gflags and disables upstream CMake tests. The pybind11 archive SHA256 is `1da0a5c38950e4f49329e9de10c59b2527840a1b963113f1c53b455971cd6aef`. A local staging-primitive smoke test assembled the two hash-checked archives and confirmed pybind11's CMakeLists.txt at the gitlink path. This is not a build or a source-completeness review. Nested sources, licensing, Python ABI and installed dataset validation remain open. Recipe, source-bundle and release paths still reject additional sources; integrate and review them safely before enabling this recipe.

2026-10-28 research: re-staged hash-verified OpenSfM and pybind11 archives. Configured the upstream CMake project with tests disabled against restored odm-dev Ceres/OpenCV and default Python 3.12, using system GCC 12. Initial build reached bundle code and failed to find ceres headers; explicitly setting ADDITIONAL_INCLUDE_DIRS resolved that lookup but compilation still failed, see following compatibility evidence. This is neither an isolated build nor an installed package and the submodule/source-bundle production guards remain in force.

Further research (2026-10-28): adding a temporary -DGLOG_USE_GLOG_EXPORT flag and explicit odm-dev include path allowed all eight native OpenSfM modules to compile with system GCC 12 against restored Ceres/OpenCV and Python 3.12. All eight imported and scripts/opensfm_fixture.py passed basic equatorial ECEF and identity-pose checks with NumPy in the odm-dev environment. This is a mixed-environment local research build, not a tested patch, isolated Conda build, installed-prefix validation or SfM dataset test. Ceres should be integrated through proper imported targets rather than relying on the ad hoc preprocessor workaround. Production staging/bundling, Python packaging/ABI and source/license review remain unresolved.

2026-10-28: created research/patches/opensfm-ceres-config.patch (SHA256 1cbf2c8044e0281368c8802205f14816fc3b635fb419a7d8fa3570603fdfd773) to find Ceres through its exported CMake config and propagate its target usage requirements through OpenSfM libraries, rather than manually injecting glog defines or include paths. Patch applied cleanly to a freshly staged exact source graph. With GCC 12 and the restored mixed Python/odm-dev environment, a clean CMake configuration and single-job build completed; after deleting old module outputs and rebuilding, all eight extensions were recreated and the research imports/ECEF/pose fixture passed. This is an experimental patch; no Conda compiler, isolated prefix, native package, SfM dataset, full notice review or release validation was performed.

2026-10-28: The pinned OpenSfM Git commit was fetched into a temporary local bare Git repository and scripts/verify_gitlinks.py verified its complete primary tree has exactly one gitlink: opensfm/src/third_party/pybind11 at a2e59f0e7065404b44dfe92a28aca47ba1378dc4, matching the experimental source plan. Automated negative tests reject altered, omitted and unexpected gitlinks. This does not verify nested gitlinks, archive-versus-tree equivalence, source completeness or enable production source staging.

2026-10-28 source-license triage: re-staged and hash-verified pinned OpenSfM plus pybind11. research/opensfm-notices.json records hashes of 12 root/third-party notices and selected data assets. Root LICENSE contains AGPL v3 text while README says ODM fork changes are AGPLv3 and also retains upstream wording that OpenSfM is BSD-style and LICENSE is BSD; this inconsistency needs qualified file-level review, not a guessed final SPDX expression. Bundled AKAZE and pybind11 notices contain BSD-3-clause terms, VLFeat COPYING contains BSD-2-clause terms. The sensor database readme claims simplified BSD despite the fork root AGPL text, and two bundled bag-of-words NPZ vocabulary files have unverified origin/training-data rights. Hashes establish identity, not redistribution permission. No owner approval or final license decision implied.

2026-10-28 follow-up source history: pinned setup.py includes both 10,000-word and 64-word NPZ vocabularies and config.py uses them as defaults. GitHub history shows the 10,000-word asset first added as opensfm/data/bow/bow_hahog_root_uchar.npz in c686ad2e8c62664c63115968d86c605c83f8b04a (feat: compute feature words), then renamed in d8cabec9e8a510d0c1c3a5be97dd8f6657ef09f9; the same latter commit added the 64-word asset. These commits establish repository history only, not training dataset provenance, model authorship or redistribution rights. AGPL/BSD ambiguity and license approval remain open; no package or publication is authorized.

2026-10-28 continued research: added scripts/opensfm_assets_fixture.py to verify the exact two default vocabulary files, sensor JSON and calibration YAML listed by pinned setup.py, rejecting missing, changed or symlinked assets. It passed on the hash-pinned staged source tree, with negative tests; this is an asset identity check, not an installed package, provenance review, functional dataset or distribution approval. No recipe or owner native workflow run yet.

2026-10-28: OpenSfM research tree guard now permits only exact provisional rattler source metadata plus known generated files, and rejects altered metadata and symlinks; verified on the actual pinned patched source with simulated runner files. The standalone research/pybind11-tests-disabled CMake harness configured the exact pinned pybind11 2.13.6 with CMake 3.31 and GCC 12: PYBIND11_TEST=OFF, BUILD_TESTING=OFF, FETCHCONTENT_FULLY_DISCONNECTED=ON and no pybind11 test build tree. This standalone subproject experiment is not a full OpenSfM configuration or network isolation; recipe and native validation remain open.

2026-10-28: added experimental local-only OpenSfM research recipe and isolated build/test runner; the recipe is not registered as a production component and native Conda build has not run. A separate owner-dispatched research workflow retains no package or source artifact and includes fresh retest and a bounded leak/RPATH audit. The package includes unresolved vocabulary assets and must not be distributed. Installed functional test currently checks native bindings, asset identity and CLI help only; an actual dataset run and review remain open.
<!-- SECTION:NOTES:END -->
