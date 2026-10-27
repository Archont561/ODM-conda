---
id: TASK-16
title: Add validated native platform variants after Linux CPU integration
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-27 08:38'
labels:
  - platforms
dependencies:
  - TASK-13
  - TASK-47
priority: medium
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Linux x86-64 CPU is the only implemented target. Add native Windows and Apple Silicon deliberately, then assess Linux ARM and CUDA separately. Do not copy CloudCompare's matrix or assume Intel macOS support. Review helper DLLs, CUDA redistribution and model/data rights before packaging.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each advertised target has native build, relocation, functional and dependency/notice audits.
- [ ] #2 CI, selectors, source staging and release records agree on the actually supported targets.
- [ ] #3 GPU packaging is kept separate until both technical behavior and redistribution/copy-left compatibility are reviewed.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Deferred from the fast-orthophoto MVP (doc-11, approved). Not a gate for TASK-13. Resume after the MVP ships.
<!-- SECTION:NOTES:END -->
