---
id: TASK-22
title: Validate dem2points package and regenerate review inputs
status: In Progress
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-26 22:40'
labels:
  - packaging
  - validation
  - dem2points
milestone: m-0
dependencies:
  - TASK-1
type: task
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The dem2points recipe already exists, but historical native artifacts were intentionally cleaned. Regenerate current evidence for the initial Linux CPU package; this is validation work, not permission to publish. Recheck the GDAL-linked executable and declared runtime dependencies; report the actual tested host rather than claiming minimum-glibc certification.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Build the selected immutable source/recipe and test the installed prefix, relocation, functional fixtures and declared dynamic dependencies; preserve explicit unsupported modes/platform limits.
- [ ] #2 Regenerate artifact audits and exact corresponding-source/staging inputs, recording hashes and any modified-source notices without committing generated binaries, archives or reports.
- [ ] #3 Keep code/source/license/native-validation acknowledgements false until their independent maintainer review; for FPCFilter, TASK-2's accepted regression outcome is included before claiming validation.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Regenerate the hash-verified dem2points source/staging bundle from the immutable commit, inspect/review exact source inputs, and attempt the prescribed native build, installed functional tests, audit and relocation checks. Record exact host/tool availability and block any acceptance criterion requiring native tooling that cannot be obtained; never reuse historical binaries as current evidence. Keep all release acknowledgements false.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-10-26: regenerated source staging from the immutable dem2points commit. The downloaded codeload archive SHA256 matches the manifest (b5d87bcafd52fd4c52f5c8828086f2ea34338742ae293cbd21bde1fd55b9fa67); generated corresponding-source bundle SHA256 is 9271c67109881484f45c09f07e4fd73026d1bee5e580dfb930dc7f66da8373d6 and repeated generation was byte-identical. The bundle contains the exact upstream archive and current packaging recipe/scripts/tests/locks; generated archives remain ignored/uncommitted. Attempted `python scripts/build.py --component dem2points`; blocked because rattler-build/Pixi are absent. This host also lacks CMake, Ninja, GDAL development headers/tools and patchelf, so no fresh package build, installed-prefix/relocation/functional test, artifact audit or dynamic-dependency report could be produced. Historical results in backlog doc-8 are not reused as current evidence. No acknowledgements were changed; AC #2 is partially satisfied for regenerated source staging only, while AC #1 and the artifact/audit parts of AC #2 remain blocked.

2026-10-26 follow-up after restoring sandbox/developer-linux-64: the default and agent-tools environments restored with manifest verification (0 failures); `pixi install --frozen --offline` was a no-op and `pixi run check` passed (50 Python tests, 4 Bun tests, static checks and both recipe renders). Retried the native dem2points build with restored rattler-build 0.68.0. It fetched the pinned codeload source successfully and rendered the recipe, then dependency solving failed after three retries fetching conda-forge repodata at https://conda.anaconda.org/conda-forge/noarch/repodata_shards.msgpack.zst (unexpected EOF in this restricted network). No .conda artifact was produced, so installed-prefix tests, relocation checks, dynamic dependency audit and package audit remain blocked; prior historical binaries are not used. Regenerated the current corresponding-source bundle including the new pixi-sandbox configuration/workflows/bootstrap; source archive checksum still matches the manifest and the bundle SHA256 was reproducible: 2abee9a46391738ce125ef6b5890a0028ef1bc2c26fcecca1cc28c2d57091b67. AC #2 source staging is current; native artifact/audit checks remain incomplete. No release acknowledgements changed.

Follow-up commands `pixi run test --component dem2points` and `pixi run audit --component dem2points` were attempted; each correctly refused because output/linux-64 contains zero dem2points artifacts. These are blocked by the conda-forge dependency-solve failure above, not recorded as passing package checks.

Final source-bundle refresh after the task note itself changed: rattler-builds cached upstream source archive was independently SHA256-checked against the manifest before seeding the local source cache; `pixi run sources --component dem2points` then succeeded twice byte-identically. Current bundle SHA256: 1db98fa1b0e02f5bdd5800f1f42d97f0dd6a28d204ab19f5674437b06694c245. The initial Pixi-Python codeload fetch had a local CA verification error; using the already hash-verified archive avoided bypassing TLS validation.

Attempted the repository native workflow (`build.yml`, dem2points) as the network-enabled build path after local conda-forge resolution failed. GitHub rejected the workflow_dispatch request with HTTP 403 `Resource not accessible by integration`; no run was queued. A GitHub connection with Actions workflow-dispatch permission is required to use that runner. No token was requested or stored.
<!-- SECTION:NOTES:END -->
