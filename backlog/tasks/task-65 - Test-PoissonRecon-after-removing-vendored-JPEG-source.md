---
id: TASK-65
title: Test PoissonRecon after removing vendored JPEG source
status: Done
assignee: []
created_date: '2026-10-29 23:35'
updated_date: '2026-10-29 23:45'
labels:
  - research
  - poissonrecon-odm
dependencies: []
ordinal: 65000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Verify all original vendored JPEG files by hash, remove them in a private staged build and keep the candidate notice.
- [x] #2 Build with host JPEG link guard, fresh test and audit without publishing the research artifact.
- [x] #3 Document source-correspondence and rights limitations and keep release gates unchanged.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Verify a fixed vendored JPEG inventory from the pinned original archive, remove only those files from the disposable staged source before the Linux build, retain the patched README, and run normal checks. No sanitized distribution is created.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Private native run 40974184592 verified and removed all 59 original vendored JPEG files from the staged tree while retaining candidate README, built with host JPEG guard, fresh-tested and audited. The full archive is still fetched and normal source metadata/bundle do not describe this experiment; no source/binary upload or release approval. See research/poissonrecon-readiness-review.md.
<!-- SECTION:NOTES:END -->
