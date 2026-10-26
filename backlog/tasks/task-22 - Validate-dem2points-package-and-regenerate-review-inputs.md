---
id: TASK-22
title: Validate dem2points package and regenerate review inputs
status: To Do
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-26 20:59'
labels:
  - packaging
  - validation
  - dem2points
milestone: m-0
dependencies:
  - TASK-1
type: task
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The dem2points recipe already exists, but historical native artifacts were intentionally cleaned. Regenerate current evidence for the initial Linux CPU package; this is validation work, not permission to publish. Recheck the GDAL-linked executable and declared runtime dependencies; report the actual tested host rather than claiming minimum-glibc certification.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Build the selected immutable source/recipe and test the installed prefix, relocation, functional fixtures and declared dynamic dependencies; preserve explicit unsupported modes/platform limits.
- [ ] #2 Regenerate artifact audits and exact corresponding-source/staging inputs, recording hashes and any modified-source notices without committing generated binaries, archives or reports.
- [ ] #3 Keep code/source/license/native-validation acknowledgements false until their independent maintainer review; for FPCFilter, TASK-2's accepted regression outcome is included before claiming validation.
<!-- AC:END -->
