---
name: odm-packaging
description: Add or update native ODM component recipes, dependency/source staging and installed-package tests. Use for rattler-build, CMake, ABI, source graphs or component integration.
---

# Native component workflow

Read the relevant Backlog task and `recipes/components.json`. The latter contains only
implemented recipes and the exact reference ODM release, not planned packages.
Read that release's SuperBuild definitions before selecting component sources.

1. Resolve every source, nested project and patch to immutable revisions and
   archive checksums. No network bootstrap inside a native build. The current
   source helper supports only the two starter graphs; extend it intentionally
   before adding submodules or enabled CMake fetches.
2. Keep build/host/run requirements separate. The repository's Pixi environment
   is tooling, never the packaged application environment. Use compiler/stdlib
   macros and the explicit variant baseline so runtime ABI requirements propagate.
3. Preserve and review root, per-file, bundled and model/asset notices. Read
   the licensing guide and component inventory in Backlog doc-6. Do not guess
   license version choice or
   assume a downloaded binary is redistributable.
4. Install to rattler's host prefix, not the outer Pixi prefix. Test executable
   behavior, Python imports where applicable, linkage and relocation from an
   installed environment, not only a source tree or `--help` output.
5. Update code and a failing behavioral fixture in focused slices; refactor only
   after green. For native changes run:
   ```bash
   pixi run check
   pixi run build --component COMPONENT
   pixi run test --component COMPONENT
   pixi run audit --component COMPONENT
   pixi run sources --component COMPONENT
   ```
6. Reset affected human release checks. Record exact tests and unrun platforms in
   the Backlog task, not a second progress document. No placeholder engine package.

Full ODM must consume the component packages, handle its SuperBuild-relative
paths/resources/launcher and pass a licensed end-to-end dataset. The two starter
recipes alone are not a photogrammetry engine. FPCFilter's no-normals sampling fix (local patch 0001, build 1) was approved
by the project owner on 2026-10-27; TASK-2 is done and the fpcfilter release gates are true (doc-10).
fpcfilter 0.2 build 1 was published to archont561/archont561 on 2026-10-27 via
OIDC with a Sigstore attestation (TASK-15 proof, Actions run 40515263476).
dem2points 0.0.0.dev20220721 build 0 was validated in CI (run 40532334352) and
owner-approved on 2026-10-27; its four release gates are true (TASK-3/22/23).
It was published to archont561/archont561 on 2026-10-27 via OIDC with a
Sigstore attestation (tag dem2points-v0.0.0.dev20220721-b0, release run 40540506268).
odm-orthophoto 0.0.0.dev20250225 build 0 (ODM reference `355`, resolved to the
numbered-branch head 55b66d87cc168b8ab287bf10e81d4da0890f84f1) landed its
recipe, AGPL-3.0-only notices and generated-data fixture on 2026-10-27 (TASK-4),
passed native CI validation the same day (run 40584231748: packaged and
fresh-env tests, audit PASS, source bundle) and was owner-approved including
the AGPL-3.0-only license call; its four release gates are true (TASK-4/28/29).
It was published to archont561/archont561 on 2026-10-27 via OIDC with a
Sigstore attestation (tag odm-orthophoto-v0.0.0.dev20250225-b0, release run
40592230904 attempt 5; attempts 1-2 hit an HTTP 403 because the prefix.dev
upload grant was scoped to a package list that did not yet include
odm-orthophoto - owner-fixed; attempts 3-4 tripped the no-clobber
gh release upload step on already-attached assets - cleared before attempt 5).
fastrasterfilter 1.0 build 0 (ODM reference `main`, resolved to the branch
head c5d6c074619e573f641c808f9bdd9d431a0b7e4b; upstream publishes no tags)
landed its recipe, AGPL-3.0-only + vendored-MIT (mf2d, cxxopts) notices and
synthetic-raster median-filter fixture on 2026-10-27 (TASK-5), passed native
CI validation the same evening on the first attempt (run 40603931789:
packaged and fresh-env tests, audit PASS, source bundle) and was
owner-approved on 2026-10-28 including the AGPL-3.0-only license call as its
own decision; its four release gates are true (TASK-5/30/31). It is not
published yet.
