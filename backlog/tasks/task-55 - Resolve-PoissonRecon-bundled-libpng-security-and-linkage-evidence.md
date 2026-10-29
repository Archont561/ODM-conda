---
id: TASK-55
title: Resolve PoissonRecon bundled libpng security and linkage evidence
status: In Progress
assignee: []
created_date: '2026-10-28 22:40'
updated_date: '2026-10-29 07:51'
labels: []
dependencies: []
references:
  - 'https://github.com/advisories/GHSA-mmpj-hr4h-5g99'
  - 'https://github.com/advisories/GHSA-m968-rq7m-646j'
priority: high
type: bug
ordinal: 55000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The pinned upstream source builds libpng 1.2.29 into a static archive; historical native output has not been inspected for its final linkage or reachable PNG paths. Historical advisories cover the source version, but exploitability in this binary is unproven. Resolve before release; see research/poissonrecon-readiness-review.md.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Determine exact final link inputs and runtime dependencies from a current native build, with retained linker map or equivalent evidence and tests.
- [ ] #2 Eliminate or responsibly mitigate any vulnerable bundled implementation present in the executable and test the relevant input/output paths; document any non-reachability argument.
- [ ] #3 Repeat native build, fresh retest, package audit and source-bundle review; preserve release gates pending owner and security/license review.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Trace pinned PoissonRecon build and linker inputs; add a fail-closed, tested linkage guard or mitigation; document limitations and run local checks. Obtain owner native validation before closing the task; preserve release gates.

Independently fetch the exact run 40835639537 artifact in a temporary read-only CI workflow, verify immutable ZIP and source-bundle digests, audit packaged link evidence and ELF, and run a fresh isolated retest; print bounded evidence to the job log without changing release gates.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-29: a reduced FAST_COMPILE -O0 research build linked bundled libmypng.a and contained the advisory-named png_handle_pCAL, png_read_png and png_set_text_2 symbols; this is not proof about the historical/full package or exploitability. Proposed build 2 patches the Poisson target to host libpng >=1.6.59,<1.7, checks a GNU link map and packages a path-free input inventory/hash, audits ELF NEEDED, and runs gray/RGB/RGBA adapter round trips. The patched reduced build, map guard and sphere fixture passed; local pixi check and focused tests passed. Local native build applied patch but failed solving compiler packages because conda-forge repodata returned EOF; no package, fresh retest or package audit exists. Source bundle assembled from hash-verified cache for research only. Owner must dispatch build.yml on proposed commit and review actual artifact, runtime, security and license evidence. No release gates changed; all acceptance criteria remain open. See research/poissonrecon-readiness-review.md.

2026-10-29: owner-dispatched native run https://github.com/Archont561/ODM-conda/actions/runs/40835639537 passed on 3ffabd94f2b1858b662e8ec66541fe5ac05fe3d5. Full recipe build 2, link-map guard, PNG adapter smoke, installed tests, fresh retest, artifact audit and source bundling passed. Host and fresh retest solved libpng 1.6.59, libjpeg-turbo 3.2.1, libzlib 1.3.2; GNU compiler 14.4.0 and sysroot 2.28. Logs report artifact poissonrecon-odm-13.8-h873e7db_2.conda and source bundle SHA256 943f6b5e3e76b1c2a28ec80b8f1213738901aab3f2bd74dafb10029d05237eeb. GitHub artifact 12880822311 reports ZIP SHA256 cd3f7ab8b1fe3ebd3b77bd246b02af5b78035095c8c67b64336915a53ccca7d1; artifact download failed EOF, so packaged evidence and bytes were not independently inspected. Link guard covers named inputs, not equivalent code or overall security. Full source, legal, security and owner release review remain open; all release gates remain false.

2026-10-29: temporary read-only inspection run https://github.com/Archont561/ODM-conda/actions/runs/40838038046 successfully downloaded artifact 12880822311, verified ZIP SHA256 cd3f7ab8b1fe3ebd3b77bd246b02af5b78035095c8c67b64336915a53ccca7d1, re-audited the package, checked all 229 source-manifest entries, and passed a fresh isolated retest. Package SHA256 0bfffd4b42c1f844ea536d3f17bd81e446f5f5600c47d06340e25a8648cb2f9c; source SHA256 943f6b5e3e76b1c2a28ec80b8f1213738901aab3f2bd74dafb10029d05237eeb; link-map SHA256 277e99846f11a1831f4289ec44d68dfbf5087127192119e922c53b34e67a89cf. Packaged named inputs list libpng.so and no libmypng.a; ELF needs libpng16.so.16; RPATH $ORIGIN/../lib. The raw linker map was not retained or independently examined, and named-input guard is not a complete security or licensing proof. Release gates remain false and TASK-55 stays open for remaining review.

2026-10-29: audit now independently rejects named static libpng archives in packaged link inventories, even alongside shared libpng; focused positive/negative tests pass. This strengthens a bounded named-input check, not map authentication or complete security evidence. See research/component-readiness-review.md.
<!-- SECTION:NOTES:END -->
