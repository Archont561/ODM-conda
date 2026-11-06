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
