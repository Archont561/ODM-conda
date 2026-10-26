---
id: TASK-25
title: Validate fpcfilter package and regenerate review inputs
status: To Do
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-26 20:59'
labels:
  - packaging
  - validation
  - fpcfilter
milestone: m-1
dependencies:
  - TASK-2
type: task
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The fpcfilter recipe already exists, but historical native artifacts were intentionally cleaned. Regenerate current evidence for the initial Linux CPU package; this is validation work, not permission to publish. Include TASK-2's no-normals outcome, normals sampling and pass-through regressions; any retained limitation must be explicit and release acknowledgements re-reviewed after a patch.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Build the selected immutable source/recipe and test the installed prefix, relocation, functional fixtures and declared dynamic dependencies; preserve explicit unsupported modes/platform limits.
- [ ] #2 Regenerate artifact audits and exact corresponding-source/staging inputs, recording hashes and any modified-source notices without committing generated binaries, archives or reports.
- [ ] #3 Keep code/source/license/native-validation acknowledgements false until their independent maintainer review; for FPCFilter, TASK-2's accepted regression outcome is included before claiming validation.
<!-- AC:END -->
