---
id: TASK-8
title: Package opensfm-odm
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 20:59'
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
Preliminary source research (2026-10-28): ODM pins OpenSfM commit `c5328439465e6ace011f39077d1077d7b1cdd65d`; codeload archive SHA256 `2bd9ec9ed20c5b426ff2808734e0a8849e2375038e378105f97128e48d704f8e`. Its `.gitmodules` declares pybind11 at `opensfm/src/third_party/pybind11`, gitlink `a2e59f0e7065404b44dfe92a28aca47ba1378dc4`; it is not included in the main codeload archive. ODM recursively initializes submodules, builds against Ceres, OpenCV and gflags and disables upstream CMake tests. Nested sources, licensing, Python ABI and installed dataset validation remain open. Current source staging explicitly rejects additional sources; extend it safely before enabling this recipe.
<!-- SECTION:NOTES:END -->
