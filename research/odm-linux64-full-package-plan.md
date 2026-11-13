# Linux-64 ODM package: full-scope gap inventory

Target: a linux-64 ODM Conda package, not the `odm-fast-research` package.
The source baseline is ODM 3.6.2 commit `47f41f1f2d09f7c15dff33dd3c15ab29c8a97d45`;
the source archive was downloaded and checked against SHA256
`5bdf8fe81b9ca47714e8a474139fd206b8090ac4315c2f530a58fcaef29cde5e`.
The [machine-readable inventory](odm-full-scope-source-inventory.json) is
reproducible with `python scripts/inventory_odm_full_scope.py /path/to/odm.tar.gz`.
It identifies source markers and pinned Python inputs, **not** resolved Conda
requirements, tested support, rights or source completeness.

## Baseline and feature gaps

The existing package `research/recipes/odm-fast-research` explicitly requires
`--fast-orthophoto` and refuses explicit classification and `--split`. This is
not a comprehensive safety boundary: upstream options can imply other behavior,
including DTM enabling classification. The last full research-stack build and
separate artifact replay tested a fast-orthophoto Seneca path and synthetic PDAL
formats, not general ODM. Earlier point-cloud-in-scene and PLY research tests are
bounded observations, not full dense, classification or 3D production support.

| Feature / source evidence | Gap to full linux-64 package | Required validation |
| --- | --- | --- |
| Dense reconstruction (`opendm/context.py` `DensifyPointCloud`) | Research fast mode skips dense work; reduced OpenMVS must be reviewed for selected capabilities and rights. | Real dataset dense reconstruction; expected point counts and outputs, fresh locked install. |
| Mesh / 3D texturing (`opendm/mesh.py`, `stages`) | `dem2mesh` is used upstream but absent from the fast recipe; registered component gates are false. OpenMVS, Poisson and texturing source and licenses remain open. | Exercise 2.5D and full 3D paths, texturing and output inspection with final packages. |
| Point classification / DTM (`opendm/point_cloud.py`, `opendm/opc.py`, `opendm/config.py`) | SMRF and OpenPointClass model/runtime paths require review; `--dtm` implies classification. Fast wrapper rejects explicit classification only. | Offline/online model acquisition behavior, model provenance, class outputs and DTM on real fixture; dependency and rights closure. |
| Split/merge and remote (`stages/splitmerge.py`, `opendm/remote.py`) | Local split/merge and optional remote NodeODM integrations are not validated by fast test; remote service itself is not supplied by a Conda package. | Multi-submodel local run, merge checks and separately configured remote integration with explicit network/service contract. |
| Point-cloud exports and tiles (`opendm/entwine.py`, `opendm/ogctiles.py`) | Source calls `entwine`, includes an `untwine` fallback and COPC paths; actual solver tools, subprocess paths and supported plugins are not established by the fast recipe. | EPT/COPC/3D tiles output tests and fresh-prefix executable provenance. |
| Image/video and optional inputs (`opendm/context.py`, upstream `requirements.txt`) | RAW/JXL and video support need actual decoder, subprocess, source/license and format coverage. `rawpy` is an upstream direct Python requirement but not an explicit fast recipe run requirement; this does not prove it is absent transitively. | Representative authorized inputs; codec/plugin checks and offline behavior. |
| Projection, reports, export and core dependencies | Pinned upstream `requirements.txt` and fast recipe differ in names and direct dependencies; Conda metadata/transitive dependencies must be mapped and solved rather than copied mechanically. PDAL/GDAL ABI and plugins need final-lock validation. | Inventory all requirements and stage subprocesses, verify imports/plugins, relocated fresh-prefix test and output sanity. |

The [existing release inventory](odm-prefix-release-readiness.md) details the
15 research packages and component gates. Published `fpcfilter`, `dem2points`,
`fastrasterfilter` and `odm-orthophoto` approvals apply only to their exact
published builds; the OpenCV 4.13 orthophoto research variant is different.
Do not overwrite published builds or substitute identities in a tested lock.

## Production recipe contract and implementation sequence

1. Map every upstream Python requirement and every external command by feature,
   including optional data/models and explicit offline/network behavior; select
   reviewed Conda identities and compatible versions. The inventory JSON is a
   starting input, not a complete mapping or a lock. The fast recipe omits
   `dem2mesh`, dense and other feature-specific contracts and cannot be renamed
   into a full package.
2. Resolve OpenSfM assets, OpenMVS source restrictions, texturing and model
   rights, JXL grant and full source/notice obligations; prepare corresponding
   sources for exact artifacts. These are separate from mechanical recipe work.
3. Implement the `odm` production recipe and relocatable launcher only after
   dependencies are identifiable. Package real source/resources, never the
   research wrapper or `LicenseRef-Unreviewed` as a production declaration.
   Use immutable source hashes, linux-64 selectors and a unique build identity;
   do not expose it as a releasable registered component prematurely.
4. Add installed/fresh-prefix tests for help, imports, executable provenance,
   plugin load and resource paths, then dataset tests for each row above. Verify
   moved-prefix behavior without ambient Python/library/PROJ contamination.
   Keep fixture rights and output checks explicit; avoid requiring a network for
   normal offline paths unless deliberately documented.
5. Freeze, retain and independently anchor the final lock, archives, inventory,
   sources and artifacts. Rebuild, run audits, and retest the precise release
   stack. Then owner reviews each component's `publishable`, `license_reviewed`,
   `source_completeness_reviewed` and `native_validation_passed` gates. Merge,
   tagged release and Prefix publication require separate authorization.

## Status of this change

No production recipe was fabricated: the full dependency/source contract and
rights decisions needed to make one honest and runnable are unresolved. The
new inventory tool is deliberately static and fail-closed on source SHA and
expected file/marker changes. It does not inspect every code path, install
packages, or assert feature completeness. Release gates remain unchanged.

The [initial dependency mapping](odm-full-package-dependency-mapping.md)
identifies the missing dense executable, a concrete dem2mesh/GDAL constraint
conflict, optional classification model and point-cloud tools, and compares all
upstream Python requirement names against the fast research recipe. It remains
an incomplete, static mapping rather than a release solve.
