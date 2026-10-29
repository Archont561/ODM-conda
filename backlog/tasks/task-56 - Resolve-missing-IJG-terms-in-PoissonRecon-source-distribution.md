---
id: TASK-56
title: Resolve missing IJG terms in PoissonRecon source distribution
status: In Progress
assignee: []
created_date: '2026-10-29 10:00'
updated_date: '2026-10-29 10:38'
labels:
  - poissonrecon-odm
dependencies: []
priority: high
type: bug
ordinal: 56000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The exact pinned PoissonRecon archive includes JPEG files referring to an accompanying IJG README which is absent. Source bundles include this full archive. Establish provenance and applicable terms, retain the proper unaltered README, document modifications, and validate both exact source and binary obligations before release.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Establish IJG version/provenance and differences, including the terms that apply to the bundled files.
- [ ] #2 Provide and verify a compliant source distribution with the required unaltered IJG terms and documented changes.
- [ ] #3 Determine binary notice applicability and ship verified notices if required; rerun native and source-bundle checks before owner review.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Verify pinned Poisson archive and compare its IJG subset against an identifiable 6b source, document missing terms and modifications, then establish authoritative provenance and compliant source/binary notices before release.

Compare pinned vendored JPEG files with an immutable IJG 6b reference; retain its unaltered README and full comparison as source materials; include a conservative verified notice in a bumped, non-published package, and revalidate without asserting legal clearance.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Hash-verified Poisson archive contains 59 JPEG files and no JPEG README. A third-party IJG 6b mirror at 3d8e50d2fb0d5555d5236570a75f575317b2dc8e has README SHA256 4cf9c190f184019b61c36bcc49d4a24ffeb2a838c6f1690d6c4db14cfb2d0478; 49 files match the mirror, 8 differ, 2 lack same-named counterparts. The source bundle embeds the entire original archive. Applicability, complete change documentation and source/binary notice handling remain unconfirmed; no release gate changed. See research/poissonrecon-readiness-review.md.

Prepared Poisson build 3: restored the byte-identified IJG 6b README with a hash-pinned patch; package notice list includes it; artifact audit requires matching payload and conda metadata bytes. Both mirrors have the same README SHA256 4cf9c190f184019b61c36bcc49d4a24ffeb2a838c6f1690d6c4db14cfb2d0478. Full textual comparison to the first pinned mirror and standalone README are included in packaging sources. Both patches applied cleanly to the pinned source; research-only dirty-tree source bundle verified 240 manifest hashes including both documents and the patch. Local rattler build 3 applied both patches but failed at compiler dependency solve: conda-forge repodata EOF; no package, installed test or artifact audit ran. Need owner-dispatched native build, fresh retest and artifact/source audit; provenance, distribution sufficiency, exact dependency notices and owner/qualified approval remain open. No release gate changed.

Owner-dispatched native workflow https://github.com/Archont561/ODM-conda/actions/runs/40855859214 at ec83f085461b30c99e3b2f5d6f362c92da8c103d passed build and packaged tests, fresh retests, artifact audit and source bundling; non-published artifact ID 12889646994, GitHub-reported ZIP SHA256 44c7723e16c9d1bc40e9b1634578836657c02ff4eebf6d13d363146f850903bf. GitHub step statuses are reported, but artifact contents and exact component selection have not been independently inspected. Provenance, source rights/completeness, dependency notice review and owner/qualified approval remain open; no release gates changed.

Temporary read-only inspection https://github.com/Archont561/ODM-conda/actions/runs/40859056365 verified ZIP SHA256 44c7723e16c9d1bc40e9b1634578836657c02ff4eebf6d13d363146f850903bf and exact Poisson-only membership. Package SHA256 1e61c71dd24d73802d90b2db89057db1a612548949c9952767b2f765df4e93ab; source bundle SHA256 817e8a5cac0e08a8f5050970dd2b34478b4475391db57daa17207488bc8d0c84; 240 manifest entries verified including README and comparison, with clean build commit ec83f085. Reaudit passed with exact IJG notice bytes in payload and metadata; RPATH $ORIGIN/../lib and ELF needs libpng16.so.16 and libjpeg.so.8. Raw linker map unavailable; metadata constraints are not resolved dependency inventory. Legal/source/provenance decisions remain open; no release gates changed.
<!-- SECTION:NOTES:END -->
