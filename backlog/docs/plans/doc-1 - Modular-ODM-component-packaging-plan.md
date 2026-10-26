---
id: doc-1
title: Modular ODM component packaging plan
type: other
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 21:04'
---
# Packaging architecture

## Scope of this scaffold

Two real native component recipes, one public distribution channel, and no full
ODM package yet. All public artifacts are optional and gated; the scaffold itself
has not created a GitHub repository or changed Prefix settings.

`recipes/components.json` is the maintained index of implemented recipes only. Future
components and their acceptance criteria/dependencies live in Backlog tasks, not
a parallel JSON roadmap. Source pins, notices, versions and human release gates
remain executable packaging metadata, not task state.

The reference native dependency set is taken from ODM **3.6.2** commit
`47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45`, not a moving `master` checkout.
Branches used by that release are resolved once for the two starter projects.

## Proposed dependency graph

```text
opendronemap (application files, data and launcher; PLANNED)
├── opensfm-odm           Python + C++ / explicit Python and NumPy ABI
├── openmvs-odm           CPU first; VCG/Eigen and exact ODM patches
├── mvs-texturing-odm     texrecon; MVE and nested source staging
├── poissonrecon-odm      ODM fork + selected meshing patches
├── odm-orthophoto        orthophoto native executable
├── dem2mesh / dem2points / fpcfilter / fastrasterfilter / renderdem
├── openpointclass       code and model rights reviewed separately
└── existing compatible conda-forge packages

nodeodm (PLANNED) -> packaged ODM + locked/audited Node.js dependencies
```

Not every nested source needs its own published package immediately. It can remain
a private build dependency or bundled source when its license permits this, provided
its notices, exact source and binary/runtime requirements are accounted for.

## Package milestones and delivery gates

Each of the 13 planned packages has one undated milestone and one task labelled
`sprint`. The hierarchy is milestone membership plus explicit task dependencies:

```text
Package milestone
└── Sprint coordinator
    ├── recipe/validation work
    ├── independent readiness-evidence review
    └── applicable shared prerequisites
```

Existing task IDs and acceptance criteria are retained. Reviews consume the actual
implementation/validation evidence; they are not placeholder package builds.
Historical starter artifacts were cleaned, so the two starter validation tasks
regenerate evidence instead of claiming those artifacts still exist.

| Package milestone | Sprint gate | Implementation / validation | Evidence review |
|---|---|---|---|
| [dem2points (m-0)](../../milestones/m-0%20-%20dem2points.md) | [TASK-24](../../tasks/task-24%20-%20Sprint-dem2points-initial-package-readiness.md) | [TASK-22](../../tasks/task-22%20-%20Validate-dem2points-package-and-regenerate-review-inputs.md) | [TASK-23](../../tasks/task-23%20-%20Review-dem2points-package-readiness-evidence.md) |
| [fpcfilter (m-1)](../../milestones/m-1%20-%20fpcfilter.md) | [TASK-27](../../tasks/task-27%20-%20Sprint-fpcfilter-initial-package-readiness.md) | [TASK-25](../../tasks/task-25%20-%20Validate-fpcfilter-package-and-regenerate-review-inputs.md) | [TASK-26](../../tasks/task-26%20-%20Review-fpcfilter-package-readiness-evidence.md) |
| [odm-orthophoto (m-2)](../../milestones/m-2%20-%20odm-orthophoto.md) | [TASK-29](../../tasks/task-29%20-%20Sprint-odm-orthophoto-initial-package-readiness.md) | [TASK-4](../../tasks/task-4%20-%20Package-odm-orthophoto.md) | [TASK-28](../../tasks/task-28%20-%20Review-odm-orthophoto-package-readiness-evidence.md) |
| [fastrasterfilter (m-3)](../../milestones/m-3%20-%20fastrasterfilter.md) | [TASK-31](../../tasks/task-31%20-%20Sprint-fastrasterfilter-initial-package-readiness.md) | [TASK-5](../../tasks/task-5%20-%20Package-fastrasterfilter.md) | [TASK-30](../../tasks/task-30%20-%20Review-fastrasterfilter-package-readiness-evidence.md) |
| [dem2mesh (m-4)](../../milestones/m-4%20-%20dem2mesh.md) | [TASK-33](../../tasks/task-33%20-%20Sprint-dem2mesh-initial-package-readiness.md) | [TASK-6](../../tasks/task-6%20-%20Package-dem2mesh.md) | [TASK-32](../../tasks/task-32%20-%20Review-dem2mesh-package-readiness-evidence.md) |
| [poissonrecon-odm (m-5)](../../milestones/m-5%20-%20poissonrecon-odm.md) | [TASK-35](../../tasks/task-35%20-%20Sprint-poissonrecon-odm-initial-package-readiness.md) | [TASK-7](../../tasks/task-7%20-%20Package-poissonrecon-odm.md) | [TASK-34](../../tasks/task-34%20-%20Review-poissonrecon-odm-package-readiness-evidence.md) |
| [opensfm-odm (m-6)](../../milestones/m-6%20-%20opensfm-odm.md) | [TASK-37](../../tasks/task-37%20-%20Sprint-opensfm-odm-initial-package-readiness.md) | [TASK-8](../../tasks/task-8%20-%20Package-opensfm-odm.md) | [TASK-36](../../tasks/task-36%20-%20Review-opensfm-odm-package-readiness-evidence.md) |
| [openmvs-odm (m-7)](../../milestones/m-7%20-%20openmvs-odm.md) | [TASK-39](../../tasks/task-39%20-%20Sprint-openmvs-odm-initial-package-readiness.md) | [TASK-9](../../tasks/task-9%20-%20Package-openmvs-odm.md) | [TASK-38](../../tasks/task-38%20-%20Review-openmvs-odm-package-readiness-evidence.md) |
| [mvs-texturing-odm (m-8)](../../milestones/m-8%20-%20mvs-texturing-odm.md) | [TASK-41](../../tasks/task-41%20-%20Sprint-mvs-texturing-odm-initial-package-readiness.md) | [TASK-10](../../tasks/task-10%20-%20Package-mvs-texturing-odm.md) | [TASK-40](../../tasks/task-40%20-%20Review-mvs-texturing-odm-package-readiness-evidence.md) |
| [renderdem (m-9)](../../milestones/m-9%20-%20renderdem.md) | [TASK-43](../../tasks/task-43%20-%20Sprint-renderdem-initial-package-readiness.md) | [TASK-11](../../tasks/task-11%20-%20Package-renderdem.md) | [TASK-42](../../tasks/task-42%20-%20Review-renderdem-package-readiness-evidence.md) |
| [openpointclass (m-10)](../../milestones/m-10%20-%20openpointclass.md) | [TASK-45](../../tasks/task-45%20-%20Sprint-openpointclass-initial-package-readiness.md) | [TASK-12](../../tasks/task-12%20-%20Package-openpointclass.md) | [TASK-44](../../tasks/task-44%20-%20Review-openpointclass-package-readiness-evidence.md) |
| [opendronemap (m-11)](../../milestones/m-11%20-%20opendronemap.md) | [TASK-47](../../tasks/task-47%20-%20Sprint-opendronemap-initial-package-readiness.md) | [TASK-13](../../tasks/task-13%20-%20Package-the-full-ODM-application-and-validate-integration.md) | [TASK-46](../../tasks/task-46%20-%20Review-opendronemap-package-readiness-evidence.md) |
| [nodeodm (m-12)](../../milestones/m-12%20-%20nodeodm.md) | [TASK-49](../../tasks/task-49%20-%20Sprint-nodeodm-initial-package-readiness.md) | [TASK-14](../../tasks/task-14%20-%20Package-nodeodm.md) | [TASK-48](../../tasks/task-48%20-%20Review-nodeodm-package-readiness-evidence.md) |

