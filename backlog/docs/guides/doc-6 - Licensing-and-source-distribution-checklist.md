---
id: doc-6
title: Licensing and source-distribution checklist
type: other
created_date: '2026-10-26 19:39'
updated_date: '2026-10-27 20:05'
---
# Licensing and source-distribution checklist

Technical guidance, not legal advice or a completed license audit.

## A channel is not a license boundary

`archont561/archont561` can host independent packages under different licenses.
Merely placing them together is not the same as combining/linking them into one
program. Conversely, splitting a combined work into multiple packages does not
remove applicable copyleft obligations.

## What this scaffold does

- Pins every implemented upstream archive to immutable commits and SHA256 checksums.
- Records each package's proposed SPDX expression and specific notice paths.
- Preserves root licenses and original vendored header notice bytes.
- Includes notices in Conda metadata and installed `share/licenses/<name>/`.
- Installs `SOURCE.txt` with a release-specific source URL.
- Generates a deterministic source archive with upstream source (including bundled
  source), recipes, build/test helpers, documentation and tooling lockfile.
- Uploads corresponding-source assets before a release binary reaches Prefix.
- Keeps `license_reviewed` and `source_completeness_reviewed` false by default.

These checks do not prove the legal adequacy of the entire dependency graph. The
maintainer remains responsible for what is actually built and distributed.

## Implemented component license inventory

This is a source-level starting inventory, not a completed audit or permission
to publish. Executable source pins, proposed license expressions and notice paths
remain in recipes/components.json and the recipes. Upstream material keeps its original
licenses; the repository MIT license covers original packaging code only.

### dem2points

- Repository: https://github.com/OpenDroneMap/dem2points
- Commit: `4527122615f41044bde0e79850464ed33549ceeb`
- Upstream root `LICENSE`: GNU GPL version 3 text. Metadata conservatively uses
  `GPL-3.0-only` until the maintainer confirms the applicable grant/version choice.
- `src/CmdLineParser.h`: leading BSD-3-Clause notice, retained verbatim.
- Runtime GDAL is a separate Conda dependency, not copied into this package.
- Installed original packaging/test code adds an MIT notice.

Current recipe expression: `GPL-3.0-only AND BSD-3-Clause AND MIT`.

### FPCFilter

- Repository: https://github.com/OpenDroneMap/FPCFilter
- ODM reference: tag `331`; resolved commit `6e0c1c0113939823b2ff3c2eef4d5907e7f5db6b`.
- Upstream root `LICENSE`: GNU GPL version 3 text; same conservative version-choice policy.
- `vendor/cxxopts.hpp`: MIT notice in the leading comment.
- `vendor/json.hpp`: MIT notice in the leading comment.
- `vendor/nanoflann.hpp`: BSD-2-Clause notice in the leading comment.
- Upstream's optional CMake test target is disabled; test-only curly/doctest/
  happly code is not compiled into the package. Its test-only GoogleTest fetch
  is also disabled. The entire `test/` tree remains in the original source
  archive with its notices; do not strip those source notices.
- Installed original packaging/test code adds an MIT notice.

Current recipe expression: `GPL-3.0-only AND BSD-2-Clause AND MIT`.

### odm-orthophoto

- Repository: https://github.com/OpenDroneMap/odm_orthophoto
- ODM reference: SuperBuild `GIT_TAG 355`; upstream uses numbered branches
  instead of tags, and `refs/heads/355` resolved to commit
  `55b66d87cc168b8ab287bf10e81d4da0890f84f1` (verified 2026-10-27).
- Upstream root `LICENSE`: GNU Affero GPL version 3 text; source files carry no
  separate headers and there is no or-later grant outside the license
  boilerplate. Metadata conservatively uses `AGPL-3.0-only` until the
  maintainer confirms the applicable grant/version choice. AGPL §13's network
  clause is an explicit review point for any service use of built binaries.
- No vendored third-party code: `src/` contains only project-original sources
  (Logger, OdmOrthoPhoto, main).
- Runtime GDAL, OpenCV and Eigen are separate Conda dependencies, not copied
  into this package.
- Installed original packaging/test code adds an MIT notice.

Current recipe expression: `AGPL-3.0-only AND MIT`.

## Notice preservation

`scripts/build_component.py` copies the root license and extracts the first
complete comment from the listed headers without rewriting the bytes. It places
notices in both `.conda-notices/` (for recipe `license_file`) and installed
`share/licenses/<component>/`. A changed/missing header notice fails the build.

