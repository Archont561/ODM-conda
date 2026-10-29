---
id: TASK-61
title: Validate reduced OpenMVS in ODM dataset integration
status: In Progress
assignee: []
created_date: '2026-10-29 22:45'
updated_date: '2026-10-29 22:45'
labels:
  - integration
dependencies: []
ordinal: 61000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Build and retest the reproducibly reduced OpenMVS tree and use it in a disposable nine-component ODM Seneca trial.
- [ ] #2 Inspect the final raster metadata when produced and document exact inputs and limitations.
- [ ] #3 Keep research sources, packages and dataset outputs private; do not change release gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Reuse the hash-verified disposable Seneca pipeline, switching its OpenMVS research build to the reproducibly reduced copy; verify final raster if generated and record success or blocker.
<!-- SECTION:PLAN:END -->