### Execution order

- The eleven native component milestones can progress in parallel, subject to
  their own work. No artificial dependency is added merely because ODM executes
  two engines sequentially in its application pipeline.
- TASK-2 belongs to the fpcfilter milestone and blocks its revalidation. TASK-3 is
  shared starter source/license review and blocks both starter review/Sprint gates.
- TASK-13 (ODM implementation) requires all eleven native Sprint gates and TASK-3.
  TASK-14 (NodeODM implementation) requires the ODM Sprint gate. Their existing
  package constraints are retained transitively through those gates.
- TASK-15 remains the shared owner/publisher task, now also requiring both starter
  readiness gates before its end-to-end completion proof. TASK-16 remains shared
  optional platform expansion, requiring the Linux CPU ODM gate as well as TASK-13.
  Neither task is duplicated into every package milestone.

Select a concrete prerequisite task for implementation. A Sprint is a readiness
coordinator, not a new version number, a calendar commitment or an automatic
release train. Do not mark it Done until every prerequisite is actually Done with
acceptance evidence. All package Sprint/work/review tasks remain To Do at creation;
only organization work is completed. No task or milestone grants permission to
flip a release flag, publish, claim new platforms or bypass owner review.

## Existing vs custom packages

Prefer conda-forge for general-purpose libraries. Check forks and feature flags
before using existing entwine/lastools/draco builds: ODM can depend on particular
behavior or features (such as Draco transcoding), not merely a package name.
Keep ODM-specific forks visibly named rather than replacing generic dependencies.

## Build/host/runtime separation

- `pixi.toml`: repository tools only; locked with `pixi.lock`.
- Recipe `build`: Python for the build helper, CMake/Ninja and compiler/stdlib macros.
- Recipe `host`: headers/libraries linked into the target component.
- Recipe `run`: non-inferred runtime requirements; compiler/library `run_exports`
  add ABI requirements. The artifact audit checks the resulting declarations.

`recipes/variants.yaml` deliberately selects GCC 14 and glibc 2.28 sysroot variants.
This is not evidence that the packages/dependencies run on every glibc 2.28 host.
No `-march=native` optimization is added by these starter build scripts.

`build_component.py` installs into rattler's `PREFIX`, never copies a Pixi environment,
and does not treat the outer Pixi `CONDA_PREFIX` as the application prefix.
The enabled starter targets have no external download graph. FPCFilter
explicitly disables its upstream test target and its GoogleTest download; that
test source tree is preserved in the source archive.

## Full ODM integration is separate work

Upstream ODM expects `SuperBuild/install/bin/...`, an OpenSfM source-tree layout,
resources and some root-relative files. A future ODM recipe must:

1. Consume the component packages instead of rebuilding SuperBuild.
2. Patch path resolution and OpenSfM launch/import logic, or deliberately preserve
   a compatible installed layout without file ownership collisions.
3. Package settings/resources and add an `odm` launcher that respects input paths.
4. Review Python/PyPI dependencies as Conda packages, without runtime pip installs.
5. Test installed environments after relocation, then an end-to-end dataset.

Installing the starter tools alone does not provide a photogrammetry engine.

## Platform progression

1. Validate CPU `linux-64` starter recipes.
2. Add the remaining components and a fully tested ODM runtime.
3. Add native Windows and Apple Silicon variants with their own audits/tests.
4. Consider Linux ARM and CUDA separately; do not advertise unsupported variants.

Upstream's current platform list is not a substitute for testing this packaging
layout. Intel macOS is not automatically covered by the CloudCompare matrix.
