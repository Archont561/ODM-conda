---
id: TASK-42
title: Review renderdem package-readiness evidence
status: In Progress
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-29 10:00'
labels:
  - packaging
  - review
  - renderdem
milestone: m-9
dependencies:
  - TASK-11
type: task
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Independently review the deliverables produced by TASK-11 for the renderdem milestone. This task verifies evidence and unresolved restrictions rather than duplicating recipe implementation. Review deterministic rendering output, GDAL/runtime ABI and source/notice coverage from the actual selected commit. Human release approval, Prefix authorization and actual upload remain separate owner actions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Review actual installed-prefix functional/relocation and dependency-audit evidence for the declared Linux CPU target, with artifact identities, regressions and limitations linked to the work task.
- [ ] #2 Review exact source/patch/build-script correspondence, dependency source obligations, notices and applicable code/data/model license expressions; resolve blockers or explicitly retain them as open work.
- [ ] #3 Record a maintainer-facing readiness decision and remaining owner/platform conditions. Completing this task does not itself flip executable release flags, publish a binary or certify untested platforms.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Review pinned RenderDEM sources and corresponding-source staging against the actual recipe and historical native evidence; document specific unresolved rights, dependencies and current-release validation steps without changing release gates.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-28 interim evidence triage: research/component-readiness-review.md records run IDs, artifact identities, source evidence and limitations. Per-recipe files match the historical native run but shared scripts changed; actual retained artifact/source inspection, current-commit native evidence as appropriate, dependency notices and qualified release review remain open. This is not approval and prerequisites and acceptance criteria remain unchecked.

2026-10-29: local batch review verified pinned archive bytes, extracted declared notice inputs and checked deterministic temporary source bundles and every manifest entry. Current-commit local native build was blocked by conda-forge repodata EOF; owner-dispatched batch validation and artifact review remain necessary. See research/component-readiness-review.md for component-specific evidence and limitations. Release gates remain false.

2026-10-29: native batch run 40844694283 at 2cc2861 and read-only artifact inspection 40846497463 passed build, installed and fresh retests, audit and source-manifest verification. Exact package/source hashes, ELF needs and bounded limitations are recorded in research/component-readiness-review.md. Legal/source completeness, ABI and owner decisions remain open; no release gates changed.

Re-fetched and SHA256-verified RenderDEM commit 93502f2. Inventoried all 11 direct-source files, root AGPLv3 statement, vendored cxxopts MIT notice and CMake link inputs. The package carries these notices, but direct source findings do not establish provenance, exact dependency closure, grant/version decision or complete corresponding-source offer. Owner/qualified review and release gates remain open; see research/component-readiness-review.md.
<!-- SECTION:NOTES:END -->
