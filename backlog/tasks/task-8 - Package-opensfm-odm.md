---
id: TASK-8
title: Package opensfm-odm
status: In Progress
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-28 11:42'
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
<!-- SECTION:NOTES:END -->
