---
id: TASK-68
title: Inspect remaining CGAL source and notice evidence
status: Done
assignee: []
created_date: '2026-10-30 00:18'
updated_date: '2026-10-30 00:20'
labels:
  - research
  - openmvs-odm
dependencies: []
ordinal: 68000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Explain the remaining installed CGAL version header difference and inspect traced dependency notice evidence.
- [x] #2 Document exact observations and unresolved qualified-review and source obligations.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Compare exact installed and upstream CGAL version headers in disposable native environment, inspect dependency notices, and document qualified-review leads without asserting clearance.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Run 40978864742 compared exact CGAL 6.2.1 host package to tag: version.h differs in expanded keywords, Git hash and release date; SPDX and version macro match. Recorded hashes and installed license file paths. Source and qualified legal review remain open in TASK-54.
<!-- SECTION:NOTES:END -->
