---
id: doc-10
title: TASK-2 FPCFilter no-normals sampling review packet
type: other
created_date: '2026-10-27'
---

# TASK-2 review packet: FPCFilter no-normals sampling

Status: **reviewed and approved by the project owner on 2026-10-27.** This packet supported AC #3 of TASK-2; the approval outcome is recorded in sections 5 and 6 below and in the TASK-2 notes.

## 1. Defect

- Upstream: `OpenDroneMap/FPCFilter` at commit `6e0c1c0113939823b2ff3c2eef4d5907e7f5db6b` (ODM tag 331). Archive SHA-256 `fb303e298ad5e5f246a20095ce0992b97e0cf6605387df5fd3e2d930516025a8`.
- File: `fastsamplefilter.hpp`, `FastSampleFilter::run()`, no-normals branch.
- Cause: rejected points were erased from a local copy of `file.points`, so the output kept every input point.
- ODM reach: OpenSfM's `export_ply` writes no normals, so `reconstruction.ply` from `--fast-orthophoto` with `--pc-sample > 0` takes this branch and sampling does nothing. The default OpenMVS dense cloud carries normals (`libs/MVS/Scene.cpp`), so the default path takes the normals branch. The latter is from source reading only, not an end-to-end run.

## 2. Change under review

- Patch: `recipes/fpcfilter/patches/0001-Write-no-normals-radius-sampling-results-back.patch`
- Patch SHA-256: `aae6c9914478ecfaa5d2cd5c8704342752dc2c24d8a441e02c728e60728faa6a`
- Applied by rattler-build after the upstream archive is verified. The upstream archive is unchanged.
- Scope: the no-normals branch only. It builds the kept list and assigns it to `file.points`. Without normals, `file.extras` is empty and is not touched. The normals branch is unchanged.
- Recipe build number: 0 → **1**. Recipe `version` stays `0.2`, the upstream CMake version.
- Not upstreamed. No upstream PR has been opened.

## 3. Test evidence

| Check | Original (build 0) | Patched (build 1) |
|---|---|---|
| No-normals radius 0.5, six points in two tight clusters: kept count (expected 2) | 6 — **fail** | 2 — **pass** |
| Installed-prefix functional test, current `scripts/functional_test.py` | fail (regression check) | pass |
| Normals + radius, normals no-radius, no-normals pass-through (no radius) | identical bytes | identical bytes |
| Random 3000-point no-normals cloud, 5 trials: all kept pairs ≥ radius apart | not satisfied (kept all 3000) | satisfied (about 800 kept per trial, min pairwise distance ≥ 0.3) |

Build commands run in `/home/user/ODM-conda` and in a separate build-0 checkout at `825ba09`:
- `pixi run check`: passes.
- `pixi run build|test|audit|sources --component fpcfilter`: pass for build 1.
- Build 0 was built and its own installed test passed. That test predates the regression check.

Artifacts:
- Build 1: `output/linux-64/fpcfilter-0.2-h873e7db_1.conda`, source bundle `source-bundles/source-fpcfilter-0.2-b1.tar.gz`.
- Build 0: `/home/user/work/build0/output/linux-64/fpcfilter-0.2-h873e7db_0.conda`, outside the repo.

Known warning: rattler-build reports "Overdepending against `_openmp_mutex`". This is pre-existing in the recipe and was not changed.

## 4. Modified-source notice and license

- The installed `share/odm-conda/fpcfilter/SOURCE.txt` for build 1 states `Modified: yes` and lists the patch with its SHA-256 and summary. Build 0 states nothing about modification, because its builder predates this notice.
- Recipe and `recipes/components.json` license expression: `GPL-3.0-only AND BSD-2-Clause AND MIT`, marked conservative pending review.
- Checked against upstream sources: `LICENSE` is the GPL-3.0 text. No file in the shipped sources carries a per-file notice. The only "either version 3 … or any later version" wording is the FSF's template in the appendix, which is advice to authors and not a grant. So `GPL-3.0-only` is the accurate identifier, and the "conservative" label in `components.json` can be dropped once TASK-3 confirms this.
- The vendored third-party files are MIT (cxxopts, json) and BSD-2-Clause (nanoflann), as recorded in `components.json`.
- Upstream `LICENSE` is included verbatim as `share/licenses/fpcfilter/FPCFilter-GPL-3.0.txt`. The patch is distributed under the same upstream terms.
- Packaging code (MIT) does not relicense the upstream code or the patch.

## 5. Release acknowledgements

- At packet time, all `release_checks` for fpcfilter were `false`: `publishable`, `license_reviewed`, `source_completeness_reviewed`, `native_validation_passed`. The packet itself changed none of them.
- 2026-10-27: the project owner granted full release approval for build 1, and all four gates were set to `true` in `recipes/components.json`. This is an owner policy decision recorded in TASK-2, not legal certification.

## 6. Decisions

Recorded by the project owner:
1. **Accepted:** keep the local patch as the workaround. No upstream PR will be opened.
2. **Confirmed (2026-10-27, project owner):** the license expression `GPL-3.0-only AND BSD-2-Clause AND MIT` is approved for build 1, and the "conservative … pending review" label was dropped from `components.json`. The upstream code still cannot be relicensed by the packager; the section 7 options are unchanged. TASK-3 remains open for dem2points and for the dependency and durable-source-URL obligations.
3. **Confirmed (2026-10-27, project owner):** build number 1 is the approved release candidate. The explicit confirmation is recorded in the TASK-2 notes; release proceeds per doc-7 (tag `fpcfilter-v0.2-b1` on the default-branch HEAD carrying the gates, then publish a non-prerelease GitHub Release).

## 7. Path to a more permissive license

- The packaging code is already MIT, and the vendored libraries are MIT or BSD. The FPCFilter binary, the patch, and the upstream code are GPL-3.0-only, so the package as a whole must stay GPL-3.0 with its corresponding source.
- Two routes would change that:
  1. **Relicensing by the upstream copyright holders.** Only they can dual-license or relicense the code. This needs their written consent, which means contacting them. It is not something the packager can do alone.
  2. **Clean-room reimplementation under MIT or BSD.** Write a new sampler from the observable behavior (the CLI flags, the PLY input and output, and the minimum-distance rule), not from the FPCFilter code. Keep a clean-room record: a spec written from behavior, and an implementation that never reads the GPL source. This is a new component with its own name. It would not be a copy of FPCFilter, and it would need its own tests and review.
- Neither route is needed to ship this workaround. Until one is done, the notices, corresponding-source bundle, and GPL-3.0-only expression must stay in every release.

## 8. Known limits

- ODM end-to-end was not run. The `--fast-orthophoto --pc-sample` claim comes from reading the OpenSfM and ODM source at the pinned references.
- The normals-bearing branch reads a shared voxel map from parallel threads without a lock. This was observed in source and is not verified. It is out of TASK-2 scope.
- Only linux-64 CPU is validated.
