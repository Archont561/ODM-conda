---
id: TASK-67
title: Prepare scoped OpenSfM asset-reduced research candidate
status: In Progress
assignee: []
created_date: '2026-10-30 00:18'
updated_date: '2026-10-30 00:18'
labels:
  - research
  - opensfm-odm
dependencies: []
ordinal: 67000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Exclude uncertain vocabulary and SQLite assets from a distinct scoped candidate and reject unsupported modes explicitly.
- [ ] #2 Test installed runtime and integration without weakening original audits.
- [ ] #3 Record missing functionality and open legal/source obligations; keep release gates closed.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implement fail-closed configuration guards and a separate local-only asset-reduced candidate; test it without changing the original research artifact or release gates.
<!-- SECTION:PLAN:END -->
