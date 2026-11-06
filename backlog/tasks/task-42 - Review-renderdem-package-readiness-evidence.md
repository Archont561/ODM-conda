---
id: TASK-42
title: Review renderdem package-readiness evidence
status: In Progress
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-29 11:03'
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
- [x] #2 Review exact source/patch/build-script correspondence, dependency source obligations, notices and applicable code/data/model license expressions; resolve blockers or explicitly retain them as open work.
- [x] #3 Record a maintainer-facing readiness decision and remaining owner/platform conditions. Completing this task does not itself flip executable release flags, publish a binary or certify untested platforms.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Review pinned RenderDEM sources and corresponding-source staging against the actual recipe and historical native evidence; document specific unresolved rights, dependencies and current-release validation steps without changing release gates.

Complete a decision-ready RenderDEM license review for the pinned tree and historical native artifact: inspect actual source, direct notices and dependency evidence, identify precise remaining owner/legal and source-offer decisions without enabling gates.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-28 interim evidence triage: research/component-readiness-review.md records run IDs, artifact identities, source evidence and limitations. Per-recipe files match the historical native run but shared scripts changed; actual retained artifact/source inspection, current-commit native evidence as appropriate, dependency notices and qualified release review remain open. This is not approval and prerequisites and acceptance criteria remain unchecked.

2026-10-29: local batch review verified pinned archive bytes, extracted declared notice inputs and checked deterministic temporary source bundles and every manifest entry. Current-commit local native build was blocked by conda-forge repodata EOF; owner-dispatched batch validation and artifact review remain necessary. See research/component-readiness-review.md for component-specific evidence and limitations. Release gates remain false.

2026-10-29: native batch run 40844694283 at 2cc2861 and read-only artifact inspection 40846497463 passed build, installed and fresh retests, audit and source-manifest verification. Exact package/source hashes, ELF needs and bounded limitations are recorded in research/component-readiness-review.md. Legal/source completeness, ABI and owner decisions remain open; no release gates changed.

Re-fetched and SHA256-verified RenderDEM commit 93502f2. Inventoried all 11 direct-source files, root AGPLv3 statement, vendored cxxopts MIT notice and CMake link inputs. The package carries these notices, but direct source findings do not establish provenance, exact dependency closure, grant/version decision or complete corresponding-source offer. Owner/qualified review and release gates remain open; see research/component-readiness-review.md.

Cross-package decision record doc-12 consolidates RenderDEM direct-source findings, candidate grant, actual runtime/source obligations and historical validation; owner/qualified decisions remain open.

Read-only inspection https://github.com/Archont561/ODM-conda/actions/runs/40861743072 reverified the historical multi-component ZIP and RenderDEM build 0 package SHA256 dc33a1fb2de90eabc0ee241f573bd14f09d4d3481f0fb813bd90f792b4f8b895; source bundle SHA256 e1f0e18a36c70c9633fcf42b199b3ecbf2bc0aefe2846ea8cc213f8c17182172, all 232 manifest entries, and exact bytes of both declared upstream notices in package payload and info metadata. Current audit and additional fresh isolated retest passed. Package ELF needs libpdalcpp.so.20 and RPATH $ORIGIN/../lib; dependency constraints do not identify the full resolved closure. No source-rights, owner or release approval inferred.

Follow-up https://github.com/Archont561/ODM-conda/actions/runs/40862253176 independently retested historical RenderDEM build 0 and inspected exact-name matching fresh-solve package metadata for PDAL 2.10.2, GDAL 3.13.3 and libgomp 16.2.0. See research/component-readiness-review.md for package and license-text hashes, bounded provenance, and remaining source/owner decisions. Future release solve and full transitive review remain unverified.

2026-11-04: read-only run 41853735397 compared 352 packaging files to the recorded Git commit, verified the pinned upstream archive and exact three notice bytes in payload and metadata, and recorded selected records from a fresh 66-package runtime solve. The review and explicit remaining source, rights, dependency, validation and owner decisions are in research/renderdem-release-gate-review.md. No release gate has changed; actual release-commit evidence and relocation coverage remain open.

2026-11-04: hosted run 41856233714 tested generated PLY, LAS and compressed LAZ with the exact build-1 package and a separate PDAL CLI, then repeated in a fresh locked prefix at a different path; 196 installed identities and hashes matched. The lightweight lock/inventory artifact expires 2026-11-18 and cannot replay without the discarded local package channel. This is not a moved-prefix, full-stack, rights or release-approval test. See research/renderdem-release-gate-review.md.

2026-11-04: traced root LICENSE to the initial RenderDEM commit and README AGPLv3 statement to a later commit; recorded chronology without treating it as definitive rights or version approval. Vendored cxxopts 3.1.1 matches upstream tag v3.1.1 except for one added noexcept and was unchanged from its RenderDEM import. See research/renderdem-release-gate-review.md; provenance and owner decisions remain open.

2026-11-04: hosted reconstruction run 41862738817 verified and staged 352 packaging files and the upstream source archive from the owner-dispatched source bundle, substituted a local source path in the recipe, built, tested, fresh-retested and audited. Rebuilt package SHA256 027dbe9ed25b9fd106a0ed94932ff047ca7a8a0f9224682652ac97c5c96dbb4e differs from original a681202611aa3fa25281055825b75a89e1a256260a954ce69bcd5393a834d94c; dependency solves remained online and byte reproducibility was not established. The technical evidence is bounded; source rights, legal completeness and owner decisions remain open. See research/renderdem-release-gate-review.md.
<!-- SECTION:NOTES:END -->
