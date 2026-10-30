---
id: TASK-66
title: Prepare reproducible reduced PoissonRecon source candidate
status: In Progress
assignee: []
created_date: '2026-10-30 00:18'
updated_date: '2026-10-30 00:18'
labels:
  - research
  - poissonrecon-odm
dependencies: []
ordinal: 66000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Verify pinned source, construct deterministic reduced candidate without vendored JPEG, and retain required packaging inputs.
- [ ] #2 Test reproduction, safety, native build and candidate source manifest without distributing restricted original.
- [ ] #3 Document unresolved source and license obligations and keep release gates closed.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implement a fail-closed local-only verified reducer and deterministic candidate bundle, test it, and validate a native build against the candidate; do not claim legal clearance.
<!-- SECTION:PLAN:END -->
