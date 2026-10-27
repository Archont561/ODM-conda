---
id: TASK-22
title: Validate dem2points package and regenerate review inputs
status: Done
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-27 15:44'
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
- [x] #1 Build the selected immutable source/recipe and test the installed prefix, relocation, functional fixtures and declared dynamic dependencies; preserve explicit unsupported modes/platform limits.
- [x] #2 Regenerate artifact audits and exact corresponding-source/staging inputs, recording hashes and any modified-source notices without committing generated binaries, archives or reports.
- [x] #3 Keep code/source/license/native-validation acknowledgements false until their independent maintainer review; for FPCFilter, TASK-2's accepted regression outcome is included before claiming validation.
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

2026-10-27: native validation completed through the repository build workflow. The owner dispatched `build.yml` (component=dem2points) from the GitHub UI after the agent token's dispatch attempt was again rejected (403 `Resource not accessible by integration` — missing actions scope). Run [40532334352](https://github.com/Archont561/ODM-conda/actions/runs/40532334352) on main HEAD `79841ca`, job `122288238934`, every step green (~26 s wall clock).

AC #1: built from the pinned immutable source (rattler-build verifies the codeload archive sha256 `b5d87bca…` as a condition of the build) on a GitHub-hosted ubuntu-24.04 runner — Ubuntu 24.04.5 LTS, image 20261012.334.1, runner 2.338.0; the test platform self-reported `__glibc 2.39`, `__linux 6.17.0`, archspec `zen2`. That is the actual tested host, not a minimum-glibc certification: the package's `__glibc>=2.28` floor is declared by the sysroot-2.28 toolchain (gcc/gxx 14.4.0, cmake 3.31.8, ninja 1.13.2), not tested on 2.28. CMake found GDAL 3.11.5; artifact `dem2points-0.0.0.dev20220721-h873e7db_0.conda` (54.58 KiB; 18 files: `bin/dem2points` 39.20 KiB, the three installed notices, `SOURCE.txt`, `functional_test.py`, `upstream.json`, metadata). Relocation exercised: build rpath removed and the binary relinked. Link report matches declarations: libc (system), libgcc_s.so.1 (libgcc), libgdal.so.37.3.11.5 (libgdal-core), libstdc++.so.6.0.36 (libstdcxx); finalized run deps `__glibc>=2.28,<3.0.a0`, `libgcc>=14`, `libstdcxx>=14`, `libgdal-core>=3.11,<3.12` run-export-pinned to `>=3.11.5,<3.12.0a0`. Installed-prefix functional tests (linkage + generated DEM data → PLY) passed twice in fresh environments: at build time and in the isolated `pixi run test` retest (`rattler-build test`, conda-forge strict priority, libgdal-core 3.11.5 h4f65170_7) — both printed "PASS: dem2points installed-prefix linkage and generated-data functional tests / ✔ all tests passed!". Minor observation: CMake reported `BUILD_TESTING` as unused (the upstream CMakeLists does not consume it) — benign.

AC #2: audit passed → `reports/audit-dem2points.json` ("PASS: dem2points artifact audit"). Corresponding-source bundle regenerated in the same run: `source-dem2points-0.0.0.dev20220721-b0.tar.gz` SHA256 `39dc218344274cd30e992b157cd9e68fcf4df45d4c9553506bbb71f30431d17f` — different from the 2026-10-26 local regeneration (`1db98fa1…`) because the bundle embeds the current repository packaging files at `79841ca`; the upstream archive portion is unchanged and hash-verified. Outputs were saved as CI artifact `odm-components-linux-64` (ID 12746897342, 3 files, 261,007 B, zip digest sha256 `354639e29a2ef28a4ddacb1ca3f4d6f55978710bc18b8eee612d4e70f5d18f16`, retained until 2026-11-10, https://github.com/Archont561/ODM-conda/actions/runs/40532334352/artifacts/12746897342); nothing was committed to git, nothing published, and dem2points carries no patches so there is no modified-source notice.

AC #3: all four dem2points release acknowledgements remain false pending the independent review (TASK-23) and the owner's decision. No historical binaries were reused and no doc-8 historical results were relied on as current evidence.
<!-- SECTION:NOTES:END -->
