---
id: TASK-65
title: Test PoissonRecon after removing vendored JPEG source
status: In Progress
assignee: []
created_date: '2026-10-29 23:35'
updated_date: '2026-10-29 23:35'
labels:
  - research
  - poissonrecon-odm
dependencies: []
ordinal: 65000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Verify all original vendored JPEG files by hash, remove them in a private staged build and keep the candidate notice.
- [ ] #2 Build with host JPEG link guard, fresh test and audit without publishing the research artifact.
- [ ] #3 Document source-correspondence and rights limitations and keep release gates unchanged.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Verify a fixed vendored JPEG inventory from the pinned original archive, remove only those files from the disposable staged source before the Linux build, retain the patched README, and run normal checks. No sanitized distribution is created.
<!-- SECTION:PLAN:END -->
