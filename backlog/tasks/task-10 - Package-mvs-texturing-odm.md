---
id: TASK-10
title: Package mvs-texturing-odm
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 20:59'
labels:
  - component
  - mvs-texturing-odm
milestone: m-8
dependencies: []
priority: medium
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upstream: https://github.com/OpenDroneMap/mvs-texturing
Reference in selected ODM build: c5a4d0c9a434553533c6e39d426e349fcfa5f48d
Next work: Stage MVE and all nested external sources; audit their licenses.
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
Preliminary source research (2026-10-28): ODM pins mvs-texturing commit `c5a4d0c9a434553533c6e39d426e349fcfa5f48d`; codeload archive SHA256 `295b11cb35c85f44908294bc89cd7d4f1057dee0016cc4cd35a5ed01570766f8`. Its SuperBuild also uses mutable OpenDroneMap/mve branch `356`, resolved to `90f13c18f92db6089c06c8c2451e283911f5f634` (archive SHA256 `f4d0d76a925d7482d14c2050b4488718c824947a3895eac196eac70ef19fc699`). The texturing CMake declares additional external projects: mapmap_cpu at `fa526e0963ca3e431a02aa7b9e87b85ba8a8e304`, rayint mutable branch `cuda`, and Eigen 3.3.2. Resolve and audit the complete enabled nested graph, disable network bootstrap and stage source explicitly. No recipe or native validation exists.
<!-- SECTION:NOTES:END -->
