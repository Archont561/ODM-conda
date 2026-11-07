# RenderDEM: alternative dependency solve assessment

Scope: research-only linux-64 fresh installs of the retained RenderDEM 1.0
build-1 package. This is not a legal opinion, an approved runtime lock, a
release-gate decision or permission to publish. The reviewed GPL-variant
concerns remain relevant to the default unconstrained consumer solve.

## Feasibility result

[Run 42235189060](https://github.com/Archont561/ODM-conda/actions/runs/42235189060)
verified the retained candidate ZIP and package SHA256
`a681202611aa3fa25281055825b75a89e1a256260a954ce69bcd5393a834d94c`,
created a disposable local channel, and installed it from conda-forge with
explicit runtime constraints `libspatialite ==5.1.0` build `lgpl_*` and
`libarchive ==3.8.11` build `lgpl_*`. The resulting environment contained
64 Conda records; its [sanitized installed-record inventory](renderdem-alternative-runtime-inventory-2026-11-06.json)
has SHA256 `a407feb383bdfd9bc8d152083b825f9f1ff67f7ce6971ec0c8cc15eaef22ac35`.
The exact candidate passed its installed-prefix linkage and synthetic PLY/LAS
raster tests. No source, binary or fixture artifact was uploaded.

[Run 42235567921](https://github.com/Archont561/ODM-conda/actions/runs/42235567921)
repeated this experiment in a **different solve**, adding the separately
installed PDAL 2.10.0 CLI. It had 194 Conda records and passed the candidate's
installed-prefix linkage, PLY/LAS and generated compressed-LAZ raster tests.
The [sanitized identity inventory](renderdem-alternative-laz-inventory-2026-11-06.json)
was emitted before the separate LAZ step and hashes to
`20f97d76ec30d8102afeca5e77c86e0c847d138e8197213d5c90c0dc35324fa1`;
its test field describes the preceding PLY/LAS step only. Both runs selected:

| Input | Selected identity | Recorded package SHA256 |
| --- | --- | --- |
| libspatialite | `5.1.0 lgpl_hb565e3a_21` | `db58425ae8969c2b1a3027d1c82c5bbfa5163c966f59c9ab7fc1b390a0bc50f4` |
| libarchive | `3.8.11 lgpl_hee3b6c9_0` | `ef86dba72bcad4a7c522bb9d8974d7b85ed6d886c5ff6c41ee27a2661d4fd626` |
| libpdal-core | `2.10.0 he93afd0_1` | `42ac62b4fa340b33c33c3110917ec520ccd8ddc3f7b06b5174054f56ec605c68` |
| libgdal-core | `3.12.2 h4f65170_3` | `7ea31130adc61b2cda72c02f51086deec699bb30ec6f51b37b6c67d02c93d061` |

The recorded package SHA256 values are installed-record metadata, not newly
independently hashed dependency archive bytes. The candidate itself was hashed
before installation. Neither solve installed LZO or librttopo. `readelf` on
both selected variant shared objects found no `liblzo2.so.2` in libarchive's
DT_NEEDED and no `librttopo.so.1` in libspatialite's DT_NEEDED. In the 194-record
run, `nm -D --defined-only` found no dynamic symbol containing `ControlPoint`
in the selected libspatialite object. These are bounded observations, not proof
that equivalent code is absent or that no other dynamic or static path exists.

## Trade-offs and remaining decisions

- The [libspatialite feedstock](https://github.com/conda-forge/libspatialite-feedstock/blob/4aa5243b6a449ff4e1810437f7d378fcb81c0c63/recipe/meta.yaml)
  defines `lgpl` and `gpl` build families; its build script disables RTTOPO
  and GCP for the non-GPL variant. The [libarchive feedstock](https://github.com/conda-forge/libarchive-feedstock/blob/8ec0f3f4dca7e77d03cbd037c56bc643cd1f75d2/recipe/meta.yaml)
  includes LZO in the GPL variant and constrains it out in the alternative.
  These current feedstock revisions explain the policy but are not independently
  proven to be the historical recipe commits that built the selected packages.
- The alternative removes features: RTTOPO topology, GCP and libarchive's LZO
  integration. Passing a point-cloud fixture does not establish that an ODM
  deployment or other GDAL consumers do not need them. Test the intended
  stack and data before adopting it.
- This is **not a GPL-free environment**: for example the installed `readline`
  record declares `GPL-3.0-only`, and compiler runtime exceptions and other
  dependency terms still need review. The package label `lgpl` is a variant
  identifier, not a complete license or notice audit. Original dependency
  source archives can still contain disabled GPL code and carry their own terms.
- No recipe or channel constraints were changed. The existing RenderDEM
  package does not enforce these alternative variants, so an unconstrained
  solve may select the GPL builds again. An actual switch would require a
  reviewed dependency policy/lock and fresh build, ABI, feature, legal and
  source-offer decisions for the intended distribution. A different dependency
  solve is not a substitute for the original review or prior approvals.
- A qualified reviewer must assess applicable notices, corresponding source,
  provenance, compatibility, source availability and service obligations for
  the final distribution. The actual protected release build's build/host
  inventory and final consumer runtime environment are not yet known. All four
  RenderDEM release gates remain false.

The alternative is technically promising for the tested narrow workloads, but
adoption is a scope and distribution decision, not an automatic legal fix.

## Private ODM integration trial

[Run 42237636247](https://github.com/Archont561/ODM-conda/actions/runs/42237636247),
job `127959326245`, tested commit `bb3890b` on linux-64. It freshly built the
15-package private research stack, constrained the runtime solve to
`libspatialite ==5.1.0 lgpl_*` and `libarchive ==3.8.11 lgpl_*`, and checked
that neither `lzo` nor `librttopo` was installed. The 438-record solve selected:

| Package | Version and build | Installed-record SHA256 |
| --- | --- | --- |
| libspatialite | `5.1.0 lgpl_h6633a9c_19` | `2919611dcd23ff43fb9d0e6cb9b12beb8ef5933ebe963308eb327f572ba05fd4` |
| libarchive | `3.8.11 lgpl_hee3b6c9_0` | `ef86dba72bcad4a7c522bb9d8974d7b85ed6d886c5ff6c41ee27a2661d4fd626` |
| libgdal-core | `3.12.2 he63569f_2` | `564d9e27f9cb3eae53a945a70c25b92f22f74a27b450dc166a255964623b4383` |
| libpdal-core | `2.10.0 h9d23c72_0` | `c43a137e3b537f8842b3c850e9a319b9cae0ab59143b4fc7358495892e61d279` |
| renderdem | `1.0 research_873e7db_1` | `eb26cc1559310afa996b8e8ccebec56164095686b392707b0305f8360fe4b929` |
| odm-fast-research | `3.6.2 hb0f4dca_3` | `73ad8037c8a6cab16edb340d39f20fb30405ce2fc2898d43590a1a0cd9618d59` |

The relocated bundle's locked replay and the Seneca fast-orthophoto pipeline
(`--skip-3dmodel`), including raster sanity and nonempty report checks, passed
with dataset commit `9220acfdca75cc5e2dd6d27fe48550c5ae0877f2`. The job
reported success and uploaded no artifacts; private inputs, binaries, lock and
outputs were discarded. Only the six identities above were preserved in its
annotation, not the complete 438-record inventory. Package hashes are recorded
metadata, not independent archive verification. Build/host environments were
solved separately and were not constrained to these variants. This freshly
built research RenderDEM is not the retained candidate tested above, and this
Seneca run alone does not validate RTTOPO, ground-control points, LZO, other
datasets, all ODM features or production distribution. See the later COPR trial below. No release gates were changed.

## Feature probes and dependency-policy review

[Run 42395378785](https://github.com/Archont561/ODM-conda/actions/runs/42395378785)
compared two **isolated** linux-64 solves, not the ODM solve. The reduced solve
selected `libspatialite 5.1.0 lgpl_hc01a4aa_22` (installed-record SHA256
`e77c0550ff161b972d1664490cbda95cd12e6c6cc3fa606c0f424742e6b7b559`)
and `libarchive 3.8.11 lgpl_hee3b6c9_0` (SHA256
`ef86dba72bcad4a7c522bb9d8974d7b85ed6d886c5ff6c41ee27a2661d4fd626`).
SpatiaLite's `HasRtTopo()` returned 0 and `nm -D --defined-only` found no
`ControlPoint` symbols. `archive_read_support_filter_lzop` returned -20
(`ARCHIVE_WARN`), reporting that an external `lzop` program would be used for
decompression; an actual archive and availability of that program were not
tested. The solve contained neither LZO nor librttopo.

The comparison solve used `libspatialite 5.1.0 gpl_h2988700_122` (SHA256
`d4e6bb1a10f4f97d60ce534a3313d268f50ba1fd7772d35121043dc166596305`)
and `libarchive 3.8.11 gpl_h3152399_100` (SHA256
`0b13f801fa48194d18819b0dc1aac182ea88089f81b87af2d3bacd69d3ff5cc5`),
with LZO and librttopo installed. `HasRtTopo()` returned 1, the four
`gaia*ControlPoint*` symbols listed in the spatialite review were present,
and registering the libarchive lzop reader returned 0. This is a capability
probe, not a topology operation, control-point transformation, compressed-file
roundtrip or license determination. These are different builds from the ODM
integration and earlier exact-candidate solves; package SHA256s are installed
record metadata. No source or binary artifacts were uploaded.

**Policy recommendation, not a release decision:** for the narrowly tested
fast-orthophoto product, prefer a reviewed *consumer lock* explicitly selecting
these variant families, rather than assuming an unconstrained RenderDEM
package will enforce them. Retain the final exact lock, complete sanitized
inventory, package hashes and channel provenance with the proposed distribution;
independently verify archive bytes and repeat replay and workload tests against
those exact binaries. Decide separately whether all consumers should have
package-level constraints: such a constraint changes the dependency contract
and can exclude legitimate topology, SpatiaLite control-point or LZO users.
An alternative solve has different ABI and features and cannot inherit an
approval for another build. A variant family wildcard alone does not freeze an
identity, and independent build/host solves need their own inventory and review.

The absence of SpatiaLite's control-point implementation should not be confused
with ODM's own ground-control-point processing. Neither `lgpl` labels nor these
probes establish a GPL-free stack, sufficient notices or corresponding source.
A qualified reviewer and owner must assess the final actual source and runtime
closure, provenance, obligations and source delivery; OpenMVS and OpenSfM
research-source restrictions remain separate blockers. A release needs its own
validated binaries, supported dataset/feature scope, gate decisions and
separate publication authorization. No gates have changed here.

## COPR ground-control-point integration

[Run 42397256516](https://github.com/Archont561/ODM-conda/actions/runs/42397256516)
(job `128477188727`, commit `52129ed`) repeated the private 15-package
source build and relocated locked replay on linux-64 with the same alternate
variant family constraints. The 438-record solve again selected
`libspatialite 5.1.0 lgpl_h6633a9c_19` and `libarchive 3.8.11
lgpl_hee3b6c9_0`, and excluded `lzo` and `librttopo`. The selected
`libgdal-core` and `libpdal-core` identities and installed-record hashes match
the Seneca trial above; freshly built `renderdem 1.0 research_873e7db_1` had
SHA256 `9f388f60644cc3af71d475ea6fab7f4f76b21202b1850466fd9b02c5048e665b`,
and `odm-fast-research 3.6.2 hb0f4dca_3` had SHA256
`8ebd9017d0acb68227422a8e1940cebb53b49ca83d37009b3b0c7144edb535e9`.
Only those six identities were preserved; hashes are installed-record metadata.

The [COPR dataset](https://github.com/OpenDroneMap/odm_data_copr/tree/97cd18478ca1885f5713a11bf98d4bf96308b399)
at commit `97cd18478ca1885f5713a11bf98d4bf96308b399` was processed with
`--fast-orthophoto --skip-3dmodel --matcher-type flann --gcp` pointing to
its `gcp_list.txt`. It passed raster sanity and the nonempty report check,
and exported eight ground control points, at least one with observations. This
is evidence of ODM's own GCP pipeline, not a test of SpatiaLite's disabled
control-point functionality or an independent geospatial accuracy assessment.
The dataset declares CC BY-SA 4.0 and credits Michele M. Tobias and Alex
Mandel; the run discarded dataset, private inputs, binaries and outputs, and
uploaded no artifacts. Attribution and license declaration are not an
independent rights verification.

The [first attempt 42395352751](https://github.com/Archont561/ODM-conda/actions/runs/42395352751)
failed before reconstruction: with no GPS metadata, ODM defaulted to
BoW/WORDS matching, which the scoped OpenSfM guard intentionally rejects
because vocabulary assets are omitted. The retry explicitly selected FLANN;
the guard was not relaxed. Both results are bounded to research builds,
selected dataset and flags, and do not establish support for arbitrary ODM
features or a final distribution.
