---
id: doc-11
title: MVP component scope for ODM fast-orthophoto
type: specification
created_date: '2026-10-27'
---

# MVP component scope for ODM fast-orthophoto

Status: **approved by the project owner and applied to Backlog on 2026-10-27.** TASK-13 no longer depends on TASK-33 or TASK-45. TASK-9 is rescoped to the ReconstructMesh target. TASK-6, TASK-12, TASK-14 and TASK-16 are deferred.

Reference: ODM 3.6.2 at `47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45`. Derived by reading the stage and helper code only. The fast path has not been run end to end.

## 1. What the fast-orthophoto path runs

Pipeline (`stages/odm_app.py`): dataset → split → merge → opensfm → odm_filterpoints → odm_meshing → mvs_texturing → georeferencing → odm_dem → odm_orthophoto → report → postprocess.

With `--fast-orthophoto`, the OpenMVS dense stage is skipped (`opensfm.connect(filterpoints)`). The other stages still run, and they call these native binaries:

| Binary | Called from | Needed for fast path? |
|---|---|---|
| OpenSfM (`opensfm`) | run_opensfm | yes |
| FPCFilter | odm_filterpoints (`--pc-sample`, sampling only if > 0) | yes |
| PoissonRecon-ODM | `screened_poisson_reconstruction` (3D mesh unless `--skip-3dmodel`; 2.5D mesh always, since fast mode uses `method='poisson'`) | yes |
| OpenMVS `ReconstructMesh` | cleanup step inside both Poisson paths (`opendm/mesh.py`) | **yes, even though DensifyPointCloud is skipped** |
| dem2points | `dem_to_points`, used by the 2.5D poisson path | yes |
| renderdem | `create_dem`, always | yes |
| fastrasterfilter | `median_smoothing`, default `apply_smoothing=True` | yes |
| mvs-texturing (`texrecon`) | 2.5D texturing always; 3D texturing unless `--skip-3dmodel` | yes |
| odm-orthophoto | odm_orthophoto stage | yes |
| dem2mesh | `dem_to_mesh_gridded`, only for `method='gridded'` | **no** (fast mode uses poisson) |
| OpenPointClass (`pcclassify`) | `--pc-classify`, default off | **no** (opt-in) |
| OpenMVS DensifyPointCloud | openmvs stage | **no** (skipped in fast mode) |
| NodeODM | server wrapper | **no** for the CLI |

Conda-forge provides PDAL, GDAL, Ceres, OpenCV and CGAL, so they can be dependencies instead of build targets. OpenSfM, OpenMVS, PoissonRecon-ODM and mvs-texturing-odm are ODM forks and must be built from pinned sources.

`--skip-3dmodel` removes the 3D mesh and 3D texturing, so it cuts run time. It does not remove any binary: the 2.5D path still needs PoissonRecon, ReconstructMesh and texrecon.

## 2. Backlog mapping

| Needed for MVP | Task | Status |
|---|---|---|
| ODM application (Python entry point, launcher, integration) | TASK-13 | To Do |
| OpenSfM | TASK-8 (`opensfm-odm`) | To Do |
| FPCFilter | fpcfilter sprint (TASK-25/26/27) | TASK-2 in progress, local patch 0001 |
| dem2points | TASK-22/23/24 | In progress / To Do |
| PoissonRecon-ODM | TASK-7 | To Do |
| OpenMVS, `ReconstructMesh` target only | TASK-9 (`openmvs-odm`), scope reduced | To Do |
| mvs-texturing (`texrecon`) | TASK-10 | To Do |
| renderdem | TASK-11 | To Do |
| fastrasterfilter | TASK-5 | To Do |
| odm-orthophoto | TASK-4 | To Do |
| TASK-3 licensing (gates TASK-13 and TASK-15) | TASK-3 | In progress |

Can be deferred from the MVP: TASK-6 (dem2mesh), TASK-12 (OpenPointClass), TASK-14 (NodeODM), TASK-16 (native variants), and the dense part of TASK-9.

## 3. Gate issue (applied)

TASK-13 currently depends on 12 items: TASK-3 plus the sprint gates for dem2points, FPCFilter, odm-orthophoto, fastrasterfilter, dem2mesh, PoissonRecon, OpenSfM, OpenMVS, mvs-texturing, renderdem and OpenPointClass. Three of these are not needed for the fast path (dem2mesh, OpenPointClass, and the dense OpenMVS build). Applied: TASK-33 and TASK-45 were removed from TASK-13's dependencies. TASK-39 is kept and rescoped to ReconstructMesh.

## 4. Suggested next steps

1. Owner approves the MVP scope, or names components to keep.
2. Rescope TASK-9 to the `ReconstructMesh` target, and record the removal of TASK-6 and TASK-12 from the MVP gates for TASK-13.
3. Build the MVP components in CI, not on the 2-CPU, ~1 GB sandbox.
4. Run one small end-to-end fast-orthophoto dataset with a clear license, once TASK-13 is buildable.
5. Verify the pinned component set against the ODM SuperBuild before the first release.

## 5. Verification still needed

- An actual `--fast-orthophoto` run, to confirm that no other binary is loaded at runtime (for example through `PATH`).
- The ODM SuperBuild's build flags for `ReconstructMesh`, to find out whether it can be built without the full OpenMVS dependency tree.
