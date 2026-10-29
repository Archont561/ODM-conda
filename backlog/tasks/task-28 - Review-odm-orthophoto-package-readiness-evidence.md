---
id: TASK-28
title: Review odm-orthophoto package-readiness evidence
status: Done
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-29 20:30'
labels:
  - packaging
  - review
  - odm-orthophoto
milestone: m-2
dependencies:
  - TASK-4
type: task
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Independently review the deliverables produced by TASK-4 for the odm-orthophoto milestone. This task verifies evidence and unresolved restrictions rather than duplicating recipe implementation. Review the ODM-compatible orthophoto executable, image/geospatial library ABI, installed-prefix behavior and any exact fork patches. Human release approval, Prefix authorization and actual upload remain separate owner actions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Review actual installed-prefix functional/relocation and dependency-audit evidence for the declared Linux CPU target, with artifact identities, regressions and limitations linked to the work task.
- [x] #2 Review exact source/patch/build-script correspondence, dependency source obligations, notices and applicable code/data/model license expressions; resolve blockers or explicitly retain them as open work.
- [x] #3 Record a maintainer-facing readiness decision and remaining owner/platform conditions. Completing this task does not itself flip executable release flags, publish a binary or certify untested platforms.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Independent review of the odm-orthophoto deliverables produced by TASK-4, from the fourth owner-dispatched native run [40584231748](https://github.com/Archont561/ODM-conda/actions/runs/40584231748) (main `bef20d9`, 2026-10-27, fully green: build + packaged tests ✓, fresh-env retest ✓, audit ✓, source bundle ✓, artifact save ✓).

AC #1 evidence: artifact `odm-orthophoto-0.0.0.dev20250225-h873e7db_0.conda` (114.05 KiB) built linux-64 from pinned commit `55b66d87` (archive sha256 `a3f3410b…f5b528d2`, 26,023 B). Packaged tests ran under the build env's python 3.12 and PASSed; the fresh-environment retest (`rattler-build test --package-file`, spec `python >=3.12,<3.13`, resolved python 3.12.16, strict conda-forge priority) PASSed the installed-prefix functional fixture: generated 4×4 solid-red textured OBJ quad → `odm_orthophoto -resolution 2 -outputDepthIdx 0` → GeoTIFF IFD verified in pure Python (4×4, RGBA 8-bit, contiguous uncompressed strips, 16 pixels `(255,0,0,255)`), corner bounds `[100,200,102,202]`, linkage. The dependency audit PASSed (`reports/audit-odm-orthophoto.json`): run-dep re-pins `__glibc >=2.28,<3.0.a0`, `_openmp_mutex >=4.5`, `libgcc/libgomp/libstdcxx >=14`, `libgdal-core >=3.11.5,<3.12.0a0`, `libopencv >=4.12.0,<4.12.1.0a0`; no undeclared runtime dependencies, notices verified, no build-cache leakage — the `build.python.skip_pyc_compilation` fix (PR #14) closed the host-python `compile_pyc` leak that failed runs 40578521206/40581957902, and run 40575816771's fixture band-order bug was fixed by PR #12; the full regression history is recorded in the TASK-4 notes. Source bundle `source-odm-orthophoto-0.0.0.dev20250225-b0.tar.gz` sha256 `c02b61f6fe14cc030afe21b846dbb4d9f36f441b142a8af14eb66cc380bc0c68`. All identities preserved in CI artifact `odm-components-linux-64` (ID 12770762758, zip sha256 `9f282206…c254a3820`, retained to 2026-11-10). Limitations: GitHub ubuntu-24.04 host glibc 2.39 — the `>=2.28` floor is a sysroot-2.28 toolchain declaration, not runtime-tested on older distributions; linux-64 only; no ODM end-to-end integration (TASK-13); the fixture proves structure/pixels/linkage, not photogrammetric quality.

AC #2 correspondence: exact source/patch/build-script correspondence holds — no patches, no disabled build trees, no vendored third-party code (`src/` = Logger, OdmOrthoPhoto, main, project-original); upstream CMake dependencies (GDAL, Eigen3, OpenMP, OpenCV core/imgproc/highgui/photo, C++17) map 1:1 to the recipe's host/run pins; the verbatim LICENSE notice `odm-orthophoto-AGPL-3.0.txt` ships in `info/licenses/` and `share/licenses/odm-orthophoto/`; license expression `AGPL-3.0-only AND MIT` (MIT = original installed packaging/test code only). The former blocker — owner license review of the AGPL grant and its §13 network clause — is resolved: the owner confirmed `AGPL-3.0-only` on 2026-10-27. No open work retained.

