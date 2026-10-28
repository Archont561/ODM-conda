---
id: TASK-7
title: Package poissonrecon-odm
status: In Progress
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-28 11:08'
labels:
  - component
  - poissonrecon-odm
milestone: m-5
dependencies: []
priority: medium
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upstream: https://github.com/OpenDroneMap/PoissonRecon
Reference in selected ODM build: 290
Next work: Port make/MSBuild integration and the exact selected ODM release patches.
Read the exact ODM reference recorded in components.json before choosing source revisions. This is planned work, not an existing recipe or a supported package.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The source graph is pinned to immutable commits and archive checksums, with ODM-required patches reviewed.
- [ ] #2 A real recipe declares build/host/run dependencies, carries the applicable notices/source, and passes installed-prefix functional tests.
- [ ] #3 components.json, source staging, artifact audits and human release gates are extended intentionally; no placeholder package is published.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Preliminary source research (2026-10-28): ODM 3.6.2 SuperBuild uses mutable branch `290`, resolved to `97caa6d34d1b05b59888bed019dea89ced74445e`; codeload archive SHA256 `88743428a97cbeed7d55e713fcfa42caebbfb7dcb2467d68899bd8feab95364b`. The inline SuperBuild definition runs `make poissonrecon` and copies `Bin/Linux/PoissonRecon`; it specifies no patch command for this component. Root LICENSE is MIT, but bundled sources and the actual build inputs still need a complete notice audit. No recipe or native validation exists.

Local research build attempt (2026-10-28): downloaded and hash-verified the pinned archive. Upstream make poissonrecon initially failed without libpng headers; retry with restored odm-dev headers and libraries reached the main C++ compilation. With system GCC 12 and upstream -O3 flags, cc1plus reached approximately 3.8 GiB RSS on this 4 GiB sandbox and was deliberately stopped to avoid an out-of-memory crash. No binary or package was produced. This does not establish a compiler defect or memory requirement for other environments; native build resources/toolchain and vendored PNG/JPEG/ZLIB notices still need review.

A further single-job research compile with upstream optimization overridden to -O0 still approached 3.8 GiB RSS on this 4 GiB sandbox and was stopped before an OOM; no binary was produced. Native CI or a larger build environment is required for meaningful validation.

2026-10-28: added a provisional linux-64 poissonrecon-odm 13.8 recipe using the pinned upstream make poissonrecon target with compiler wrappers, single-job compilation, two hash-checked makefiles, and all release checks false. Carried the root MIT license, BSD source header, and bundled libpng and zlib header notices provisionally; full notice review and security assessment of the old static libpng remain open. Added generated outward-normal unit-sphere functional fixture. It passes against a local research build with FAST_COMPILE enabled and -O0 (which limits supported degree/boundary options and is NOT the unmodified full recipe). Installed layout was manually assembled around that research build, not from a Conda artifact. Render-only and corresponding-source bundle succeeded; actual rattler-build could not solve compiler dependencies because conda.anaconda.org was unreachable. Prior attempts to compile the full variant approached 3.8 GiB RSS and were stopped; package build, isolated installed tests, audit, native CI and owner review still required.
<!-- SECTION:NOTES:END -->
