---
id: TASK-32
title: Review dem2mesh package-readiness evidence
status: In Progress
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-29 11:19'
labels:
  - packaging
  - review
  - dem2mesh
milestone: m-4
dependencies:
  - TASK-6
type: task
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Independently review the deliverables produced by TASK-6 for the dem2mesh milestone. This task verifies evidence and unresolved restrictions rather than duplicating recipe implementation. Review deterministic mesh output, the installed GDAL linkage and the complete pinned meshing source graph. Human release approval, Prefix authorization and actual upload remain separate owner actions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Review actual installed-prefix functional/relocation and dependency-audit evidence for the declared Linux CPU target, with artifact identities, regressions and limitations linked to the work task.
- [ ] #2 Review exact source/patch/build-script correspondence, dependency source obligations, notices and applicable code/data/model license expressions; resolve blockers or explicitly retain them as open work.
- [ ] #3 Record a maintainer-facing readiness decision and remaining owner/platform conditions. Completing this task does not itself flip executable release flags, publish a binary or certify untested platforms.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Capture bounded actual fresh-test dependency evidence for the verified native artifacts; inspect available matching dependency notices and record limitations, preserving all owner gates.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-28 interim evidence triage: research/component-readiness-review.md records run IDs, artifact identities, source evidence and limitations. Per-recipe files match the historical native run but shared scripts changed; actual retained artifact/source inspection, current-commit native evidence as appropriate, dependency notices and qualified release review remain open. This is not approval and prerequisites and acceptance criteria remain unchecked.

2026-10-29: local batch review verified pinned archive bytes, extracted declared notice inputs and checked deterministic temporary source bundles and every manifest entry. Current-commit local native build was blocked by conda-forge repodata EOF; owner-dispatched batch validation and artifact review remain necessary. See research/component-readiness-review.md for component-specific evidence and limitations. Release gates remain false.

2026-10-29: native batch run 40844694283 at 2cc2861 and read-only artifact inspection 40846497463 passed build, installed and fresh retests, audit and source-manifest verification. Exact package/source hashes, ELF needs and bounded limitations are recorded in research/component-readiness-review.md. Legal/source completeness, ABI and owner decisions remain open; no release gates changed.

Hash-verified 53-file dem2mesh archive and reviewed CMake static JMeshLib inputs and source grants. Simplify.h names Sven Forstmann and MIT but does not contain the MIT permission text; project added full MIT text at 04ffc389 in 2019, after the vendored file existed. Candidate build 1 adds that exact text conservatively, keeps the original Simplify source attribution, and audits package payload and metadata bytes. Exact historical provenance and adequacy require review. Local build applied patch but failed at conda-forge compiler solve EOF; no candidate native artifact exists. Dirty-tree source bundle verified 244 manifest hashes. Detailed matrix: doc-12. No release gates changed.

Owner-dispatched native workflow https://github.com/Archont561/ODM-conda/actions/runs/40860898752 at commit 9355b8a8c904726f2b40f011dd43c64f457f22e0 passed build and packaged tests, fresh retest, audit, and source bundle; GitHub artifact 12892015321 reports ZIP SHA256 a04b3651eebe670cb9549904567565f15bf8047c9ef6faf71da720b20c2a67ad. Artifact bytes and exact selection have not been independently inspected. License/source review, provenance, owner approval and all release gates remain open.

CORRECTION: independent artifact inspection https://github.com/Archont561/ODM-conda/actions/runs/40861743072 verified artifact 12892015321 contains only dem2points build 0, not dem2mesh. The previously recorded run 40860898752 successfully validated dem2points, not dem2mesh build 1. No dem2mesh build 1 native artifact or tests exist from that run. Need an owner dispatch with dem2mesh selected; gates remain false.

Owner-dispatched native run https://github.com/Archont561/ODM-conda/actions/runs/40862757220 at 87a6098968fb25be4ca7e972b86c3dcf73ffbe70 passed build, installed tests, fresh retest, audit and source bundling. Temporary read-only inspection https://github.com/Archont561/ODM-conda/actions/runs/40863260951 verified ZIP SHA256 432b5b58d45d0cc3844a9980afc1ba84b0fb8f92da75af3b93d1863d33236d5f, dem2mesh-only artifact identity, package SHA256 6b1a2e6d64019a6de50e917cc454cf848da3e73049a570acaba2cda5f9d80f7d and source bundle SHA256 a4201af5e73b6752b42c53564282a6b48d2481bafdfb9c7ac7dc1ef110d8ef90. All 244 manifest entries and all seven declared notice bytes matched both payload and metadata; independent fresh retest and current audit passed. ELF RPATH $ORIGIN/../lib; libgdal.so.37. Source completeness, provenance, license/security/ABI and owner approval remain open; gates unchanged.
<!-- SECTION:NOTES:END -->
