---
id: TASK-15
title: Configure and prove the new repository publisher
status: Done
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-27 14:01'
labels:
  - release
  - maintainer
dependencies:
  - TASK-3
  - TASK-2
  - TASK-24
  - TASK-27
priority: high
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Repository owner action, not completed by the scaffold. Create or configure Archont561/ODM-conda, protect the prefix GitHub Environment, and add an OIDC Repository Access entry to the EXISTING archont561/archont561 Prefix channel for release.yml and environment prefix. Keep the existing CloudCompare publisher unchanged. Do not store a long-lived all-channel token.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The new repository/workflow/environment identity is authorized with narrow Read/write access.
- [x] #2 The release source URL resolves before a binary is published; the binary checksum and attestation match the validated artifact.
- [x] #3 A real release is intentionally approved only after technical/source/license reviews; no automatic release is tied to a work session.
<!-- AC:END -->

<!-- SECTION:NOTES:BEGIN -->
## Implementation Notes

Publisher configured and proven by a real channel publication on **2026-10-27**:
`fpcfilter-0.2-h873e7db_1.conda` (build 1 of 0.2, tag `fpcfilter-v0.2-b1` on
main HEAD `9f6ee33`) is live in the `linux-64` subdir of the existing
[`archont561/archont561`](https://prefix.dev/archont561/archont561) channel,
uploaded via OIDC with a Sigstore attestation. The CloudCompare publisher was
not modified; no long-lived token exists.

Evidence:

- **Green run:** [40515263476](https://github.com/Archont561/ODM-conda/actions/runs/40515263476)
  — build job `122227456507` ✓ (guard, build, fresh-container retest, audit,
  staging) and publish job `122227824888` ✓ (OIDC + attestation upload, binary
  attached to the Release). All steps in the required order.
- **Release:** <https://github.com/Archont561/ODM-conda/releases/tag/fpcfilter-v0.2-b1>
  — 4 assets: `source-fpcfilter-0.2-b1.tar.gz` (551,633 B), `audit.json`,
  `SHA256SUMS`, `fpcfilter-0.2-h873e7db_1.conda` (231,522 B).
- **Channel record (repodata):** sha256
  `8d3949bf9fdb570e30afbcd91174ee5f80e9b8cd06525a26899642bc5ed1e679`,
  `attestations_sha256`
  `d168ed89fb6eea9e7bb97849cff669103b4e2bd0eb2c9baffd8023d2660f179b`,
  size 231,522 B (matches the Release asset byte-for-byte in size), license
  `GPL-3.0-only AND BSD-2-Clause AND MIT`, deps exactly as predicted in
  components.json.

Acceptance criteria:

- **#1** — prefix.dev Repository Access entry for owner `Archont561` / repo
  `ODM-conda` / workflow `release.yml` / environment `prefix` on channel
  `archont561/archont561`, authorized by the project owner on 2026-10-27;
  write access proven empirically by the successful upload. The GitHub
  Environment `prefix` exists without plan-supported protection rules
  (doc-7's conditional guidance); the approval gate is the manual Release +
  committed gates, not environment protection.
- **#2** — the source asset was uploaded before the binary (enforced step
  order in the publish job, both steps green); the publish job re-verified
  `SHA256SUMS --strict` before uploading, and prefix.dev's repodata hash is
  computed from the received bytes. The agent sandbox could not re-hash the
  attached asset locally (GitHub asset CDN blocked); hash identity rests on
  the CI strict check plus the repodata/asset size match.
- **#3** — release approved intentionally: owner approved patch/license/build 1
  (TASK-2, doc-10, PR #5 merged to main), the tag was placed manually on that
  exact HEAD, and the Release was created manually with the compliance notes.
  Nothing ties a release to a work session.

**Incident record (release recreation).** The first three attempts (runs
`40485231900`, `40488765642`, `40489592807`, 2026-10-27 08:08–10:35 UTC)
passed the build stage but failed at the upload POST with
`authentication failed (HTTP 403)` — OIDC minting succeeded every time (the
identity matched), but the minted token was denied channel write access. Root
cause was the Repository Access entry's scope on prefix.dev (fixed by the
owner between 10:35 and 13:48 UTC); see doc-7 "OIDC failure signatures".
While failed, the Release and the remote tag were deleted; a UI re-run of the
old run then failed at the build stage because the guard requires tag ==
HEAD. Recovery: re-pushed the same annotated tag (`2e4acea` → commit
`9f6ee33`) and recreated the Release with identical compliance notes, which
triggered run `40515263476` — green on the first attempt.

**Dependency note.** Formal dependencies TASK-3 (in progress), TASK-24 and
TASK-27 (to do) remain open — they track dem2points obligations and the
fpcfilter sprint paperwork. The publisher proof itself is component-scoped
and was satisfied by the real fpcfilter publication; TASK-25/26 formal
verification/review records can cite the green run above.
<!-- SECTION:NOTES:END -->
