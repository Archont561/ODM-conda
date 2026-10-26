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
recipes alone are not a photogrammetry engine. FPCFilter's non-normals sampling
limitation remains TASK-2 until actually resolved.
