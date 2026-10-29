---
id: TASK-58
title: Investigate OpenVINO dependency and license metadata for odm-orthophoto
status: Done
assignee: []
created_date: '2026-10-29 19:59'
updated_date: '2026-10-29 19:59'
labels:
  - research
dependencies: []
ordinal: 58000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Trace why the historical standalone solve includes OpenVINO packages using versioned upstream recipe evidence.
- [x] #2 Explain the missing package license labels using versioned feedstock evidence and preserve the limits of that explanation.
- [x] #3 Record concrete next steps for any assembled distribution without changing release gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Compare the historical solve with versioned OpenCV and OpenVINO feedstock recipes and the later metadata fix; distinguish source-level evidence from verified binary metadata, document remaining distribution review and validate repository checks.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Traced the historical solve to OpenCV host dependency and OpenVINO run exports using versioned feedstock recipes; upstream PR 147 explains the missing split-output license labels and adds Apache-2.0 in a later version. Exact older binaries were not all inspected and assembled-distribution notice/source review remains required. No gates changed.
<!-- SECTION:FINAL_SUMMARY:END -->
