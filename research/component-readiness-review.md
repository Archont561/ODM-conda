# Native component readiness: evidence triage

Review date: 2026-10-28. This is an interim technical evidence review, not a
qualified license opinion or approval to publish. It does not close the
packaging, independent review or sprint acceptance criteria. Human owner and
platform decisions remain separate. `recipes/components.json` leaves all four
release checks false for each component below.

## Native validation evidence

| Component | Evidence | Current assessment |
| --- | --- | --- |
| dem2mesh (TASK-6/32/33) | [Run 40686337935](https://github.com/Archont561/ODM-conda/actions/runs/40686337935), commit `21a57c9109725e5ae1713cbd0dd1ad3162080a17`; source bundle SHA256 `ab4713b1b108ea70f1d4ae2eaefc5762e31ff974fa1cfa0c2260043062d0d83e`. | Build, packaged and fresh tests, audit and source bundle passed. Review compiled JMeshLib and other notices, GPL grants, GDAL linkage and actual bundle completeness. |
| poissonrecon-odm (TASK-7/34/35) | Same run and commit; source bundle SHA256 `7e2d03e07eb412b52977b3428eaa3c6db410689556cf262e48ae5e8c2d484e7c`. | Same steps passed. Review bundled libpng/zlib, BSD/MIT notices, security and support for the older static libpng, and full source/dependency obligations. See `poissonrecon-readiness-review.md` and TASK-55; actual final linkage is not established. |
| renderdem (TASK-11/42/43) | Same run and commit; source bundle SHA256 `dba0897029f3cdf310604d3b947e87bb79323c70456ee78ac039c65cb13c7001`. | Same steps passed. Generated PLY-to-raster fixture does not validate LAS/LAZ or full ODM workflows. Review PDAL/GDAL ABI, AGPL and transitive dependency/source requirements. |
| mvs-texturing-odm (TASK-10/40/41) | [Run 40746814931](https://github.com/Archont561/ODM-conda/actions/runs/40746814931), build 2, commit `902550d4f7438d382a2288e064b185a6834e53cf`. | Same steps passed; build 2 includes fail-closed GNU link-map checks for named MVE sfm/SIFT/SURF inputs. Original MVE source contains the files and warnings; the check is not a patent or complete source-rights determination. See `mvs-texturing-license-review.md`. |

GitHub reports successful named build, fresh-retest, audit and source-bundle
steps on both runs. The first produced non-published artifact ID `12815549805`
with GitHub-reported ZIP SHA256
`3b33418c9111591bf5bc83127106b105e803ee4d899190f860c73699c7a411ca`.
The texturing run produced artifact ID `12841144045`, reported ZIP SHA256
`5a92c91c65b56433766eddb739f5db488d4c0cf8403647274aee262c26bdd899`.
These artifacts are retention-limited; this review did not download or
independently inspect their archive bytes, metadata, link map or contents.
Source-bundle hashes for the first run are transcribed from work-task records,
not independently recomputed here. The source bundles are not legal clearance.

## Evidence applicability to current tree

GitHub recursive Git-tree comparisons against main merge commit
`c1e191133b1cbe552b3b413ad4419e2309690382` show the individual files under
`recipes/dem2mesh/`, `recipes/poissonrecon-odm/`, and `recipes/renderdem/`
have the same blob IDs as the three-component run. All files under
`recipes/mvs-texturing-odm/` match the texturing run. This is **not** a claim
that the complete build context is unchanged: common build, functional test,
audit and source-bundle scripts changed since the three-component run; the
source-bundle script changed since the texturing run. Shared component metadata
also changed. Verify the precise impact and rerun the applicable native checks
on a proposed release commit before relying on historic results.

## Remaining gates

For each component: review all actual source inputs, pinned patches, selected
compile/link inputs, runtime dependency versions and notices; verify the exact
package and corresponding-source artifacts and source-offer plan; assess ABI,
relocation and representative functionality; resolve or explicitly retain
legal/security gaps. No component review or sprint is complete merely because
a historical native run passed. Owner/qualified review and a separately
authorized publication remain necessary. OpenMVS/OpenSfM local-only evidence
and blockers are recorded in `open-components-license-review.md`.

## Local batch review (2026-10-29)

At base `ce8776f674dfbd534804f7ba5adb0492be36222f`, independently fetched the
three pinned upstream archives and verified the SHA256 values in
`recipes/components.json`. The current dem2mesh CMake target finds GDAL and
OpenMP and links the vendored JMeshLib; RenderDEM finds PDAL and OpenMP. This
is source-level evidence, not an inventory of the libraries loaded by an
installed package. The current installed RenderDEM fixture exercises both a
synthetic PLY and uncompressed classification-2 LAS grid; the previous table's
PLY-only statement describes the earlier review and should not be read as the
current fixture's coverage. LAZ and an end-to-end ODM dataset remain untested.

The Poisson system-libpng patch applied cleanly to its pinned archive and the
four patched file hashes matched the builder's enforced values. The current
link-map guard excludes named static PNG inputs; an audit gap was found and
fixed so packaged path-free inventories also reject static `libpng*.a` even if
`libpng.so` appears. This does not authenticate a map or prove absence of code
under another name. The previously inspected build 2 package and map inventory
are described in `poissonrecon-readiness-review.md`.

Each declared notice input existed and could be extracted using the current
builder's extraction method (6 dem2mesh, 2 RenderDEM and 14 Poisson inputs).
That is not a file-level or transitive legal review, nor evidence of the exact
notices inside the historical dem2mesh/RenderDEM packages.

Three preliminary source bundles were generated twice from a **dirty** working
tree; hashes matched between repeats and all 232 manifest entry hashes per
bundle were checked. They were temporary local files and are not published or
release artifacts. This uncovered an ambiguity: manifests gave only HEAD even
when included packaging files were modified. The bundler now records ordinary
Git dirty status alongside the base revision; ignored files are not reflected
in Git status, so manifest entry hashes remain the source of truth for bytes.
No legal completeness or correspondence to a previously built binary follows
from these local bundle checks.

A new isolated rattler native build was attempted but stopped at dem2mesh's
compiler solve: conda-forge repodata returned unexpected EOF. The remaining two
recipes did not run in that attempt; no new packages, fresh retests or audits
were produced. The earlier owner-dispatched runs remain evidence for their
specific commits only. For current-commit package evidence, dispatch the existing
multi-component workflow with dem2mesh, RenderDEM and PoissonRecon selected.
The package/source artifact identities, dependency versions and any retained
link evidence should then be inspected; use temporary read-only inspection only
if necessary. Independent review, source obligations, notices, ABI, owner and
security/legal decisions remain open. No release gates were changed.

### Current batch native and artifact evidence

Owner-dispatched [run 40844694283](https://github.com/Archont561/ODM-conda/actions/runs/40844694283)
at `2cc2861a8746589fda4bef57fcf29b1cd60b7f50` passed native build, packaged
tests, fresh retests, audit and source-bundle steps. Its ZIP artifact 12884831960
SHA256 `21526568d7fb39f0070ef929c01c50367881eb81eee1cdf6382cad496b6d2265`
was independently downloaded and checked by temporary read-only inspection
[run 40846497463](https://github.com/Archont561/ODM-conda/actions/runs/40846497463).
The inspection required exactly the three expected packages, audit reports and
source bundles, reran current artifact audits and fresh package retests, and
verified all 232 manifest-listed files in each source bundle. Manifests identify
the build commit above and recorded a clean ordinary Git status.

| Component | Package SHA256 | Source bundle SHA256 | Notable ELF NEEDED |
| --- | --- | --- | --- |
| dem2mesh | `9b16ad6af730ec9e9b9764c572544bddfd217e5900c8c66afb6fa259044a0521` | `fa88d68e3e531983bdd10399e79c4348adcfe0de53cbde9a22a0289d8803e5c6` | `libgdal.so.37` |
| renderdem | `dc33a1fb2de90eabc0ee241f573bd14f09d4d3481f0fb813bd90f792b4f8b895` | `e1f0e18a36c70c9633fcf42b199b3ecbf2bc0aefe2846ea8cc213f8c17182172` | `libpdalcpp.so.20` |
| poissonrecon-odm | `0c9573bf61ab920ee54a2391268adc75dba687ae5a8e2a89bf827a0593b2b6cf` | `92e4663aa1ae4f2e7c41fe9da5f0ca36cd853a16402e751205f53057869ea10d` | `libpng16.so.16`, `libjpeg.so.8` |

All three report RPATH `$ORIGIN/../lib`; the package metadata declares GDAL
>=3.11.5,<3.12, PDAL >=2.10.2,<2.11, and Poisson libpng >=1.6.59,<1.7
respectively. These are dependency constraints, not a complete actual dependency
SBOM or ABI proof. Poisson's packaged link inventory contains `libpng.so` and
no named static PNG archive; the raw map was not retained (reported SHA256
`723c766b3194095604fb8333158ff51c7a64a217883d4c2d5616dccd050124f7`).
The source manifest does not hash itself or README-SOURCE.txt; all entries
listed by the manifest were checked, not certified as complete corresponding
source. Package identities and hashes do not resolve license, security, relocation
beyond the tested environments, LAZ coverage or owner approval. The temporary
inspection workflow and its helper were removed; release gates remain false.

### RenderDEM direct-source license inventory (2026-10-29)

Independently re-fetched the archive at commit
[93502f2e225be0cebcb8663db3bc5058baa3eb1e](https://github.com/OpenDroneMap/RenderDEM/tree/93502f2e225be0cebcb8663db3bc5058baa3eb1e)
and verified SHA256 `748cb2839db7d24ee3fdce034e8637829630a9d68ec6561fb76523e25d24af8d`.
The archive contains exactly 11 regular files: `.gitignore`, `CMakeLists.txt`,
`LICENSE`, `README.md`, `main.cpp`, `point_io.cpp`, `point_io.hpp`,
`render.cpp`, `render.hpp`, `utils.hpp`, and `vendor/cxxopts.hpp`. The
README says AGPLv3, the root LICENSE contains AGPL v3 text, and cxxopts has a
Jarryd Beck 2014–2022 MIT permission/copyright notice. The six non-vendor
C++ files have no explicit license headers; reading the small tree and searching
for copyright/license references found no additional explicit notice there.
This is a direct-tree inventory, **not** proof of copyright ownership,
provenance of unmarked snippets, or that the AGPL-only version choice is
legally settled. The provisional expression remains `AGPL-3.0-only AND MIT`.

CMake compiles `main.cpp`, `point_io.cpp`, and `render.cpp`, includes the
three local headers and cxxopts, and links PDAL, OpenMP and C++ filesystem.
The recipe carries the root AGPL text, the extracted cxxopts first comment,
and MIT packaging notice; the historical source bundle contains the pinned
upstream archive and packaging files. Determine the exact separately solved
runtime package licenses/notices and applicable compiler-runtime exceptions;
inspect the exact proposed artifact and its source offer rather than inferring
compliance from declared package names. Owner and qualified review must decide
AGPL grant/version, network-service implications, notices, and source delivery.
No release check has been changed.

For PoissonRecon, a newly identified missing IJG README in the full upstream
source archive is tracked by TASK-56 and documented in
`poissonrecon-readiness-review.md`. For texturing, the source graph was
re-fetched and all five archive hashes matched; the MVE disclaimer still
requires source/patent review, and the large Eigen tree and exact dependency
closure have not been completely reviewed. Earlier artifact and native results
remain limited to their recorded commits and environments.
