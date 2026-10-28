---
id: TASK-30
title: Review fastrasterfilter package-readiness evidence
status: Done
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-28 08:50'
labels:
  - packaging
  - review
  - fastrasterfilter
milestone: m-3
dependencies:
  - TASK-5
type: task
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Independently review the deliverables produced by TASK-5 for the fastrasterfilter milestone. This task verifies evidence and unresolved restrictions rather than duplicating recipe implementation. Review the selected raster-library ABI and a licensed deterministic raster-filter fixture from an installed prefix. Human release approval, Prefix authorization and actual upload remain separate owner actions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Review actual installed-prefix functional/relocation and dependency-audit evidence for the declared Linux CPU target, with artifact identities, regressions and limitations linked to the work task.
- [x] #2 Review exact source/patch/build-script correspondence, dependency source obligations, notices and applicable code/data/model license expressions; resolve blockers or explicitly retain them as open work.
- [x] #3 Record a maintainer-facing readiness decision and remaining owner/platform conditions. Completing this task does not itself flip executable release flags, publish a binary or certify untested platforms.
<!-- AC:END -->

<!-- SECTION:NOTES:BEGIN -->
## Implementation Notes

Independent review of the fastrasterfilter deliverables produced by TASK-5, from the owner-dispatched native run [40603931789](https://github.com/Archont561/ODM-conda/actions/runs/40603931789) (main `b69b666`, 2026-10-27, component=fastrasterfilter, attempt 1, fully green in ~35 s: solve + GCC 14 build ✓, packaged tests ✓, fresh-env retest ✓, audit ✓, source bundle ✓, artifact save ✓).

AC #1 evidence: the linux-64 artifact was built from pinned commit `c5d6c074619e573f641c808f9bdd9d431a0b7e4b` (archive sha256 `0dbbb42c4ac63adce825447641b366db1566bffee5d45b3e5fdae757f565993e`, 32,346 B); the audit enforced the internal identity `fastrasterfilter-1.0-0.conda` against `recipes/components.json` (name/version/build/subdir) and the exact build-hash filename, byte size and dependency re-pins are recorded in the run's audit JSON (`reports/audit-fastrasterfilter.json`), carried in CI artifact odm-components-linux-64 (ID 12780031224, 405,434 B, zip sha256 `a241a1aac8e131611bd047ff07bd7235cb90cc5ccb33a3c5274a1abf72778469`, retained to 2026-11-10) and to be re-pinned permanently by the publication record. The fresh-environment retest PASSed the installed-prefix functional fixture ("PASS: fastrasterfilter installed-prefix linkage and generated-data functional tests"): pure-Python 8×8 Float32 GeoTIFF (constant 123.5, diagonal −999/+999 spike pair, geotransform 100,1,0,200,0,−1, no CRS) → `fastrasterfilter -r 1` at the default 512 window and at `-w 4` → per-pixel exact 123.5 output in both runs, byte-identical results, Float32/single-band/uncompressed IFD verified, ModelPixelScale/ModelTiepoint preserved, no-input help path exit 0, `ldd` linkage clean. The dependency audit PASSed: required runtime set {`__glibc`, `libgcc`, `libstdcxx`} ∪ {`libgdal-core`, `libgomp`} declared; notices verified in payload and `info/licenses/`; payload bounded to `bin/fastrasterfilter` + `share/licenses/fastrasterfilter/` + `share/odm-conda/fastrasterfilter/` with no build-cache or checkout leakage; the recipe's `skip_pyc_compilation` guard keeps the installed fixture out of `__pycache__` even if the host graph drifts (this host has no Python today). Source bundle `source-fastrasterfilter-1.0-b0.tar.gz` sha256 `4729bdd511d534a571ba29c82147d02224138ff5348f31d935d60ee0104d7be0`. No regressions were needed: first-attempt green. Limitations: GitHub ubuntu-24.04 host glibc 2.39 — the `>=2.28` floor is a sysroot-2.28 toolchain declaration, not runtime-tested on older distributions; linux-64 only; no ODM end-to-end integration (TASK-13); the fixture proves exact median-filter semantics on a synthetic raster, not photogrammetric DEM quality; the nodata-masked input path (nodata→NaN→median→nodata) is not exercised by the fixture, while the pinned commit's block-padding fix is covered by the `-w 4` run.

AC #2 correspondence: exact source/patch/build-script correspondence holds — no patches, no disabled build trees, no submodules or CMake download directives; the entire upstream tree is 8 files (CMakeLists.txt, LICENSE, README.md, main.cpp, utils.hpp, vendor/cxxopts.hpp, vendor/mf2d/{LICENSE,filter.cpp,filter.hpp}). Upstream CMake dependencies (GDAL, OpenMP, C++17, stdc++fs on Linux) map 1:1 to the recipe's host/run pins (`libgdal-core >=3.11,<3.12`, `libgomp >=14`); GDAL and OpenMP remain separate Conda runtime dependencies and nothing third-party is copied into the package beyond the vendored sources compiled into the executable. Notices: `fastrasterfilter-AGPL-3.0.txt` (verbatim root LICENSE), `mf2d-MIT.txt` (verbatim vendor/mf2d/LICENSE, Jukka Suomela 2014), `cxxopts-MIT.txt` (first-comment, Jarryd Beck), plus `packaging-MIT.txt`; license expression `AGPL-3.0-only AND MIT`. The former blocker — owner license review of the AGPL grant and its §13 network clause, explicitly not inherited from the odm-orthophoto approval — is resolved: the owner confirmed `AGPL-3.0-only AND MIT` on 2026-10-28. No open work retained.

AC #3 readiness decision: fastrasterfilter `1.0` build 0 is **technically ready** for an initial linux-64 publication. Remaining owner/platform conditions: (1) the four `release_checks` are flipped `true` by the owner-approval commit accompanying this review; (2) publication requires the tag `fastrasterfilter-v1.0-b0` on the approved HEAD plus the manual Release through the proven guard/release.yml OIDC publisher (TASK-15 flow, rerun-safe byte-compare attachment per PR #18); (3) the prefix.dev upload grant already includes fastrasterfilter (original six-package grant — no grant change needed, unlike odm-orthophoto); (4) version `1.0` is upstream's CMake project version, not an upstream release — upstream publishes no tags and the ODM reference is the `main` branch head; (5) validation provenance: run 40603931789 executed on `b69b666`, and the approval HEAD differs only by PR #20's test-framework changes (tests/, pixi.toml, .gitignore) with recipe, build script and packaged payload byte-identical; (6) no platform beyond linux-64 is built or certified. Completing this task flips no flags itself, publishes nothing and certifies no untested platform.
<!-- SECTION:NOTES:END -->
