---
id: TASK-71
title: Inventory reduced OpenMVS notice and dependency evidence
status: Done
assignee: []
created_date: '2026-10-30 13:44'
updated_date: '2026-10-30 13:48'
labels:
  - research
  - openmvs-odm
dependencies: []
ordinal: 71000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Produce verifiable inventory of retained notices and traced host dependencies
- [x] #2 Record unresolved source and legal review without changing release gates
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Reconcile retained-source notice inventory and traced host dependencies against exact reduced tree; identify gaps.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Re-staged exact OpenMVS/VCG/Eigen graph, applied four research patches, reproduced 3274-file tree fingerprint e64c1718c05d58ac74051a8a0a216febbcac7144898cea022d378af427549489 and generated research/openmvs-reduced-notice-inventory.json: 17 filename candidates; 495 historical entries match, 2 excluded notices absent, 2 modified by patch. Report references prior hashed CGAL host trace. Filename heuristics and partial host inventory are not comprehensive; TASK-54 remains open.
<!-- SECTION:NOTES:END -->
