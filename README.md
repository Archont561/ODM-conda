# ODM Conda packages

**Unofficial, modular OpenDroneMap packaging with Pixi and rattler-build.**

Target: the existing **`archont561/archont561`** Prefix channel, shared with CloudCompare.

> **Starter scaffold, not a full ODM/NodeODM distribution.** The four
> published Linux CPU components (OIDC + attestation, 2026-10-27/28) are
> `fpcfilter 0.2` build 1 (TASK-15), `dem2points 0.0.0.dev20220721` build 0,
> `odm-orthophoto 0.0.0.dev20250225` build 0 and `fastrasterfilter 1.0`
> build 0; their sixteen release gates are owner-approved `true`.

## Implemented components

| Component | Pinned source | Installed-test coverage |
| --- | --- | --- |
| `dem2points` | `4527122615f41044bde0e79850464ed33549ceeb` | Synthetic DEM → PLY, coordinates, normals, linkage |
| `fpcfilter` | ODM tag `331`, commit `6e0c1c0113939823b2ff3c2eef4d5907e7f5db6b`, plus local patch 0001 (build 1) | ASCII pass-through; no-normals sampling (regression for TASK-2); normals-bearing binary PLY sampling; linkage |
| `odm-orthophoto` | ODM reference `355` (numbered branch head), commit `55b66d87cc168b8ab287bf10e81d4da0890f84f1` | Synthetic textured OBJ quad → GeoTIFF structure, corner bounds, exact pixel data, linkage |
| `fastrasterfilter` | ODM reference `main` (branch head), commit `c5d6c074619e573f641c808f9bdd9d431a0b7e4b` | Synthetic GeoTIFF DEM → exact median-filter output at two window sizes (padding regression), geotransform preservation, help path, linkage |

The reference is **ODM 3.6.2** (`47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45`),
not moving ODM master. `dem2points` uses snapshot version `0.0.0.dev20220721`;
FPCFilter's `0.2` is its CMake version, not the ODM tag number.
`odm-orthophoto` uses snapshot version `0.0.0.dev20250225` (pinned commit
date); its ODM reference `355` is a numbered branch in the upstream repository,
whose head is the pinned commit. `fastrasterfilter`'s `1.0` is its CMake
project version; its ODM reference `main` is a branch in the upstream
repository (upstream publishes no tags), whose head is the pinned commit.

**FPCFilter's no-normals sampling path had an upstream bug** (the pinned commit
erased rejected points from a local copy). Build 1 carries a local fix,
`recipes/fpcfilter/patches/0001-*.patch`. The fix changes only that branch;
normals-bearing sampling and pass-through are byte-identical to upstream.
The project owner approved the patch, the license expression and build 1 on
2026-10-27 (Backlog **TASK-2**, review packet doc-10); all four fpcfilter
release gates are `true`. Build 1 was published to `archont561/archont561`
via the OIDC release workflow on 2026-10-27 (**TASK-15** publisher proof;
`pixi add fpcfilter --channel archont561/archont561`).

The project owner approved `dem2points 0.0.0.dev20220721` build 0 on
2026-10-27 (Backlog **TASK-3**, readiness review **TASK-23**, CI validation
run 40532334352); all four dem2points release gates are `true`. Build 0 was
published to `archont561/archont561` via the OIDC release workflow on
2026-10-27 (tag `dem2points-v0.0.0.dev20220721-b0`, release run 40540506268;
`pixi add dem2points --channel archont561/archont561`).

The project owner approved `odm-orthophoto 0.0.0.dev20250225` build 0 on
2026-10-27 (Backlog **TASK-4**, readiness review **TASK-28**, sprint
**TASK-29**, CI validation run 40584231748: packaged + fresh-env functional
tests, dependency audit PASS, source bundle `c02b61f6…`); all four
odm-orthophoto release gates are `true`. Upstream is AGPL-3.0 (network
copyleft); the owner confirmed the `AGPL-3.0-only AND MIT` expression and
accepted §13 as policy for this ODM-ecosystem component. Build 0 was published
to `archont561/archont561` via the OIDC release workflow on 2026-10-27 (tag
`odm-orthophoto-v0.0.0.dev20250225-b0`, release run 40592230904, green on
attempt 5 after the owner extended the package-scoped prefix.dev upload grant;
`pixi add odm-orthophoto --channel archont561/archont561`).

The project owner approved `fastrasterfilter 1.0` build 0 on 2026-10-28
(Backlog **TASK-5**, readiness review **TASK-30**, sprint **TASK-31**, CI
validation run 40603931789: packaged + fresh-env functional tests, dependency
audit PASS, source bundle `4729bdd5…`); all four fastrasterfilter release
gates are `true`. Upstream is AGPL-3.0 (network copyleft) with vendored MIT
mf2d/cxxopts; the owner confirmed the `AGPL-3.0-only AND MIT` expression and
accepted §13 as policy for this ODM-ecosystem component. Build 0 was published
to `archont561/archont561` via the OIDC release workflow on 2026-10-28 (tag
`fastrasterfilter-v1.0-b0`, release run 40653848189, green on the first
attempt; `pixi add fastrasterfilter --channel archont561/archont561`).

