---
id: TASK-26
title: Review fpcfilter package-readiness evidence
status: Done
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-27 14:31'
labels:
  - packaging
  - review
  - fpcfilter
milestone: m-1
dependencies:
  - TASK-25
  - TASK-3
type: task
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Independently review the deliverables produced by TASK-25 for the fpcfilter milestone. This task verifies evidence and unresolved restrictions rather than duplicating recipe implementation. Include TASK-2's no-normals outcome, normals sampling and pass-through regressions; any retained limitation must be explicit and release acknowledgements re-reviewed after a patch. Human release approval, Prefix authorization and actual upload remain separate owner actions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Review actual installed-prefix functional/relocation and dependency-audit evidence for the declared Linux CPU target, with artifact identities, regressions and limitations linked to the work task.
- [x] #2 Review exact source/patch/build-script correspondence, dependency source obligations, notices and applicable code/data/model license expressions; resolve blockers or explicitly retain them as open work.
- [x] #3 Record a maintainer-facing readiness decision and remaining owner/platform conditions. Completing this task does not itself flip executable release flags, publish a binary or certify untested platforms.
<!-- AC:END -->

<!-- SECTION:NOTES:BEGIN -->
## Implementation Notes

Independent review of the TASK-25 deliverables (evidence review; no recipe work
duplicated). Evidence base: doc-10 review packet, CI run
[40515263476](https://github.com/Archont561/ODM-conda/actions/runs/40515263476),
the live [Release `fpcfilter-v0.2-b1`](https://github.com/Archont561/ODM-conda/releases/tag/fpcfilter-v0.2-b1),
and the [`archont561/archont561`](https://prefix.dev/archont561/archont561)
linux-64 repodata record.

AC #1: installed-prefix functional/relocation/dependency-audit evidence checked
against the build job (`122227456507`): fresh-container retests including
TASK-2's no-normals regression, normals-bearing binary PLY sampling, ASCII
pass-through and linkage; relocation; dependency audit (`audit.json`).
Artifact identities linked to TASK-25: published `fpcfilter-0.2-h873e7db_1.conda`,
repodata sha256
`8d3949bf9fdb570e30afbcd91174ee5f80e9b8cd06525a26899642bc5ed1e679`,
attestations_sha256
`d168ed89fb6eea9e7bb97849cff669103b4e2bd0eb2c9baffd8023d2660f179b`, size
231,522 B matching the Release asset. Declared target: linux-64 only; doc-10 §8
limitations restated in TASK-25's notes apply unchanged.

AC #2: correspondence verified — tag `fpcfilter-v0.2-b1` == `main` HEAD at
publication (`9f6ee33`), enforced by the release guard ("Release gates passed
… policy check, not legal certification."); source = pinned upstream commit
`6e0c1c0113939823b2ff3c2eef4d5907e7f5db6b` + patch 0001 with hashes recorded
in `recipes/components.json`; the corresponding-source bundle was uploaded
before the binary and is durably available as a Release asset. Shipped runtime
dependency graph from repodata: `libgomp>=14`, `libgcc>=14`, `libstdcxx>=14`,
`_openmp_mutex>=4.5`, `__glibc>=2.28,<3.0.a0` — all conda-forge packages,
dynamically linked and not copied into this package, so their
source/redistribution conditions ride on their own conda-forge packaging.
Bundled vendored notices (MIT cxxopts/json, BSD-2 nanoflann) are preserved in
the corresponding-source archive and installed under `share/licenses/`.
License expression `GPL-3.0-only AND BSD-2-Clause AND MIT` is owner-confirmed
(TASK-2, doc-10 §5–6).

AC #3: readiness decision — recorded and already executed by the owner:
fpcfilter 0.2 build 1 was approved (2026-10-27) and published to the channel
via OIDC with a Sigstore attestation (TASK-15). Remaining owner/platform
conditions: none for linux-64; no other platform is built or certified by this
review, and closing this task flips no release flags by itself.

Explicitly retained as open work (AC #2 permits retention): the dem2points
portion of TASK-3 — expression owner-confirmed as `GPL-3.0-only` (2026-10-27),
but binary correspondence and dependency source obligations await the
dem2points path (TASK-22/23/24). Closing TASK-26 while TASK-3 is In Progress is
justified because every fpcfilter-side item of TASK-3 is resolved and the
remaining items are dem2points-scoped, outside this fpcfilter-milestone review.
<!-- SECTION:NOTES:END -->