AC #3 readiness decision: odm-orthophoto `0.0.0.dev20250225` build 0 is **technically ready** for an initial linux-64 publication. Remaining owner/platform conditions: (1) the four `release_checks` are flipped `true` by the owner-approval commit accompanying this review; (2) publication requires the tag `odm-orthophoto-v0.0.0.dev20250225-b0` on the approved HEAD plus the manual Release through the proven guard/release.yml OIDC publisher (TASK-15); (3) the snapshot version `0.0.0.dev20250225` is intentional — upstream declares no release version; (4) no platform beyond linux-64 is built or certified. Completing this task flips no flags itself, publishes nothing and certifies no untested platform.

Post-publication addendum (2026-10-27): the remaining owner conditions from AC #3 were executed the same day. The gates were flipped by owner approval (PR #16, merged as `995e412`), the tag `odm-orthophoto-v0.0.0.dev20250225-b0` was placed on that HEAD, and the Release fired run [40592230904](https://github.com/Archont561/ODM-conda/actions/runs/40592230904), which needed five attempts. Attempts 1-2 failed at the channel-upload step with `authentication failed (HTTP 403)`: the prefix.dev repository grant for Archont561/ODM-conda is scoped to an explicit package list ("Upload: 6 packages") that did not include `odm-orthophoto` — the trusted-publisher configuration itself (workflow release.yml, environment prefix) was correct and the identical command had succeeded for dem2points at 16:24Z; the owner added the package to the grant. Attempts 3-4 then failed one step earlier, at source attachment: the workflow's `gh release upload` (no `--clobber`) rejected the assets already attached by attempt 2; the agent deleted the three Release assets to clear the rerun path (permanent-fix candidate: add `--clobber` to the two upload steps in release.yml — deferred to a separate change, not done mid-release; landed afterwards in a `--clobber`-free form because the lint forbids that flag in the publisher to protect artifact immutability — the two attachment steps now compare bytes against any already-attached asset: attach when absent, keep when identical, fail loudly on divergence, so publish-job reruns are idempotent without ever replacing published bytes). Attempt 5 was fully green (publish job 122522353941: checksums ✓, source-before-binary ✓, OIDC + Sigstore channel upload ✓, binary attached to the Release ✓; the rerun rebuilt nothing — reviewed artifacts were carried). Channel record verified in the linux-64 repodata: `odm-orthophoto-0.0.0.dev20250225-h873e7db_0.conda`, sha256 `4608b6ffb5dd73d844b826fba184acca80a234f4622b1b7950522506e5c13ca9`, attestations_sha256 `6b1bcadd2813422df6077078e9e903ed337ba32b6194a180b4dda892f068fa0c`, md5 `6c39fa5c5bd83fa008305c1fd249923d`, size 116,934 B matching the Release asset byte-for-byte, license `AGPL-3.0-only AND MIT`, depends exactly the recipe run pins with run-export re-pins (`libgdal-core >=3.11.5,<3.12.0a0`, `libopencv >=4.12.0,<4.12.1.0a0`, `__glibc >=2.28,<3.0.a0`, `_openmp_mutex >=4.5`, libgcc/libgomp/libstdcxx >=14); installable via `pixi add odm-orthophoto --channel archont561/archont561`. The channel now serves nine package names. Release assets: the .conda, source bundle, audit.json and SHA256SUMS.
<!-- SECTION:NOTES:END -->

2026-10-29: owner explicitly approved the four release gates for standalone odm-orthophoto 0.0.0.dev20250225 build 2 and authorized publication after the approval PR passes and merges. Scope is linux-64 component only, not a bundled GDAL/OpenCV/OpenVINO environment or full ODM. Owner previously accepted AGPL-3.0-only AND MIT and AGPL section 13 policy for build 0. Native run 40908393516 and independent artifact/source/notice inspection and fresh retest 40908908691 passed; dependency and OpenVINO evidence is in research/component-readiness-review.md. Evidence is not legal certification or a claim of identical release rebuild bytes. Tests ran on Ubuntu 24.04, not glibc 2.28; synthetic fixture and failed ODM trial do not establish full integration or real-world quality. Trusted main HEAD/tag, release rebuild, retest, audit, collision checks and durable source before binary publication remain required.
<!-- SECTION:NOTES:END -->

<!-- SECTION:NOTES:BEGIN -->