### Recipes under validation

`dem2mesh` has a linux-64 recipe pinned to the researched head of ODM reference
`334` and a generated-raster functional test. The test passed against a local
research build, **not yet against the packaged executable**. Native build,
installed-prefix and artifact validation and the full license review remain
open; all publication gates are false. On a machine with conda-forge access,
run the following commands. See TASK-6 for the current evidence.

```sh
pixi run build --component dem2mesh
pixi run test --component dem2mesh
pixi run audit --component dem2mesh
pixi run sources --component dem2mesh
```

`renderdem` also has a linux-64 recipe, pinned to the researched head of ODM's
`main` reference. Its generated point-cloud-to-raster fixture passed against a
local PDAL 2.10 research build, but its package, installed-prefix test, source
and notice review, and release gates remain unvalidated. The fixture exercises PLY and LAS
input, but not LAZ input. On a machine with conda-forge access,
run the same commands with `--component renderdem`.

`poissonrecon-odm` has a recipe for ODM's `PoissonRecon` make target. Its
sphere reconstruction fixture passed against a modified research-only
FAST_COMPILE build; the recipe builds the unmodified, full upstream variant.
The full native package, installed-prefix test and artifact audit have not
been validated here, and license/source review and all publication gates remain
open. On a sufficiently provisioned machine with conda-forge access, run the
same commands with `--component poissonrecon-odm`.

## Quick start

Requirements: Linux x86-64, Git, **Pixi 0.82.0**, and network access for initial
locked tool/source downloads. If this directory is not already a Git working tree,
initialize Git once with `git init -b main` before using Backlog or installing hooks.

```bash
pixi install --locked
pixi install --locked -e agent-tools
pixi run check
pixi run hooks-install

# Build one component, or omit --component to build all implemented components.
pixi run build --component fpcfilter
pixi run test --component fpcfilter
pixi run audit --component fpcfilter
pixi run sources --component fpcfilter
```

`check` runs syntax/TOML/manifest/Backlog/skill checks, Python and Bun tests,
Actionlint **with ShellCheck**, and recipe rendering. It does not compile engines.
`build` includes packaged tests; `test` reinstalls artifacts into fresh environments.
Tests generate small fixtures, not proprietary drone datasets.

The manual **Build and test native components** workflow provides a checkbox
for each implemented component. Check any combination to build, retest, audit,
and bundle those components; leave all boxes unchecked to select all. GitHub
limits workflow-dispatch inputs to ten, so adding a component also requires
updating the checkbox list. Automation that used the former `component` input
must instead pass individual boolean inputs such as `dem2mesh=true` and
`renderdem=true`.

Local commands still accept comma-separated names, for example:

```bash
pixi run build --component 'dem2mesh,renderdem'
pixi run test --component 'dem2mesh,renderdem'
pixi run audit --component 'dem2mesh,renderdem'
pixi run sources --component 'dem2mesh,renderdem'
```

The workflow does not publish packages or approve release gates.

The toolchain baseline is GCC 14 / glibc 2.28 sysroot; the selected dependencies
and older Linux runtimes still need target testing. Only Linux x86-64 CPU is enabled.
Windows, macOS, ARM and CUDA are not supported by this scaffold yet.

## Backlog and skills

Future components, known issues, acceptance criteria, dependencies and progress
are maintained in **Backlog.md**, not a second JSON roadmap or static architecture
and issues documents:

```bash
pixi run -e agent-tools bunx backlog task list --plain
pixi run -e agent-tools bunx backlog task TASK-2 --plain
pixi run -e agent-tools bunx backlog doc list --plain
pixi run -e agent-tools bunx skills list --json
```

Backlog covers the tooling migration, FPCFilter bug, license/source review,
remaining native components, full ODM, NodeODM, publishing setup and additional
platforms. Plans, maintained guides, archived evidence and ADRs live in `backlog/docs`.
Do not hand-edit CLI-owned task state; use the locked CLI.

[AGENTS.md](AGENTS.md) routes the four local skills (`session`, `backlog`,
`odm-packaging`, `release-review`) and three managed skills (`tdd`,
`writing-for-agents`, `refactor`). Managed copies are commit-pinned in
`skills-lock.json` and checked against their actual content hashes. Provenance and
upstream MIT notices are in [.agents/NOTICE.md](.agents/NOTICE.md).

Bun/Backlog/skills use a separate `agent-tools` Pixi environment: Bun's ICU pin
cannot coexist with the packaging Python build. The `bunx` task first performs a
frozen install and then runs `bun x --bun`; no system Node or bunx shim is needed.
The Conda Bun 1.3.11 package currently reports `1.3.11-canary.1`; see Backlog doc-3.

## Hooks and CI

Lefthook auto-discovers `.config/lefthook.yml`; there is no root config stub.
Contributor setup is in [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md).

