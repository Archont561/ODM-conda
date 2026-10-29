---
id: TASK-63
title: Test OpenSfM asset-reduced runtime in ODM Seneca
status: In Progress
assignee: []
created_date: '2026-10-29 23:33'
updated_date: '2026-10-29 23:33'
labels:
  - research
  - integration
dependencies: []
ordinal: 63000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Run installed functional and end-to-end tests with the two uncertain vocabularies and SQLite database absent.
- [ ] #2 Record changed runtime coverage, fallback behavior, raster metadata and remaining source and license limitations.
- [ ] #3 Do not upload research sources, binaries or dataset outputs or change release gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Build and audit original research components without modification; in a disposable installed prefix only, verify and remove two vocabularies and the SQLite database, assert fallback behavior, and run the reduced OpenMVS Seneca experiment. This does not create a distributable artifact.
<!-- SECTION:PLAN:END -->
