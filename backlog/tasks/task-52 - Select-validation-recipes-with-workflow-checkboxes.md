---
id: TASK-52
title: Select validation recipes with workflow checkboxes
status: Done
assignee: []
created_date: '2026-10-28 11:52'
updated_date: '2026-10-28 11:52'
labels: []
dependencies: []
type: enhancement
ordinal: 52000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Manual build workflow exposes one boolean checkbox per implemented component and defaults to all if none are checked.
- [x] #2 Selected components are built, tested, audited and source-bundled consistently, without changing release gates.
- [x] #3 Offline checks cover selections, malformed input, documentation and workflow validation.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use boolean dispatch inputs, derive the selected components from validated runner environment values, share the resulting selection with later steps, and verify public CLI and workflow seams.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added one boolean workflow input per implemented component, with no selections meaning all; propagated validated checkbox selections across build, test, audit and sources. Documented migration from the prior string input and preserved comma-separated local CLI selection. Offline pixi check passed with 117 tests and Actionlint; native workflow was not dispatched.
<!-- SECTION:FINAL_SUMMARY:END -->
