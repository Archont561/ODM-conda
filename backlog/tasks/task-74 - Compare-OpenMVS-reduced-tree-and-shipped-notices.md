---
id: TASK-74
title: Compare OpenMVS reduced tree and shipped notices
status: Done
assignee: []
created_date: '2026-10-30 14:03'
updated_date: '2026-10-30 14:10'
labels:
  - research
  - openmvs-odm
dependencies: []
ordinal: 74000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Compare inventoried reduced tree notice candidates to actual research package payload and metadata
- [x] #2 Record omissions and limitations without legal clearance or release changes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Compare hashed inventory paths to actual private package payload and info/licenses; document heuristic gaps.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Private run 41068961668 built the actual package from the 3274-file reduced graph, passed installed/fresh tests and research audit. Five of 17 filename candidates match payload bytes, 12 do not; no info/licenses entries. Full comparison and package SHA in research/openmvs-package-notice-comparison.json. Filename heuristic includes scripts and contributor agreements; absence does not establish notice applicability. All original rights and source questions remain open under TASK-54; no artifacts uploaded.
<!-- SECTION:NOTES:END -->
