---
id: TASK-56
title: Resolve missing IJG terms in PoissonRecon source distribution
status: In Progress
assignee: []
created_date: '2026-10-29 10:00'
updated_date: '2026-10-29 10:00'
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
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Hash-verified Poisson archive contains 59 JPEG files and no JPEG README. A third-party IJG 6b mirror at 3d8e50d2fb0d5555d5236570a75f575317b2dc8e has README SHA256 4cf9c190f184019b61c36bcc49d4a24ffeb2a838c6f1690d6c4db14cfb2d0478; 49 files match the mirror, 8 differ, 2 lack same-named counterparts. The source bundle embeds the entire original archive. Applicability, complete change documentation and source/binary notice handling remain unconfirmed; no release gate changed. See research/poissonrecon-readiness-review.md.
<!-- SECTION:NOTES:END -->
