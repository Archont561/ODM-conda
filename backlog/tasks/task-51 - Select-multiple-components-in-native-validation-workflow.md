---
id: TASK-51
title: Select multiple components in native validation workflow
status: Done
assignee: []
created_date: '2026-10-28 10:58'
updated_date: '2026-10-28 10:58'
labels: []
dependencies: []
type: enhancement
ordinal: 51000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Workflow and local validation commands accept all, one component, or an ordered comma-separated selection.
- [x] #2 Invalid selections fail before any component build; release gates remain unchanged.
- [x] #3 Document and test the selection behavior.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Validate the complete selection in the shared CLI selector, use a quoted string workflow input, exercise rendered CLI behavior and run offline checks.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented comma-separated workflow and local component selection, validated the full list before execution, preserved release-stage single-component guard and all existing release checks. Offline pixi run check passed with 112 tests, workflow lint and recipe rendering; native CI dispatch/build was not run.
<!-- SECTION:FINAL_SUMMARY:END -->
