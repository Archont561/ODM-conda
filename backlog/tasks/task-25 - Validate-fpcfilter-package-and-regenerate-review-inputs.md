---
id: TASK-25
title: Validate fpcfilter package and regenerate review inputs
status: Done
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-27 14:31'
labels:
  - packaging
  - validation
  - fpcfilter
milestone: m-1
dependencies:
  - TASK-2
type: task
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The fpcfilter recipe already exists, but historical native artifacts were intentionally cleaned. Regenerate current evidence for the initial Linux CPU package; this is validation work, not permission to publish. Include TASK-2's no-normals outcome, normals sampling and pass-through regressions; any retained limitation must be explicit and release acknowledgements re-reviewed after a patch.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Build the selected immutable source/recipe and test the installed prefix, relocation, functional fixtures and declared dynamic dependencies; preserve explicit unsupported modes/platform limits.
- [x] #2 Regenerate artifact audits and exact corresponding-source/staging inputs, recording hashes and any modified-source notices without committing generated binaries, archives or reports.
- [x] #3 Keep code/source/license/native-validation acknowledgements false until their independent maintainer review; for FPCFilter, TASK-2's accepted regression outcome is included before claiming validation.
<!-- AC:END -->

<!-- SECTION:NOTES:BEGIN -->
## Implementation Notes

Validation evidence was regenerated in CI rather than locally (the agent sandbox
has no pixi; the CI environment is pinned and better controlled). The
definitive validation is the release run; every build from the pinned source
was green:

- **Run [40515263476](https://github.com/Archont561/ODM-conda/actions/runs/40515263476)**
  (2026-10-27): build job `122227456507` ✓ — release guard/check, rattler-build
  from pinned upstream commit `6e0c1c0113939823b2ff3c2eef4d5907e7f5db6b` plus
  local patch 0001 (hashes in `recipes/components.json`), fresh-container
  installed-prefix retests (ASCII pass-through, TASK-2's no-normals regression,
  normals-bearing binary PLY sampling, linkage), relocation, dependency audit →
  `audit.json`, deterministic corresponding-source staging; publish job
  `122227824888` ✓ (OIDC + Sigstore attestation).
- The earlier runs `40485231900`, `40488765642`, `40489592807` also passed
  their build stages; their only failures were the publish-side upload 403s
  (prefix.dev Repository Access scope — see TASK-15's incident record).

AC #2: generated outputs live as CI artifacts and GitHub Release assets —
nothing binary/generated is committed to git: `source-fpcfilter-0.2-b1.tar.gz`
(551,633 B), `SHA256SUMS` (271 B), `audit.json` (614 B), and the published
`fpcfilter-0.2-h873e7db_1.conda` (231,522 B; channel repodata sha256
`8d3949bf9fdb570e30afbcd91174ee5f80e9b8cd06525a26899642bc5ed1e679`,
attestations_sha256
`d168ed89fb6eea9e7bb97849cff669103b4e2bd0eb2c9baffd8023d2660f179b`). The
modified-source notice (patch 0001) is carried in the bundle and package
metadata, owner-approved via doc-10/TASK-2.

AC #3: acknowledgements stayed `false` throughout validation and were flipped
only after the owner's independent review (doc-10, TASK-2, merged as PR #5);
TASK-2's accepted no-normals regression outcome is part of the tested matrix.

Retained limitations (doc-10 §8), restated for the review (TASK-26): Linux
x86-64 CPU target only; no ODM end-to-end validation; shared voxel-map reads
out of scope; pre-existing `_openmp_mutex` over-dependency warning.
<!-- SECTION:NOTES:END -->