The artifact audit verifies installed notice paths and Conda's `info/licenses/`
metadata. These checks are helpful but do not determine copyright ownership,
license compatibility, or whether a version-choice expression is legally correct.

## Imported development guidance

The maintained managed agent-skill copies and adapted pixi-sandbox routing retain their
upstream MIT notices separately from root LICENSE. See `.agents/NOTICE.md` and
`.agents/licenses/manifest.json` for exact source commits, corresponding license
files and immutable upstream URLs. `skills-lock.json` was generated by the pinned
skills manager; checks verify the committed content hashes. This is not a security
or dependency-license audit. Bun, Backlog.md, skills and Conda development binaries
are installed from the locks, not redistributed inside native component payloads or maintained source trees.

## Human review before each new source/build configuration

- [ ] Confirm the applicable upstream grant, including `-only` vs `-or-later`;
      do not infer the latter just from the standard license's example appendix.
- [ ] Review compiled-in and vendored code, generated files, patches and assets.
- [ ] Keep required copyright, attribution, warranty and modification notices.
- [ ] Check compatibility of code that is actually linked/combined.
- [ ] Confirm redistribution rights for prebuilt executables and runtime libraries.
- [ ] Determine and provide all required corresponding source for the distribution.
- [ ] Ensure the archived source really matches the shipped object code.
- [ ] Keep a clear source link next to downloads and inside the package, and retain
      availability while needed to satisfy the applicable license.
- [ ] Confirm model/imagery licenses independently of code licenses.
- [ ] Document material limitations or unresolved issues in the release notes.

A source bundle containing only the main repository is insufficient when the
build fetched other repositories/submodules. The current bundler intentionally
rejects `.gitmodules` and undisclosed CMake downloads in enabled build targets.
FPCFilter explicitly records `test/` as disabled (`BUILD_TESTING=OFF`), so its
test-only GoogleTest fetch is not part of the built object-code source graph.
The original archive still includes that entire test tree and its notices.

External Conda dependencies are not copied into these component artifacts. This
fact alone does not settle every source obligation for all possible combined or
linked works. Review which dependency sources/notices are required for the actual
distribution; expand source staging before asserting completeness.

## Specific future pitfalls

- **OpenPointClass:** review applicable AGPL grants, original notices and model
  redistribution rights separately.
- **MVS-texturing, MVE, VCG and Eigen:** inspect per-file exceptions, compiled-in
  code, patches and nested dependency source completeness.

- **ODM OpenSfM fork:** its README explicitly places ODM changes under AGPLv3,
  not BSD. Preserve original notices too.
- **OpenMVS and ODM:** review applicable AGPL grants and combined-code compatibility.
- **LAStools:** a mixed distribution. Package the explicitly open-source subset
  only unless separately authorized; free-to-use binaries are not automatically
  redistributable.
- **Obj2Tiles/helper DLLs:** check licenses and complete sources for included
  third-party code. Being downloaded by upstream is not sufficient permission.
- **CUDA:** review NVIDIA redistribution permissions and copyleft compatibility;
  using a dependency package is not a blanket legal exemption.
- **Model weights/datasets:** code licenses do not automatically cover these.

## Network use and output data

Binary distribution and running a service are different activities. AGPLv3's
remote-interaction provision applies to modified programs supporting such
interaction; hosting a modified service can require a prominent corresponding-
source offer to its remote users. A private registry does not cancel recipients'
rights. Ordinary orthophotos/point clouds are not automatically AGPL just because
a tool generated them, unless their contents themselves include covered material.

The packaging repository's MIT license cannot relicense upstream binaries or
derived patches. Label published builds unofficial; do not imply endorsement.

## References

- GNU GPLv3: https://www.gnu.org/licenses/gpl-3.0.html (especially §§1 and 6)
- GNU AGPLv3: https://www.gnu.org/licenses/agpl-3.0.html (including §13)
- GNU FAQ: https://www.gnu.org/licenses/gpl-faq.html
- Selected ODM source: https://github.com/OpenDroneMap/ODM/tree/47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45
- FPCFilter source: https://github.com/OpenDroneMap/FPCFilter/tree/6e0c1c0113939823b2ff3c2eef4d5907e7f5db6b
- dem2points source: https://github.com/OpenDroneMap/dem2points/tree/4527122615f41044bde0e79850464ed33549ceeb
