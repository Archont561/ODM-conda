---
id: TASK-90
title: Isolate private ODM variants and package Python runtime dependencies
status: In Progress
assignee: []
created_date: '2026-10-30 21:12'
updated_date: '2026-10-30 21:12'
labels:
  - odm
  - packaging
  - research
dependencies: []
ordinal: 90000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Give private ABI/source variants Conda identities distinct from production artifacts.
- [ ] #2 Package the previously separate Python dependencies or document precisely blocked inputs without concealing them.
- [ ] #3 Validate a fresh ODM environment without separately adding PyPI dependencies where feasible, and record remaining release blockers.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use explicit research build strings for ABI/source variants and inspect exact pinned Python wheels and source packaging. Test private channel solve and integration without weakening release gates.
<!-- SECTION:PLAN:END -->
