---
id: TASK-69
title: Prepare reduced Poisson research recipe and source metadata
status: Done
assignee: []
created_date: '2026-10-30 13:44'
updated_date: '2026-10-30 13:57'
labels:
  - research
  - poissonrecon-odm
dependencies: []
ordinal: 69000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Generate reproducible candidate-specific source metadata and recipe without claiming complete source
- [x] #2 Verify manifest and native build or record concrete blockers
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Generate private source, recipe and explicit provenance; build and verify without changing production audits.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created generated local-path recipe with accurate research-only metadata. Candidate file hashes and all retained/omitted upstream files compared with hash-pinned original; generated source doc disclaims source offer. Separate native validation underway; production audit unchanged.

Private run 41066302285 compared two candidates, verified source hashes back to original, built generated local recipe, passed installed/fresh tests and checked accurate installed source metadata. Normal production audit correctly rejected research metadata; separate full research artifact audit remains future work. Outputs discarded; TASK-56 remains open.
<!-- SECTION:NOTES:END -->
