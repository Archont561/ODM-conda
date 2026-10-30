---
id: TASK-36
title: Review opensfm-odm package-readiness evidence
status: In Progress
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-30 00:03'
labels:
  - packaging
  - review
  - opensfm-odm
milestone: m-6
dependencies:
  - TASK-8
type: task
ordinal: 36000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Independently review the deliverables produced by TASK-8 for the opensfm-odm milestone. This task verifies evidence and unresolved restrictions rather than duplicating recipe implementation. Review the pinned ODM fork, Python/NumPy/native extension ABI, relocated imports/entry points and all applicable notices; do not assume the fork is BSD-only. Human release approval, Prefix authorization and actual upload remain separate owner actions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Review actual installed-prefix functional/relocation and dependency-audit evidence for the declared Linux CPU target, with artifact identities, regressions and limitations linked to the work task.
- [ ] #2 Review exact source/patch/build-script correspondence, dependency source obligations, notices and applicable code/data/model license expressions; resolve blockers or explicitly retain them as open work.
- [ ] #3 Record a maintainer-facing readiness decision and remaining owner/platform conditions. Completing this task does not itself flip executable release flags, publish a binary or certify untested platforms.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Reconcile pinned OpenSfM source, runtime assets, third-party rights and local-only restrictions against actual evidence; do not infer owner or legal approval.

Trace OpenSfM vocabulary and sensor database introductions and contributor records; distinguish evidence of authorship from rights in underlying data.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-28 interim research-only evidence and unresolved source/license blockers are recorded in research/open-components-license-review.md; the relevant owner-dispatched native build/fresh retest/limited audit passed, but temporary outputs were removed. No production artifact, comprehensive dependency or source audit, license approval or release decision follows. Prerequisites and acceptance criteria remain unchecked.

2026-10-29: Local research source archives and exact patched tree/asset hashes verified; research audit now checks package identity and critical runtime declarations. Real-package validation of the new audit requires owner dispatch; rights, dependency and ABI review remain open.

2026-10-29: owner-dispatched research run 40848319389 selected all at 7f0e5c5 and passed both local-only builds, installed tests, fresh retests and strengthened audits; outputs were discarded. Production, complete source/notices, rights and ABI review remain open.

Doc-12 consolidates exact OpenSfM local-only source/asset/grant and vmem blockers and build evidence. Rights and actual dependency graph remain unresolved; no distribution approval.

Traced 10,000/64-word vocabulary introduction and rename commits and investigated vmem history, exact sdist file matches and psutil similarity; recorded evidence and unresolved training-data and license questions in research/open-components-license-review.md. Criteria and gates remain open.

Pinned SQLite has 7523 rows: all 3708 lowercased OpenSfM JSON entries match exactly, and 3814 of 3815 added keys and values match historical AliceVision cameraSensors.db b369311; latter contains source fields naming multiple websites and user contributions. Later DroneDB merge script is consistent with this composition but postdates SQLite. Vocabulary training corpus remains unidentified. Record and caveats in research/open-components-license-review.md; rights remain open.

Run 40973960114 completed one Seneca fast-orthophoto scenario after verified vocabularies and SQLite were deleted from the disposable installed prefix; JSON fallback confirmed. No modified package or corresponding-source archive built; modes requiring the vocabularies, cameras outside JSON and source/data rights remain open. See research/odm-fast-orthophoto-prototype.md.
<!-- SECTION:NOTES:END -->
