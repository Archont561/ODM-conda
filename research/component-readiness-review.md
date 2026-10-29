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

### RenderDEM exact artifact and selected dependency notice review (2026-10-29)

Read-only [inspection run 40862253176](https://github.com/Archont561/ODM-conda/actions/runs/40862253176)
re-fetched and SHA256-checked the historical batch ZIP, selected the unique
RenderDEM package and source bundle, reran the current artifact audit and a
fresh isolated functional retest, and checked all 232 source-manifest entries.
It extracted the hash-verified upstream archive from the bundle and compared
both declared upstream notices byte-for-byte with the installed payload and
Conda metadata: the AGPL root text and cxxopts MIT first comment matched in
both places. The additional packaging MIT notice exists (the audit checks its
presence, not exact content). Package SHA256 is
`dc33a1fb2de90eabc0ee241f573bd14f09d4d3481f0fb813bd90f792b4f8b895`;
source bundle SHA256 is
`e1f0e18a36c70c9633fcf42b199b3ecbf2bc0aefe2846ea8cc213f8c17182172`.
The source manifest excludes itself and README-SOURCE.txt. This confirms exact
bytes of listed files, not corresponding-source sufficiency.

The independent fresh retest solved `libpdal-core 2.10.2 he6b862a_5`,
`libgdal-core 3.13.3 h7fa801c_4`, `libgomp 16.2.0 he0feb66_7`, and
`libgcc`/`libstdcxx 16.2.0` among other dependencies. This is a test solve,
not a lock for a future distribution, the historical build solve, a complete
SBOM, or a guarantee that downloaded packages below were the exact bytes used
by the solver. The temporary inspection separately fetched matching conda-forge
package filenames and recorded SHA256 and license metadata:

| Package | SHA256 | `info/about.json` license | `info/licenses` evidence |
| --- | --- | --- | --- |
| `libpdal-core-2.10.2-he6b862a_5.conda` | `8b31fb486e70cd6a24557f3c6203dd5898acbd87710a97758e4580ac7480165b` | `BSD-3-Clause` | `LICENSE.txt` SHA256 `9ab1261b649806f4884539d5fd49d8f2c9a634762ee52f1ddd2330ef417f5cdf`, matching [PDAL 2.10.2's upstream license](https://github.com/PDAL/PDAL/blob/27008f6241be44585c866a29dfc13bb16d678dab/LICENSE.txt). |
| `libgdal-core-3.13.3-h7fa801c_4.conda` | `03caa0d547a9a193390c4ca67b1738a290c02fdeaf9b4623f2c469fb35b767a2` | `MIT` | `LICENSE.TXT`, `LICENSE_libgeotiff.txt`, `LICENSE_libtiff.txt`; hashes in inspection annotations. GDAL's license inventory includes third-party terms. |
| `libgomp-16.2.0-he0feb66_7.conda` | `92a0bb350c7be6a4eedcb4e111c60aefd176018e6b1c009a6e025dbe9bbcd758` | `GPL-3.0-only WITH GCC-exception-3.1` | No regular `info/licenses/` entries were observed by the inspection; it did **not** inspect the package payload, so this is not a claim that the package lacks license text elsewhere. |

These three package metadata records are not an analysis of all transitive
inputs or the applicability of GCC's exception. Assess their exact versioned
sources, full notices and actual release solve; confirm source-offer and
service obligations, exact grant/version choice, and owner/qualified approval.
No release check is changed.

**Correction to TASK-32:** the owner run initially thought to validate
candidate dem2mesh build 1 actually selected **dem2points**. Inspection of
artifact `12892015321` verified ZIP SHA256
`a04b3651eebe670cb9549904567565f15bf8047c9ef6faf71da720b20c2a67ad` and
found only the dem2points package, audit and source bundle. It provides no
native validation of dem2mesh build 1. The owner must dispatch a run selecting
`dem2mesh`; do not use that run as evidence for it.


### Fresh dem2mesh and Poisson test solves (2026-10-29)

[Read-only inspection run 40865060880](https://github.com/Archont561/ODM-conda/actions/runs/40865060880) verified the previously recorded artifact ZIP hashes, selected one package each, and passed fresh isolated rattler-build retests. The following conda-forge name/version/build rows were captured from test output; local package and virtual specs are not listed. This is a test solve, not a build/host solve or a future release environment. Package archive hashes for the solved entries were not captured from the solver.

- poissonrecon-odm fresh test solve: _openmp_mutex/4.5/20_gnu, bzip2/1.0.8/hda65f42_10, ca-certificates/2026.10.23/hbd8a1cb_0, ld_impl_linux-64/2.46.1/default_hbd61a6d_103, libexpat/2.9.0/hd2095e1_0, libffi/3.7.0/h81df57d_1, libgcc/16.2.0/ha9f2e26_7, libgomp/16.2.0/he0feb66_7, libjpeg-turbo/3.2.1/h7cc23a3_0, liblzma/5.8.3/hb03c661_1, libnsl/2.0.1/hb9d3cd8_1, libpng/1.6.59/h922cc85_0, libpython/3.12.16/ha57cdbe_0_cpython, libsqlite/3.54.1/h0737f62_101, libstdcxx/16.2.0/h934c35e_7, libuuid/2.42.4/hcfc3c73_0, libxcrypt/4.4.38/h280c20c_0, libzlib/1.3.2/h25fd6f3_3, ncurses/6.6/hdb14827_1, openssl/3.6.5/h781a0a9_0, python/3.12.16/h5f976f7_0_cpython, readline/8.3/hd6e31c0_1, tk/8.6.13/noxft_h1df4ec4_4, tzdata/2026e/h5d301ff_0, zstd/1.5.7/hb78ec9c_7
- dem2mesh fresh test solve: _openmp_mutex/4.5/20_gnu, blosc/1.21.6/he440d0b_1, bzip2/1.0.8/hda65f42_10, c-ares/1.34.9/hebe6cf0_0, ca-certificates/2026.10.23/hbd8a1cb_0, freexl/2.0.0/h1f12c17_3, geos/3.14.1/h55b0958_0, giflib/5.2.2/ha257d8a_1, icu/78.3/py310h44b86e0_2, json-c/0.18/hebe6cf0_2, keyutils/1.6.3/h7cc23a3_1, krb5/1.22.2/hbc21106_2, ld_impl_linux-64/2.46.1/default_hbd61a6d_103, lerc/4.2.0/hdb68285_0, libarchive/3.8.9/gpl_h3152399_101, libbrotlicommon/1.2.1/h39a168f_0, libbrotlidec/1.2.1/ha411449_0, libbrotlienc/1.2.1/h018ffa1_0, libcurl/8.23.0/ha042cf0_0, libdeflate/1.25/hd45a770_1, libedit/3.1.20260512/pl5321h373387f_0, libev/4.33/h280c20c_3, libexpat/2.9.0/hd2095e1_0, libffi/3.7.0/h81df57d_1, libgcc/16.2.0/ha9f2e26_7, libgcc-ng/16.2.0/h69a702a_7, libgdal-core/3.11.5/h4f65170_7, libgomp/16.2.0/he0feb66_7, libhwy/1.4.0/h57c4cff_2, libiconv/1.18/h0cb94f2_3, libjpeg-turbo/3.2.1/h7cc23a3_0, libjxl/0.11.2/h174a0a3_1, libkml/1.3.0/haa4a5bd_1023, liblzma/5.8.3/hb03c661_1, libnghttp2/1.70.0/hc5e5977_0, libnsl/2.0.1/hb9d3cd8_1, libpng/1.6.59/h922cc85_0, libpsl/0.23.1/hd9e3e90_1, libpython/3.12.16/ha57cdbe_0_cpython, librttopo/1.1.0/h55b0958_21, libspatialite/5.1.0/gpl_h03b4e02_121, libsqlite/3.54.1/h13e7031_0, libssh2/1.11.1/h6154650_1, libstdcxx/16.2.0/h934c35e_7, libstdcxx-ng/16.2.0/hdf11a46_7, libtiff/4.7.2/hcc2c06a_1, libuuid/2.42.4/hcfc3c73_0, libwebp-base/1.6.0/hd42ef1d_1, libxcrypt/4.4.38/h280c20c_0, libxml2/2.15.4/h7df9aa5_1, libxml2-16/2.15.4/hf3af7cc_1, libxml2-devel/2.15.4/h7df9aa5_1, libzlib/1.3.2/h25fd6f3_3, lz4-c/1.10.0/hee9eb32_2, lzo/2.10/hebe6cf0_1003, minizip/4.2.2/haac24f3_1, muparser/2.3.5/hee9eb32_1, ncurses/6.6/hdb14827_1, openssl/3.6.5/h781a0a9_0, pcre2/10.47/h8b3dc9c_1, proj/9.8.1/he0df7b0_0, python/3.12.16/h5f976f7_0_cpython, readline/8.3/hd6e31c0_1, snappy/1.2.2/h34e00bb_2, sqlite/3.54.1/h9ffa6c4_0, tk/8.6.13/noxft_h1df4ec4_4, tzdata/2026e/h5d301ff_0, uriparser/0.9.8/hac33072_0, xerces-c/3.3.0/h78fed68_2, zlib/1.3.2/h25fd6f3_3, zstd/1.5.7/hb78ec9c_7

Selected matching-name conda-forge package archives were downloaded independently, their metadata and regular `info/licenses/` files inspected (not their payload); these bytes were **not** hash-correlated with solver downloads. They are not a full dependency license or security review.

**poissonrecon-odm**

- `libgomp 16.2.0 he0feb66_7`: metadata `GPL-3.0-only WITH GCC-exception-3.1`; archive SHA256 `92a0bb350c7be6a4eedcb4e111c60aefd176018e6b1c009a6e025dbe9bbcd758`; no regular `info/licenses/` files observed.
- `libjpeg-turbo 3.2.1 h7cc23a3_0`: metadata `IJG AND BSD-3-Clause AND Zlib`; archive SHA256 `2f7d092a3212884825c43814575225fde8a9190611bc0e38c55e0dae45e329ac`; `info/licenses/LICENSE.md` SHA256 `ba6bceebcba0fdd35488477c2cca8c4632ce82c74dbfbc87d886ce6fc4433579`.
- `libpng 1.6.59 h922cc85_0`: metadata `zlib-acknowledgement`; archive SHA256 `c7381be8ef713501f6cd2f5ad473e401f2edeaec3c46788296b8dbf0de165e15`; `info/licenses/LICENSE` SHA256 `bdb0a645ea18c60507d0368379b1ac5474b92255fcc2d115e07486a7672ba526`.
- `libzlib 1.3.2 h25fd6f3_3`: metadata `Zlib`; archive SHA256 `eb8a0db0aa570124f7d2a93d7c7f596e3390df5e047818d873baad32985fc736`; `info/licenses/LICENSE` SHA256 `e32ff4e00d9d94930537635291da39e7e612703334bf6fde8c7f1686fe8a45a2`.

**dem2mesh**

- `libgdal-core 3.11.5 h4f65170_7`: metadata `MIT`; archive SHA256 `516eec194db83718aff80de8ebe7bab7473b8064ff9967c01b97de173ea8311d`; no regular `info/licenses/` files observed.
- `libgomp 16.2.0 he0feb66_7`: metadata `GPL-3.0-only WITH GCC-exception-3.1`; archive SHA256 `92a0bb350c7be6a4eedcb4e111c60aefd176018e6b1c009a6e025dbe9bbcd758`; no regular `info/licenses/` files observed.
- `libjpeg-turbo 3.2.1 h7cc23a3_0`: metadata `IJG AND BSD-3-Clause AND Zlib`; archive SHA256 `2f7d092a3212884825c43814575225fde8a9190611bc0e38c55e0dae45e329ac`; `info/licenses/LICENSE.md` SHA256 `ba6bceebcba0fdd35488477c2cca8c4632ce82c74dbfbc87d886ce6fc4433579`.
- `libpng 1.6.59 h922cc85_0`: metadata `zlib-acknowledgement`; archive SHA256 `c7381be8ef713501f6cd2f5ad473e401f2edeaec3c46788296b8dbf0de165e15`; `info/licenses/LICENSE` SHA256 `bdb0a645ea18c60507d0368379b1ac5474b92255fcc2d115e07486a7672ba526`.
- `libzlib 1.3.2 h25fd6f3_3`: metadata `Zlib`; archive SHA256 `eb8a0db0aa570124f7d2a93d7c7f596e3390df5e047818d873baad32985fc736`; `info/licenses/LICENSE` SHA256 `e32ff4e00d9d94930537635291da39e7e612703334bf6fde8c7f1686fe8a45a2`.

In particular, no regular metadata license files were observed for the matching libgdal-core 3.11.5 and libgomp archives. This does not establish their absence elsewhere in the packages; payloads were not inspected. Obtain and review actual distribution bytes, notices, all transitive obligations and source offers before owner decisions.

## Release review: three GDAL-aligned build-2 candidates (2026-10-29)

This is an engineering evidence and decision checklist, not legal advice, an
owner release approval, or a release. Scope is Linux x86-64 CPU only. The
published build-0 decisions for these components are historical; they do not
turn the four current build-2 release checks on. The current
`recipes/components.json` is authoritative: all four checks remain **false**
for every candidate. Some wording in Backlog doc-6 describes the earlier
publication and must not be read as the current gate state.

### Evidence common to all three

- These are genuine rebuilds with host and runtime `libgdal-core >=3.12.2,<3.12.3`,
  not relabeled build-0 artifacts. Build 0 remains the earlier published build.
  Existing prior owner decisions on each component's license expression are
  recorded in Backlog TASK-3, TASK-28 and TASK-30; those decisions are not
  a new approval of the changed build, dependency solve or release gates.
- Owner-dispatched builds [40908393516](https://github.com/Archont561/ODM-conda/actions/runs/40908393516)
  (fastrasterfilter and odm-orthophoto) and
  [40909632056](https://github.com/Archont561/ODM-conda/actions/runs/40909632056)
  (dem2points) passed. Independent inspection runs
  [40908908691](https://github.com/Archont561/ODM-conda/actions/runs/40908908691)
  and [40910163219](https://github.com/Archont561/ODM-conda/actions/runs/40910163219)
  verified identities and declared upstream notices in package payload and
  metadata, source-bundle hashes, the current package audit, and fresh retests.
  The four-package installation selected GDAL 3.12.2 and PDAL 2.10.0 and checked
  executable presence; individual functional fixtures were tested separately,
  not in that combined prefix. Full ODM integration is not established.
- Artifacts 12910914634 and 12911564893 were not expired on 2026-10-29;
  GitHub reported expiry on 2026-11-12. They are evidence, not a durable
  corresponding-source offer. A release must generate and attach its own exact
  source bundle before uploading its binary, and must not overwrite an existing
  package or release asset. Prior test hashes do not assert byte identity with
  a future rebuild or its dependency solve.
- Tested on GitHub-hosted Ubuntu 24.04, not every Linux distribution. The
  declared glibc 2.28 floor is a toolchain target, not a test on glibc 2.28.
  No other platform is certified. Per-component fixture limitations in the
  original readiness tasks still apply.

### fastrasterfilter 1.0 build 2

- Source: [pinned tree and AGPLv3 README](https://github.com/OpenDroneMap/FastRasterFilter/tree/c5d6c074619e573f641c808f9bdd9d431a0b7e4b);
  vendored [mf2d notice](https://github.com/OpenDroneMap/FastRasterFilter/blob/c5d6c074619e573f641c808f9bdd9d431a0b7e4b/vendor/mf2d/LICENSE)
  identifies MIT. Recipe proposes `AGPL-3.0-only AND MIT`; TASK-30 records the
  earlier owner confirmation of the expression and AGPL section 13 policy.
  Vendored cxxopts and packaging notices also ship.
- Artifact `fastrasterfilter-1.0-h873e7db_2.conda` SHA256
  `52d42537b1ed1ba80a473e4540392d90f49f95e7e6dbb930445c9a3307f859dd`;
  reviewed source bundle SHA256
  `90c3330cf2afeafd6b49cc46779cffaf6682e97918f747cbacd0c36094a95db2`.
- Remaining: review the exact changed GDAL 3.12.2 dependency graph and applicable
  notices/source obligations, recheck license/source completeness and native
  evidence for this build, and obtain the owner's explicit gate decision and
  separate publication authorization. Prior synthetic tests do not establish
  nodata-path behavior or real-world DEM quality (TASK-30).

### odm-orthophoto 0.0.0.dev20250225 build 2

- Source: [pinned tree](https://github.com/OpenDroneMap/odm_orthophoto/tree/55b66d87cc168b8ab287bf10e81d4da0890f84f1)
  and [AGPLv3 license text](https://github.com/OpenDroneMap/odm_orthophoto/blob/55b66d87cc168b8ab287bf10e81d4da0890f84f1/LICENSE).
  Recipe proposes `AGPL-3.0-only AND MIT`; TASK-28 and doc-6 record the earlier
  owner license and network-use policy decision. The upstream license text alone
  does not independently prove an only-versus-or-later grant.
- Artifact `odm-orthophoto-0.0.0.dev20250225-h873e7db_2.conda` SHA256
  `093c55b75981239cb31dccaf66e44e9a4d2addcfe37e31950870451d2f0bb58f`;
  source bundle SHA256
  `651ef9bee5651c94684e0f67fd89e1f29e326c0b06414ce021fbe8dbe206dc20`.
- Remaining: review the changed GDAL and selected OpenCV/native dependency
  graph and its source/notice obligations, recheck source and native evidence
  for this build, and obtain the owner's explicit gate decision and separate
  publication authorization. A generated intermediate orthophoto in a failed
  ODM trial is not final-output or end-to-end validation.

### dem2points 0.0.0.dev20220721 build 2

- Source: [pinned tree](https://github.com/OpenDroneMap/dem2points/tree/4527122615f41044bde0e79850464ed33549ceeb),
  [GPLv3 text](https://github.com/OpenDroneMap/dem2points/blob/4527122615f41044bde0e79850464ed33549ceeb/LICENSE),
  and [BSD three-clause parser notice](https://github.com/OpenDroneMap/dem2points/blob/4527122615f41044bde0e79850464ed33549ceeb/src/CmdLineParser.h).
  Recipe proposes `GPL-3.0-only AND BSD-3-Clause AND MIT`; TASK-23 records the
  earlier owner-confirmed version choice for the initial release. The license
  text by itself does not resolve the upstream grant's version choice.
- Artifact `dem2points-0.0.0.dev20220721-h873e7db_2.conda` SHA256
  `f7077c2eb01f380503d2aa5203e20d78e824a1c4adceaa486f4cbaf22bee8cb0`;
  source bundle SHA256
  `9029351b2cccf4eeca82c580f7fab8c68f0f05410cae36ca003380c9d16a8ce8`.
- Remaining: review the changed GDAL 3.12.2 dependency graph and corresponding
  source/notice obligations, recheck source and native evidence for this build,
  and obtain the owner's explicit gate decision and separate publication
  authorization. Upstream cautions that it has limited testing outside ODM.

### Release decision checklist

For **each** component, before flipping gates: review the exact recipe/source
and bundle, package/installed fixture/audit, actual finalized dependency
identities and licenses, distribution and source availability, target limits,
license obligations and any new upstream changes. Have the owner explicitly
approve each of `license_reviewed`, `source_completeness_reviewed`,
`native_validation_passed` and `publishable` for that build. Review with qualified
counsel where appropriate. `pixi run release-check --tag` for all three current
build-2 tags was executed on 2026-10-29 and correctly blocked all four gates.
Then, only with separate authorization, recheck channel/asset collisions and
current OIDC permissions, use the exact component tag on clean trusted
main HEAD, and let the protected workflow rebuild, retest, audit and provide
source before the binary. No new release has been authorized here.

### Risk-based dependency review of the three build-2 candidates (2026-10-29)

This review is scoped to **distributing the three component packages**, not
republishing their conda-forge dependency packages or a full ODM image. If the
distribution later bundles dependencies, assess that actual distribution and
its corresponding obligations separately. This is not legal advice and does
not grant publication approval.

[Read-only run 40935677599](https://github.com/Archont561/ODM-conda/actions/runs/40935677599)
downloaded and SHA256-verified the two owner-dispatched artifact ZIPs and all
three component packages, re-ran the current audit against each exact build-2
artifact, and independently solved each package with conda-forge. All three
passed audit and solve. The audit checks payload boundaries, identity, metadata,
source reference, notice presence, ELF dependencies and RPATH; it does not
prove the complete legal provenance of everything in a binary. The earlier
independent inspections cited above additionally compared declared upstream
notice bytes in metadata and payload and verified source-bundle hashes and
fresh retests. No binary, source bundle or third-party dependency was uploaded.

The complete fresh-solve package filenames, solver-record SHA256s and declared
license labels are recorded in
[component-build2-dependency-inventory.md](component-build2-dependency-inventory.md).
Each standalone solve selected 63 external packages for dem2points and
fastrasterfilter, and 218 for odm-orthophoto. These are **new no-install
solves**, not the previously tested combined environment, original build
inputs, or a future release solve. Package metadata is an inventory signal,
not proof of applicable rights, actual byte installation, or source-offer
sufficiency. Resolve and review the actual distribution again if it changes.

| Component | Exact audited payload / linkage | Evidence and owner-facing decision |
|---|---|---|
| fastrasterfilter | One executable, four notices (AGPL, mf2d MIT, cxxopts MIT, packaging MIT), `SOURCE.txt`, manifest and fixture. ELF needs GDAL, OpenMP and C/C++ runtime shared libraries; mf2d is compiled in. | Earlier owner accepted the component's AGPL-3.0-only + MIT expression and §13 policy; build-2 notice/source evidence and fresh retest are recorded above. Review changed GDAL/runtime dependency risks below and explicitly decide the four current gates. |
| dem2points | One executable, three notices (GPL, BSD-3-Clause parser, packaging MIT), `SOURCE.txt`, manifest and fixture. ELF needs GDAL and C/C++ runtime shared libraries; parser is compiled in. | Earlier owner confirmed GPL-3.0-only + BSD-3-Clause + MIT for the initial release; verify build-2 source/notice evidence and GDAL/runtime considerations below before deciding each current gate. |
| odm-orthophoto | One executable, two notices (AGPL and packaging MIT), `SOURCE.txt`, manifest and fixture. ELF needs GDAL, OpenCV, OpenMP and C/C++ runtime shared libraries. | Earlier owner accepted the AGPL-3.0-only + MIT expression and §13 policy. In addition to the shared GDAL/runtime considerations, resolve or explicitly assess the OpenCV/OpenVINO signals below before a gate decision. |

These payload boundaries show that separate GDAL/OpenCV shared-library files
are not in the component packages; ELF dynamic dependencies do **not** prove
that no other code was statically linked or compiled in. Header-only Eigen and
other compiled inputs require build-source/notice review. `SOURCE.txt` points
to a release-specific source URL that is not a durable offer until the exact
source asset is actually attached. Earlier CI source bundles are temporary and
expire. None of the above proves minimum-glibc or end-to-end ODM coverage.

**Dependency signals requiring a distribution-specific decision:**

- The standalone solves selected `libgdal-core 3.12.2 h4f65170_3` (lock SHA256
  `7ea31130adc61b2cda72c02f51086deec699bb30ec6f51b37b6c67d02c93d061`),
  declared `MIT`. The separate earlier Python-3.12 combined test selected a
  different build `hc2c0581_0`; do not treat these as identical. GDAL's
  [v3.12.2 license inventory](https://github.com/OSGeo/gdal/blob/v3.12.2/LICENSE.TXT)
  describes additional source-tree notices, so its `MIT` metadata is not a
  complete accounting of bundled code. The fresh solves also include GPL-2.0-
  or-later `librttopo` and `lzo`, GPL-3.0-only `readline`, LGPL packages, and
  GCC runtime packages labeled `GPL-3.0-only WITH GCC-exception-3.1`. These
  are separately resolved packages, not automatically evidence of a license
  conflict or of code copied into the ODM component. Review their applicability
  and obligations if shipping them as part of an assembled distribution.
- The orthophoto standalone solve selected `libopencv 4.12.0
  qt6_py313hbb662ea_612` (lock SHA256
  `4f28a2b341b24804cc60480e46b28986bd29dfe744856fa52d005c16d03dde76`),
  declared `Apache-2.0`; the [upstream 4.12.0 license](https://github.com/opencv/opencv/blob/4.12.0/LICENSE)
  is Apache 2.0. The solve also includes GPL-labeled FFmpeg/x264/x265 and
  LGPL-3.0-only Qt. These are flags for assessing the actual assembled
  distribution, not an assertion of an incompatibility.
- Thirteen `libopenvino` records in that orthophoto solve had **no license
  field in the solver lock**. [Run 40935909195](https://github.com/Archont561/ODM-conda/actions/runs/40935909195)
  fetched and SHA256-verified the exact selected `libopenvino 2025.4.1
  hb56ce9e_1` and `libopenvino-pytorch-frontend 2025.4.1 hecca717_1`
  packages; their `info/index.json` and `info/about.json` also lacked license
  fields and contained no regular `info/licenses/` files. Only the metadata
  archives were inspected, not their payloads or the other 11 packages. The
  upstream [OpenVINO 2025.4.1 root license](https://github.com/openvinotoolkit/openvino/blob/2025.4.1/LICENSE)
  is Apache 2.0, but this does not establish the full package license or its
  third-party contents. Treat the missing metadata and remaining packages as
  unresolved if redistributing that solve; do not infer a restriction merely
  from the absent label.
- The same hash-verified metadata inspection found `MIT` for the selected
  libgdal-core and `Apache-2.0` for libopencv, but no regular `info/licenses/`
  files in their metadata archives. Payload notice locations and complete
  third-party obligations were not inspected. Lack of a metadata file is not
  proof the whole package lacks notices.

**Next decisions:** Owner review of the exact build-2 package and source evidence,
its declared direct-component licenses and distribution scope; evaluate the
flagged dependency obligations for that scope; independently approve each
current `license_reviewed`, `source_completeness_reviewed`,
`native_validation_passed` and `publishable` gate if warranted. Obtain separate
publication authorization and use the source-before-binary protected workflow.
All four gates remain false for each candidate; no release or upload is performed by this review.

### Owner gate decision: fastrasterfilter 1.0 build 2 (2026-10-29)

After reviewing the above evidence and limitations, the owner explicitly
approved all four fastrasterfilter build-2 release gates and authorized its
release. Scope is the standalone Linux x86-64 component, not publication of an
assembled dependency environment or the complete ODM application. Accordingly
only fastrasterfilter's flags are changed; the other candidates remain blocked.
The owner-approved AGPL-3.0-only AND MIT expression and network-use policy
remain applicable. The prior fixture does not cover nodata or establish
real-world DEM quality, and the glibc 2.28 floor is not a tested runtime.
Release must rebuild and retest on the trusted default-branch HEAD, preserve
source-before-binary ordering, and refuse collisions. The earlier package and
bundle hashes describe validation inputs and do not assert identical bytes
from a fresh build. Approval is not legal certification.

### Owner gate decision: dem2points build 2 (2026-10-29)

The owner explicitly approved all four gates for dem2points
`0.0.0.dev20220721` build 2 and authorized publication after the approval PR
passes and merges. Scope is the standalone Linux x86-64 component, not a bundled
GDAL dependency environment or full ODM. The previously approved license
expression is `GPL-3.0-only AND BSD-3-Clause AND MIT`. Native build
[40909632056](https://github.com/Archont561/ODM-conda/actions/runs/40909632056),
independent artifact/source/notice inspection and fresh retest
[40910163219](https://github.com/Archont561/ODM-conda/actions/runs/40910163219),
and dependency inventory
[40935677599](https://github.com/Archont561/ODM-conda/actions/runs/40935677599)
provide the evidence summarized above. The tests ran on Ubuntu 24.04, not a
minimum-glibc 2.28 runtime; generated fixture coverage is not full ODM or
real-world validation. These prior artifacts do not imply byte-identical release
rebuilds. The protected workflow must use the trusted main HEAD, rebuild,
retest, audit and attach corresponding source before binary upload, refusing
collisions. This approval is not legal certification.

### OpenVINO dependency investigation (2026-10-29)

**Why it appeared.** `odm-orthophoto` requires `libopencv` at both host and
runtime. The previously inspected standalone solve selected OpenCV 4.12.0 and
13 OpenVINO 2025.4.1 split outputs (the exact builds and hashes are in the
[dependency inventory](component-build2-dependency-inventory.md)). A
[versioned OpenCV 4.12 feedstock recipe](https://github.com/conda-forge/opencv-feedstock/blob/43c21d0144cd7341492397f54a96c86203ba628f/recipe/meta.yaml)
uses `libopenvino-dev` as a host dependency, and its
[build script](https://github.com/conda-forge/opencv-feedstock/blob/43c21d0144cd7341492397f54a96c86203ba628f/recipe/build.sh)
enables OpenVINO outside the ppc64le exclusion. The
[OpenVINO 2025.4.1 build-1 feedstock recipe](https://github.com/conda-forge/openvino-feedstock/blob/4f61681cf2fc18af6b9ae6b92cc05a1550939243/recipe/meta.yaml)
exports the core, frontends and platform plugins from `libopenvino-dev`. This
explains the packaging mechanism consistent with the 13 records, including GPU
and NPU plugins in a CPU-oriented application. It does **not** prove that this
OpenCV source revision produced the exact solved binary, that all 13 are loaded
or used, or that a later solve will have the same dependencies.

**Why the labels were missing.** The versioned 2025.4.1 build-1 recipe sets
`Apache-2.0` at the top level but lists `license_file` without a `license` field
in each split output. Conda-forge subsequently documented this exact class of
problem in [openvino-feedstock PR #147](https://github.com/conda-forge/openvino-feedstock/pull/147):
missing output-level `license` fields prevented tools from identifying the
licenses. Its [merged patch](https://github.com/conda-forge/openvino-feedstock/commit/f50a776eaea61e82618c85de11c63842d78214c5)
added `Apache-2.0` to each output's `about` section for a **later** 2026.0.0
build. This is strong evidence of a historical metadata omission, not evidence
that the 2025.4.1 packages were rebuilt, relabeled, or individually audited.
The two exact hash-verified older packages inspected in run 40935909195 really
did lack those metadata fields. The other 11 were observed in the solver lock,
not individually inspected.

The older recipe specifies the root `LICENSE` and three `licensing/` notice
files for its outputs. Upstream 2025.4.1 has
[third-party-programs.txt](https://github.com/openvinotoolkit/openvino/blob/2025.4.1/licensing/third-party-programs.txt),
[onednn_third-party-programs.txt](https://github.com/openvinotoolkit/openvino/blob/2025.4.1/licensing/onednn_third-party-programs.txt)
and [runtime-third-party-programs.txt](https://github.com/openvinotoolkit/openvino/blob/2025.4.1/licensing/runtime-third-party-programs.txt).
Recipe intent and upstream notice lists do **not** establish their presence or
completeness in the exact binary payloads. The previous inspection found no
regular `info/licenses/` files in two metadata archives; it did not inspect
payloads, alternate notice paths or the remaining packages.

**Decision boundary.** Publishing the standalone ODM component is distinct
from redistributing an assembled environment containing these packages; neither
a missing label nor an Apache-2.0 label proves a license incompatibility or
fully accounts for third-party obligations. For any assembled distribution,
freeze the actual solve and hashes, inspect every shipped package's metadata,
payload and notices (including dynamically loaded plugins and other OpenCV/GDAL
dependencies), compare with the exact build sources and patches, and obtain the
owner's distribution-specific review. Upgrading/rebuilding OpenCV to select
newer OpenVINO would require a fresh solve, rebuild, tests, audit and review; no
such change or safe drop-in replacement is established here. The separate
odm-orthophoto release gates remain closed; this investigation is not legal
certification or a release approval.
