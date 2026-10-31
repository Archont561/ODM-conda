---
id: TASK-91
title: Build ODM Python dependencies from pinned source
status: Done
assignee: []
created_date: '2026-10-30 22:35'
updated_date: '2026-10-30 23:08'
labels:
  - odm
  - packaging
  - research
dependencies: []
ordinal: 91000
---

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Replace the five private upstream-wheel repacks with pinned source builds and explicitly staged build dependencies.
- [x] #2 Build and test each source-built Conda package and validate the ODM integration without separate PyPI dependencies where feasible.
- [x] #3 Record remaining source completeness, native audit and release blockers without weakening gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Use exact SHA-pinned PyPI source archives and isolated offline builds; inspect JPEG XL Rust crate and native dependency staging before constructing its source build; privately build and fresh-test candidates and integrate if all inputs resolve.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Replaced five private wheel repacks with source-built candidates, each with research build 1; four built and fresh-tested in 41139276835. JPEG XL source archive SHA256 8ea589fc559ea7c5dfccb42af4d8148f5db508f5f4d4518328bab5a31fcb268e, locked registry crates staged by cargo vendor then offline maturin dynamic build. Run 41140647274 tested guarded crate staging, fresh JPEG XL roundtrip and ELF NEEDED libjxl.so.0.11/libjxl_threads.so.0.11. Full Conda-only ODM run 41139889906 used earlier helper, built five candidates and ODM build 2 SHA256 3b4fac8f2755300d4765125c02b28894ff6221241c58dd87910400af5f160c06; replayed lock 5ac9c3df78ed7fd205b199b28c05bca546caed1020f353ba2fc68611a607be7a into relocated prefix with 456 matching records and passed launcher, Seneca and raster sanity. No binaries, source bundle, imagery or lock retained. Complete source, notices, native security and owner release gates remain open.
<!-- SECTION:NOTES:END -->
