---
id: TASK-10
title: Package mvs-texturing-odm
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 20:59'
labels:
  - component
  - mvs-texturing-odm
milestone: m-8
dependencies: []
priority: medium
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Upstream: https://github.com/OpenDroneMap/mvs-texturing
Reference in selected ODM build: c5a4d0c9a434553533c6e39d426e349fcfa5f48d
Next work: Stage MVE and all nested external sources; audit their licenses.
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
Preliminary source research (2026-10-28): ODM pins mvs-texturing commit `c5a4d0c9a434553533c6e39d426e349fcfa5f48d`; codeload archive SHA256 `295b11cb35c85f44908294bc89cd7d4f1057dee0016cc4cd35a5ed01570766f8`. Its SuperBuild also uses mutable OpenDroneMap/mve branch `356`, resolved to `90f13c18f92db6089c06c8c2451e283911f5f634` (archive SHA256 `f4d0d76a925d7482d14c2050b4488718c824947a3895eac196eac70ef19fc699`). The texturing CMake declares additional external projects: mapmap_cpu at `fa526e0963ca3e431a02aa7b9e87b85ba8a8e304`, rayint mutable branch `cuda`, and Eigen 3.3.2. Resolve and audit the complete enabled nested graph, disable network bootstrap and stage source explicitly. No recipe or native validation exists.


Staging research (2026-10-28): a provisional local graph also stages mapmap (`fa526e0963ca3e431a02aa7b9e87b85ba8a8e304`, archive SHA256 `01ab05c7f7e6e14f5a54bc2111f6af382b148a504670a30b42b70b1851767e39`), rayint mutable `cuda` head (`ad9f826a8b134090511709e5813a8ba56dc2e837`, archive SHA256 `7ed6d0af9ba58cb359eaed25bd87fa818507abe41fe56cf7ff9929dd953212a7`), and a GitHub mirror commit for Eigen 3.3.2 (`ae9889a130bd0a9d3007f41d015563c2e8ac605f`, archive SHA256 `f82dcfb9b297caf1ed43648c389cc5118839b3b4ced018d12cd11d5362b2811e`). The mirror archive is not the GitLab tarball specified by upstream; equivalence requires review. MVE is staged at a non-default `_external/mve` path requiring CMake configuration. Texturing still invokes ExternalProject downloads; rayint and mapmap have their own nested fetch definitions if configured independently. Decide and test the enabled build graph and disable downloads without weakening checks before claiming complete staging.


Offline CMake experiment (2026-10-28): `research/patches/mvs-texturing-offline.patch` (SHA256 `37d03ca8b5a50bd72b6e7a4ed2f2856e1d83c0355806f7fc9efa059f9a57ef65`) applies cleanly to the pinned texturing source. It removes the active elibs ExternalProject configuration and dependent target edges, fails configuration if the three staged dependency paths are missing, and removes `-march=native`. With the restored odm-dev CMake and explicitly supplied **temporary stub** TBB config and MVE libraries, configuration generated Ninja files with no obvious download commands or ext_* targets. Removing Eigen/Core produced the intended missing-source error. This is configure-only research, not a compiled executable, network-isolated build, license review or proof of source completeness. The restored odm-dev environment lacks TBB development CMake files and headers; native CI must supply a real host dependency and run actual builds. No recipe uses this experimental patch yet.


Local native research build (2026-10-28): built the pinned MVE libraries and then `texrecon` with the experimental offline patch using system GCC 12, restored odm-dev libraries and one job. The restored environment contained TBB runtime 2023.1.0 but no TBB development headers/config; for this experiment only, headers were obtained from oneTBB tag v2023.1.0, commit `3046c8b0c29df995980003ea24f4d78c80ec0c8d` (archive SHA256 `44763279bb3ac76fb67572cc3336d7421521bc882e9fde484ea662389f4fda0b`) and a local CMake imported target pointed at the restored libtbb.so.12. Linking initially failed because system libstdc++ lacked `CXXABI_1.3.15`; adding the restored Conda library directory to link search succeeded. `texrecon --help` printed usage and exited 1; `ldd` resolved TBB and libstdc++ from the restored prefix. Generated Ninja file had no obvious download commands. This was a local, non-installed, non-release build; network isolation was not enforced, no actual scene or output mesh was tested, no packaged ABI or source-completeness review is implied, and matching header tag to Conda build provenance is not verified. No release gate is changed. A CI recipe must use a genuine TBB development package, a consistent Conda toolchain, and installed-prefix functional and audit tests.


Eigen review (2026-10-28): GitLab's `3.3.2` tag resolves to commit `477d1e81928a8514d2cca6a6e1e7e478eecd8634`, whereas the GitHub mirror's tag resolves to `ae9889a130bd0a9d3007f41d015563c2e8ac605f`. Comparing the root Git trees by object IDs and modes showed every GitLab-listed item matched the GitHub tree, including the entire `Eigen` subtree `ed8a562c6e0da4fa8677ba68e05227a7789417e8`; GitHub additionally contains `.hgtags` (`6230c86a671a6d7ffa84fc4a17b1cbf977a1ea0b`). GitLab's `Eigen/Core` blob also matches (`82558155ec8599df8a4dc3b32b51ce85bb285ce0`). This establishes a specific tree difference, not identical Git commits or archive bytes; the original upstream archive MD5 and exact tar contents have not been checked. The original GitLab archive or a reviewed replacement decision is still needed for release. GitLab API: `https://gitlab.com/api/v4/projects/libeigen%2Feigen/repository/tags/3.3.2` and `/repository/tree?ref=3.3.2&per_page=100`; GitHub tree `a6257542e2ec890c9c52e727ffb686c1593af247`.

Experimental source-bundle smoke test: all five planned archives and the offline patch were included and their hashes verified from the resulting archive. This research bundle is not integrated with the release bundler and does not certify complete sources, licenses or network-free builds.
<!-- SECTION:NOTES:END -->
