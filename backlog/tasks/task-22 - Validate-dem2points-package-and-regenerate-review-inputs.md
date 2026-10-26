---
id: TASK-22
title: Validate dem2points package and regenerate review inputs
status: In Progress
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-26 21:34'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Regenerate the hash-verified dem2points source/staging bundle from the immutable commit, inspect/review exact source inputs, and attempt the prescribed native build, installed functional tests, audit and relocation checks. Record exact host/tool availability and block any acceptance criterion requiring native tooling that cannot be obtained; never reuse historical binaries as current evidence. Keep all release acknowledgements false.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-26: regenerated source staging from the immutable dem2points commit. The downloaded codeload archive SHA256 matches the manifest (b5d87bcafd52fd4c52f5c8828086f2ea34338742ae293cbd21bde1fd55b9fa67); generated corresponding-source bundle SHA256 is 9271c67109881484f45c09f07e4fd73026d1bee5e580dfb930dc7f66da8373d6 and repeated generation was byte-identical. The bundle contains the exact upstream archive and current packaging recipe/scripts/tests/locks; generated archives remain ignored/uncommitted. Attempted `python scripts/build.py --component dem2points`; blocked because rattler-build/Pixi are absent. This host also lacks CMake, Ninja, GDAL development headers/tools and patchelf, so no fresh package build, installed-prefix/relocation/functional test, artifact audit or dynamic-dependency report could be produced. Historical results in backlog doc-8 are not reused as current evidence. No acknowledgements were changed; AC #2 is partially satisfied for regenerated source staging only, while AC #1 and the artifact/audit parts of AC #2 remain blocked.
<!-- SECTION:NOTES:END -->
