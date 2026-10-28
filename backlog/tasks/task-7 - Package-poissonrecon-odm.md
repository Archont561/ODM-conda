---
id: TASK-7
title: Package poissonrecon-odm
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 20:59'
labels:
  - component
  - poissonrecon-odm
milestone: m-5
dependencies: []
priority: medium
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upstream: https://github.com/OpenDroneMap/PoissonRecon
Reference in selected ODM build: 290
Next work: Port make/MSBuild integration and the exact selected ODM release patches.
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
Preliminary source research (2026-10-28): ODM 3.6.2 SuperBuild uses mutable branch `290`, resolved to `97caa6d34d1b05b59888bed019dea89ced74445e`; codeload archive SHA256 `88743428a97cbeed7d55e713fcfa42caebbfb7dcb2467d68899bd8feab95364b`. The inline SuperBuild definition runs `make poissonrecon` and copies `Bin/Linux/PoissonRecon`; it specifies no patch command for this component. Root LICENSE is MIT, but bundled sources and the actual build inputs still need a complete notice audit. No recipe or native validation exists.
<!-- SECTION:NOTES:END -->
