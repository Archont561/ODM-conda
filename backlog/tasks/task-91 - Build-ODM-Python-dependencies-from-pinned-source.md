---
id: TASK-91
title: Build ODM Python dependencies from pinned source
status: In Progress
assignee: []
created_date: '2026-10-30 22:35'
updated_date: '2026-10-30 22:35'
labels:
  - odm
  - packaging
  - research
dependencies: []
ordinal: 91000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Replace the five private upstream-wheel repacks with pinned source builds and explicitly staged build dependencies.
- [ ] #2 Build and test each source-built Conda package and validate the ODM integration without separate PyPI dependencies where feasible.
- [ ] #3 Record remaining source completeness, native audit and release blockers without weakening gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use exact SHA-pinned PyPI source archives and isolated offline builds; inspect JPEG XL Rust crate and native dependency staging before constructing its source build; privately build and fresh-test candidates and integrate if all inputs resolve.
<!-- SECTION:PLAN:END -->
