---
id: TASK-6
title: Package dem2mesh
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-27 08:38'
labels:
  - component
  - dem2mesh
milestone: m-4
dependencies: []
priority: medium
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upstream: https://github.com/OpenDroneMap/dem2mesh
Reference in selected ODM build: 334
Next work: Carry the selected ODM release patches and audit JMeshLib.
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
Deferred from the fast-orthophoto MVP (doc-11, approved). Not a gate for TASK-13. Resume after the MVP ships.
<!-- SECTION:NOTES:END -->
