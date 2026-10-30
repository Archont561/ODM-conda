---
id: TASK-76
title: Investigate unmatched OpenMVS notice candidates
status: Done
assignee: []
created_date: '2026-10-30 14:21'
updated_date: '2026-10-30 14:38'
labels:
  - research
  - openmvs-odm
dependencies: []
ordinal: 76000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Classify unmatched notice candidates against traced build sources and record evidence
- [x] #2 Record open notice and rights obligations without assuming clearance
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Classify the 12 unmatched notice candidates, add a hash-verified LMFit notice and metadata to the research package, then native-retest.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Classified all 12 prior filename candidates using the historical trace; LMFit lmmin.cpp and lmmin.h are traced, and COPYING SHA256 09c21b5a8ca469b20e0ce3795f19370affba36f532e480e593c9712c91caf4c4 was not shipped in build 3. Research build 4 now declares/copies it and carries six notices in Conda metadata, with hash-checked research audit; recipe renders and focused tests pass. Native build/installed/fresh tests and audit not run because GitHub TLS failed; do not treat build 4 as validated or close legal TASK-54.

Offline synthetic rattler-build 0.68.0 probe packaged six fake nested license paths into info/licenses; the real metadata verifier passed exact hashes and rejected removal of the LMFit-style entry. This exercises metadata mechanics only, not the actual OpenMVS build 4.

Connectivity restored: private run 41072875690 built research build 4, passed installed/fresh tests and separate payload plus six Conda metadata notice checks. Package SHA256 25c69f66d30f9943bdca7646cab46d3eb1bc6c917781d6919dcc4a35115afabd, discarded. Standard research build stages original graph; legal, remaining notice, transitive and corresponding source review remain open under TASK-54.
<!-- SECTION:NOTES:END -->
