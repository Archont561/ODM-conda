---
id: TASK-67
title: Prepare scoped OpenSfM asset-reduced research candidate
status: Done
assignee: []
created_date: '2026-10-30 00:18'
updated_date: '2026-10-30 00:58'
labels:
  - research
  - opensfm-odm
dependencies: []
ordinal: 67000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Exclude uncertain vocabulary and SQLite assets from a distinct scoped candidate and reject unsupported modes explicitly.
- [x] #2 Test installed runtime and integration without weakening original audits.
- [x] #3 Record missing functionality and open legal/source obligations; keep release gates closed.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implement fail-closed configuration guards and a separate local-only asset-reduced candidate; test it without changing the original research artifact or release gates.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented a distinct local-only scoped recipe and asset-reduced runtime with explicit WORDS/BoW/VLAD config guards. Initial package run 40980422096 passed installed/fresh tests and its distinct audit; a stricter conflict-constraint build and full dataset integration were then started (results below). Original archives, remaining asset rights and corresponding-source scope remain open.

Guarded disposable runtime completed Seneca in run 40979586923; 9521 x 10546 RGBA Byte EPSG:32617; outputs discarded. Final scoped recipe at 910804f passed native build, installed/fresh tests and separate audit in 40982191066; discarded package SHA256 55ffe458560964100848b9b50df6238341c07ee025bf84760dba7b874cd7aaa0.

Actual distinct scoped package at eb4fef2 completed Seneca in run 40980893166 after installed omission and guard checks. Discarded package SHA256 bef5d8d3b315169126a5a37f7c9ad274c13f2407a7968e763c080dc262ce189a; raster 9539 x 10546 RGBA Byte EPSG:32617, outputs discarded. Later isolation constraint and notice text separately validated in 40982191066. Rights, original archive and corresponding source remain open under TASK-36; no release approved.
<!-- SECTION:NOTES:END -->
