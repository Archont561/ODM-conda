---
id: TASK-82
title: Trace scoped OpenSfM and OpenMVS source and notice evidence
status: Done
assignee: []
created_date: '2026-10-30 16:26'
updated_date: '2026-10-30 16:36'
labels:
  - research
dependencies: []
ordinal: 82000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Investigate exact pinned source and unresolved notice evidence
- [x] #2 Document remaining source and license blockers without approving release
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Review exact source pins, exclusion mechanisms and notice gaps, probe upstream evidence and retain bounded verified findings.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Hash-matched 251 historical traced Eigen files against the exact pinned archive and recorded conservative marker search. COPYING.README describes mixed licenses and MPL2_ONLY; IncompleteLUT has a claimed SPARSKIT relicensing permission which is not independently verified. Scoped OpenSfM pinned graphs and exclusions remain documented; original archives, embedded/host dependency notices and source rights remain unresolved.

Recorded exact pinned retained sensor_data.json hash and attributed readme blob/hash; research audit checks JSON but not readme presence. Upstream license assertion is not independent grant or notice review.
<!-- SECTION:NOTES:END -->