- **Pre-commit:** parallel staged Python syntax, Taplo formatting and workflow lint.
- **Commit-msg:** Convco validates Conventional Commits from the actual message file.
  Both this hook and PR history checks explicitly use `.config/convco.yml`.
- **Pre-push:** unfiltered, sequential, fail-fast static/unit/agent/render gates.
- **PR/main CI:** `pixi run check`; PR commits also pass Convco range validation.
  PR runs cancel older runs by ref; main runs have SHA-distinct concurrency groups.
- **Manual native workflow:** the same cheap gate, then build/reinstall-test/audit/source.
- **Release:** serialized, non-cancelling component releases and an isolated OIDC publisher.
- **Developer sandbox:** after a change reaches `main`, `publish-sandbox.yml` publishes the locked `default` and `agent-tools` Linux environments to `sandbox/developer-linux-64`. This is a Git transport branch for restoring developer tools, not a package release.

Restore the published environment from a repository checkout with:

```bash
./restore.sh
```

The restore script fetches the matching sandbox branch when needed. On shared or locked-down machines, opt out of per-user Pixi tool registration with `PIXI_SANDBOX_USER_TOOLS=skip ./restore.sh`.

Backlog conventions adapt `Archont561/pixi-sandbox` at `1903b088a0896126dee82e2a8b6b007942303ffc`; the generated sandbox workflows/bootstrap are based on v0.9.0 at `603166a44c24bfba9d82d62f9f5638ca6ba31d9e`.
No automatic component version bump or release-per-session policy was copied.

## Repository layout

```text
pixi.toml / pixi.lock         # exact repository tooling; not the application environment
package.json / bun.lock      # private, exact JS development tools
AGENTS.md / .agents/          # scoped local skills, managed copies, notices
skills-lock.json             # manager-generated source refs and content hashes
backlog/                     # CLI-managed tasks, plans, guides, decisions and evidence
recipes/                     # native component recipes (one directory each)
recipes/components.json     # shared pins, notices, versions and human gates
recipes/variants.yaml        # shared, versioned compiler/sysroot baseline
scripts/ / tests/            # packaging/check helpers and generated-data tests
.config/lefthook.yml        # auto-discovered local hook configuration
.config/convco.yml          # explicit shared commit/check policy
.github/CONTRIBUTING.md     # contributor entry point
.github/workflows/           # thin checks/build; isolated credentialed publication
```

Generated `output/`, `reports/`, `source-bundles/`, release staging, caches and
`*.zip` exports are ignored, not repository source. The old root `docs/` is obsolete;
maintained guidance lives only in `backlog/docs`. Source bundles include
Backlog/skills/locks and required notices, not dependency trees or Git internals.
Local artifacts are regenerated with the build/test/audit/source tasks when needed.

## Package milestones

All 13 planned packages have a Backlog milestone and one undated Sprint coordinator
with explicit work/review dependencies. See [the package milestone map](backlog/docs/plans/doc-1%20-%20Modular-ODM-component-packaging-plan.md).
Native components can progress in parallel; ODM requires their readiness gates,
and NodeODM requires ODM. Shared owner/platform work stays separate.

## Offline development

Conda-forge tooling is already declared in the two locked environments. Offline
work also needs the installed/cached packages and Bun project dependencies; locks
alone are not the payload. Native recipe builds need additional isolated build
dependencies and upstream sources. See [the offline provisioning guide](backlog/docs/guides/doc-9%20-%20Offline-development-tooling-and-provisioning-boundaries.md).
No portable transport or offline native-build guarantee is implied.

## Publication and installation

Creating the GitHub repository, configuring its `prefix` environment and adding
that repository's narrowly scoped OIDC authorization to the **existing** channel
are owner actions in **TASK-15**. CloudCompare's authorization is not inherited.
Read [the Backlog publishing guide](backlog/docs/guides/doc-7%20-%20Publish-to-the-existing-Prefix-channel.md) for the exact review/tag sequence.

The no-checkout publisher makes corresponding source available before uploading
the channel binary and does not run project scripts with credentials. Successful
checks never automatically approve publication.

These are **future** installation commands, not a claim that packages are online:

```bash
pixi init odm-tools
cd odm-tools
pixi workspace channel add https://prefix.dev/archont561/archont561
pixi workspace channel add conda-forge
pixi add fpcfilter dem2points
```

There is intentionally no `odm` command yet. Full ODM's installed layout, launcher
and end-to-end dataset tests are separate Backlog work.

## Licensing and validation

The root [MIT license](LICENSE) covers original packaging code only. It does not
relicense upstream components, imported skills, vendored code, models or patches.
Read [the Backlog licensing guide](backlog/docs/guides/doc-6%20-%20Licensing-and-source-distribution-checklist.md) and the
[archived native validation baseline](backlog/docs/validation/doc-8%20-%20Archived-native-scaffold-validation-baseline.md). This is not an official OpenDroneMap
release, a complete legal audit, or certification of every upstream mode/platform.
