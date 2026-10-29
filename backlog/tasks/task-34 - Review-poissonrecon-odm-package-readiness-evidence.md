---
id: TASK-34
title: Review poissonrecon-odm package-readiness evidence
status: In Progress
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-29 11:24'
labels:
  - packaging
  - review
  - poissonrecon-odm
milestone: m-5
dependencies:
  - TASK-7
type: task
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Independently review the deliverables produced by TASK-7 for the poissonrecon-odm milestone. This task verifies evidence and unresolved restrictions rather than duplicating recipe implementation. Review the actual ODM fork/meshing changes rather than assuming a generic PoissonRecon build is interchangeable. Human release approval, Prefix authorization and actual upload remain separate owner actions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Review actual installed-prefix functional/relocation and dependency-audit evidence for the declared Linux CPU target, with artifact identities, regressions and limitations linked to the work task.
- [ ] #2 Review exact source/patch/build-script correspondence, dependency source obligations, notices and applicable code/data/model license expressions; resolve blockers or explicitly retain them as open work.
- [ ] #3 Record a maintainer-facing readiness decision and remaining owner/platform conditions. Completing this task does not itself flip executable release flags, publish a binary or certify untested platforms.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Inventory pinned Poisson source, notice remediation and native artifact evidence; distinguish source and binary obligations and keep pending decisions open.

Capture bounded actual fresh-test dependency evidence for the verified native artifacts; inspect available matching dependency notices and record limitations, preserving all owner gates.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-28 interim evidence triage: research/component-readiness-review.md records run IDs, artifact identities, source evidence and limitations. Per-recipe files match the historical native run but shared scripts changed; actual retained artifact/source inspection, current-commit native evidence as appropriate, dependency notices and qualified release review remain open. This is not approval and prerequisites and acceptance criteria remain unchecked.

2026-10-29: local batch review verified pinned archive bytes, extracted declared notice inputs and checked deterministic temporary source bundles and every manifest entry. Current-commit local native build was blocked by conda-forge repodata EOF; owner-dispatched batch validation and artifact review remain necessary. See research/component-readiness-review.md for component-specific evidence and limitations. Release gates remain false.

2026-10-29: native batch run 40844694283 at 2cc2861 and read-only artifact inspection 40846497463 passed build, installed and fresh retests, audit and source-manifest verification. Exact package/source hashes, ELF needs and bounded limitations are recorded in research/component-readiness-review.md. Legal/source completeness, ABI and owner decisions remain open; no release gates changed.

Decision matrix in doc-12 cross-references IJG source notice remediation, successful owner native run 40855859214 and unresolved archive/notice/dependency rights and security review; no gate changed.

Read-only run https://github.com/Archont561/ODM-conda/actions/runs/40865060880 reverified ZIPs, passed fresh dem2mesh and Poisson retests, and logged conda-forge test-solve rows plus separately downloaded exact-name selected dependency metadata and regular notice hashes. Details and limitations: research/component-readiness-review.md. Solver bytes not hash-correlated; build/host, release closure, security, legal and source delivery remain open.
<!-- SECTION:NOTES:END -->
