---
id: TASK-70
title: Verify scoped OpenSfM source and solver isolation
status: Done
assignee: []
created_date: '2026-10-30 13:44'
updated_date: '2026-10-30 13:55'
labels:
  - research
  - opensfm-odm
dependencies: []
ordinal: 70000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Prepare or investigate reproducible scoped source candidate with limitations
- [x] #2 Test actual solver conflict with full OpenSfM package or document blocker
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Create reproducible reduced upstream candidate and test solver conflict on real scoped/full package metadata.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Generated two identical private reduced OpenSfM source archives SHA256 3f36288338532cee3bf5797b3031868b06b0a29eeb1adbd44905f1f3bf2f2fef, 581 retained files and three hash-verified exclusions. Recipe not yet adapted: installed runtime transformation currently requires assets to exist before removal; separate pybind11, vmem, guard, patches and dependency sources absent. No source-completeness or rights claim.

Private run 41066302285 built and audited actual full and scoped packages. Pixi solver independently solved each from the local channel and rejected joint installation, with both names in conflict output. linux-64 solver evidence only; files discarded. Reduced source archive remains an investigation, not a usable recipe or complete source; TASK-36 remains open.
<!-- SECTION:NOTES:END -->
