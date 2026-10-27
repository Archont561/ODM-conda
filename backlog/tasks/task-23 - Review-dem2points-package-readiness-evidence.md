---
id: TASK-23
title: Review dem2points package-readiness evidence
status: Done
assignee: []
created_date: '2026-10-26 20:59'
updated_date: '2026-10-27 16:34'
labels:
  - packaging
  - review
  - dem2points
milestone: m-0
dependencies:
  - TASK-22
  - TASK-3
type: task
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Independently review the deliverables produced by TASK-22 for the dem2points milestone. This task verifies evidence and unresolved restrictions rather than duplicating recipe implementation. Recheck the GDAL-linked executable and declared runtime dependencies; report the actual tested host rather than claiming minimum-glibc certification. Human release approval, Prefix authorization and actual upload remain separate owner actions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Review actual installed-prefix functional/relocation and dependency-audit evidence for the declared Linux CPU target, with artifact identities, regressions and limitations linked to the work task.
- [x] #2 Review exact source/patch/build-script correspondence, dependency source obligations, notices and applicable code/data/model license expressions; resolve blockers or explicitly retain them as open work.
- [x] #3 Record a maintainer-facing readiness decision and remaining owner/platform conditions. Completing this task does not itself flip executable release flags, publish a binary or certify untested platforms.
<!-- AC:END -->

<!-- SECTION:NOTES:BEGIN -->
## Implementation Notes

Independent review of the dem2points deliverables produced by TASK-22
(evidence review; no recipe work duplicated). Evidence base: CI run
[40532334352](https://github.com/Archont561/ODM-conda/actions/runs/40532334352)
(job `122288238934`, headSha `79841ca` = main, dispatched by the project owner),
its CI artifact `odm-components-linux-64` (ID 12746897342, retained until
2026-11-10), and the TASK-22 implementation notes.

AC #1: installed-prefix functional/relocation/dependency-audit evidence
reviewed for the declared linux-64 CPU target — linkage + generated-data
functional tests passed in two independent fresh environments (build-time test
env and the isolated `rattler-build test` retest with conda-forge strict
priority); relocation exercised via rpath removal + relink; audit PASS →
`reports/audit-dem2points.json`. Artifact identities linked to TASK-22:
`dem2points-0.0.0.dev20220721-h873e7db_0.conda` (54.58 KiB; variant
`h873e7db_0` = gcc 14 / sysroot 2.28 / linux-64), source bundle
`source-dem2points-0.0.0.dev20220721-b0.tar.gz` (SHA256 `39dc2183…`).
Limitations stated honestly: tested host was Ubuntu 24.04.5 with glibc 2.39 —
the declared `__glibc>=2.28` floor is a toolchain declaration, not a tested
certification; linux-64 only; no ODM end-to-end run; no regressions exist for
this component (unmodified upstream source, no patches).

AC #2: correspondence reviewed — source = pinned upstream commit
`4527122615f41044bde0e79850464ed33549ceeb` (archive sha256 `b5d87bca…`
verified by rattler-build at fetch), no patches, build driven by
`recipes/dem2points/recipe.yaml` + `scripts/build_component.py`. The package
ships only the executable, three notices (root GPL-3.0 text, CmdLineParser
BSD-3-Clause first comment, packaging MIT), `SOURCE.txt`, `upstream.json` and
`functional_test.py` — no vendored dependency source. Shipped dependency
graph: `libgdal-core 3.11.5 h4f65170_7` (plus its transitive conda-forge
closure: geos 3.14.1, proj 9.8.1, libspatialite 5.1.0, xerces-c 3.3.0, …),
`libgcc`/`libstdcxx` >=14, `__glibc>=2.28,<3.0.a0` — all dynamically linked
conda-forge packages, none copied into this package, so their
source/redistribution obligations ride on conda-forge's own packaging. License
expression `GPL-3.0-only AND BSD-3-Clause AND MIT`: the GPL-3.0-only
version choice is owner-confirmed (2026-10-27, recorded in TASK-3); notices
installed verbatim. Technical blockers: none. Explicitly retained as open
work (permitted by this AC): the owner's dem2points release-acknowledgement
decision — all four gates remain `false` — and any publication decision; both
are separate owner actions.

AC #3: maintainer-facing readiness decision — dem2points
`0.0.0.dev20220721` build 0 is **technically ready** for an initial linux-64
package: validation is complete and reproducible from the pinned source, the
license expression is owner-confirmed, and the corresponding-source bundle
regenerates in CI. Remaining owner/platform conditions: (1) flip the four
`release_checks` if publication is wanted (currently all `false`); (2)
publication additionally requires a tag on the approved HEAD and a manual
Release through the proven guard/release.yml publisher (TASK-15); (3) the
snapshot version `0.0.0.dev20220721` is intentional — upstream declares no
release version; (4) no platform beyond linux-64 is built or certified.
Closing this task flips no flags, publishes nothing and certifies no untested
platform.
Post-publication addendum (2026-10-27): the remaining owner conditions from
AC #3 were executed the same day. The gates were flipped by owner approval
(PR #9, merged as `05a761f`), the tag `dem2points-v0.0.0.dev20220721-b0` was
placed on that HEAD, and the manual Release fired run
[40540506268](https://github.com/Archont561/ODM-conda/actions/runs/40540506268)
— green (build ✓ 36 s, publish ✓ 18 s; source uploaded before the binary;
OIDC + Sigstore attestation). Channel record verified in the linux-64
repodata: `dem2points-0.0.0.dev20220721-h873e7db_0.conda`, sha256
`80840e8befa0b0dbdf3d99777032b40bfe87b774c3823a3201f3550535eec2da`,
attestations_sha256
`7dec913f8fb5f19754492d66580579280b5e083e2d008448534cd845b0e39386`, size
55,883 B matching the Release asset; installable via
`pixi add dem2points --channel archont561/archont561`. Observation: the
prefix.dev repodata edge cache served a stale copy for several minutes after
the successful upload — verified with a cache-busted re-fetch.
<!-- SECTION:NOTES:END -->
