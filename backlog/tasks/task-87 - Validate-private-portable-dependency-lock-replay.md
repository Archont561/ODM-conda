---
id: TASK-87
title: Validate private portable dependency lock replay
status: In Progress
assignee: []
created_date: '2026-10-30 19:26'
updated_date: '2026-10-30 19:26'
labels:
  - research
  - integration
dependencies: []
ordinal: 87000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create private lock and verified local package set without publishing binaries
- [ ] #2 Replay exact lock in relocated fresh prefix and validate integration
- [ ] #3 Document source, notice and portability limitations
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Build private variants, create isolated original lock and archive set, relocate byte-identical lock/manifest and packages, replay with a fresh prefix and compare inventories, then run private Seneca and raster checks.
<!-- SECTION:PLAN:END -->
