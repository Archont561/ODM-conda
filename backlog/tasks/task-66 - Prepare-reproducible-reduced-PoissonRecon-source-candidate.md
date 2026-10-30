---
id: TASK-66
title: Prepare reproducible reduced PoissonRecon source candidate
status: Done
assignee: []
created_date: '2026-10-30 00:18'
updated_date: '2026-10-30 00:57'
labels:
  - research
  - poissonrecon-odm
dependencies: []
ordinal: 66000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Verify pinned source, construct deterministic reduced candidate without vendored JPEG, and retain required packaging inputs.
- [x] #2 Test reproduction, safety, native build and candidate source manifest without distributing restricted original.
- [x] #3 Document unresolved source and license obligations and keep release gates closed.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implement a fail-closed local-only verified reducer and deterministic candidate bundle, test it, and validate a native build against the candidate; do not claim legal clearance.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Local-only source candidate deterministically excludes 59 vendored JPEG files and includes packaging plus hash manifest. Run 40979099535 recreated two identical candidates, verified file hashes and built, installed/fresh-tested and audited from an adapted recipe; exact candidate SHA recorded via 40979919908. Original archives and outputs private; normal metadata and source bundle do not describe the reduction. Rights and source scope remain open in TASK-56.

Updated generator at 910804f: run 40982191055 passed repeated archive comparison, manifest and absent-JPEG checks, native build, installed/fresh tests and normal audit; outputs discarded.
<!-- SECTION:NOTES:END -->
