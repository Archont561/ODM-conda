---
id: TASK-89
title: Build private Conda ODM fast-orthophoto application candidate
status: In Progress
assignee: []
created_date: '2026-10-30 20:34'
updated_date: '2026-10-30 20:34'
labels:
  - odm
  - packaging
  - research
dependencies: []
ordinal: 89000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create a pinned local-only ODM application recipe with relocatable launcher and explicit component dependencies.
- [ ] #2 Build and install the candidate with actual compatible component packages and test its launcher and a real pipeline privately.
- [ ] #3 Document exact scope and remaining publication blockers without weakening gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Package the existing prefix-adapted ODM prototype as a local-only Conda candidate; declare actual component and runtime dependencies, then test a fresh privately assembled environment and Seneca pipeline. Preserve release gates and record any unvalidated inputs.
<!-- SECTION:PLAN:END -->
