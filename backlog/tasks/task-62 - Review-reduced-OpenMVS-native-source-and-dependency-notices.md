---
id: TASK-62
title: Review reduced OpenMVS native source and dependency notices
status: Done
assignee: []
created_date: '2026-10-29 22:54'
updated_date: '2026-10-29 23:01'
labels:
  - research
dependencies: []
ordinal: 62000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Compare the retained tree with the earlier notice inventory and record changed, omitted and matching entries.
- [x] #2 Inspect the reduced build host package identities and selected CGAL and Boost headers when available.
- [x] #3 Document notice obligations and unresolved corresponding-source scope without authorizing distribution.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Verify and reconstruct pinned research trees locally, compare the retained file hashes with the prior inventory, inspect a disposable native build and its host dependency metadata, and record scoped licensing evidence.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Compared 499 historical entries with the all-four-patch retained tree: 495 match, two excluded and two patched. Disposable native run 40969462242 recorded exact CGAL/Boost/Eigen host identities and header dependency traces; source and per-file legal correspondence remain open in TASK-54. Documented reviewer leads and limitations in research/open-components-license-review.md; no release clearance.
<!-- SECTION:NOTES:END -->
