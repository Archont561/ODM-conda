---
id: TASK-80
title: Investigate Seneca dataset rights and raster sanity checks
status: In Progress
assignee: []
created_date: '2026-10-30 15:38'
updated_date: '2026-10-30 15:40'
labels:
  - research
  - integration
dependencies: []
ordinal: 80000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document immutable dataset license and provenance evidence with unresolved rights
- [ ] #2 Implement and test bounded raster sanity checks without claiming geographic validation
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Check immutable Seneca repository metadata and add conservative raster sanity tests; do not assert dataset rights.
<!-- SECTION:PLAN:END -->
