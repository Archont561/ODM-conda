# RenderDEM: LZO and librttopo distribution review

Scope: the `linux-64` RenderDEM build-1 candidate and the two versions in the
fresh 66-package runtime solve, **not** a legal opinion, a final-release
approval or a blanket review of their entire source trees. The
[runtime review](renderdem-runtime-closure-review.md) records the exact package
identities and the observed ELF dependency names.

## Evidence

[Read-only run 42230699444](https://github.com/Archont561/ODM-conda/actions/runs/42230699444)
independently downloaded the two exact selected Conda packages and verified
their archive SHA256 values against the retained candidate runtime inventory.
It fetched the source archives at HTTPS locations and verified them against
the source SHA256 values recorded in the packages' embedded recipes. It also
compared each archive's root `COPYING` byte-for-byte with the package's
`info/licenses/COPYING`. No package or source archive was uploaded.

| Input | Exact binary identity and SHA256 | Source archive SHA256 |
| --- | --- | --- |
| LZO | `lzo 2.10 hebe6cf0_1003`, `a0a1400198e5302d8367f2ed53437ee3cc41dbc463cb481921ce765578780b7a` | `c0f892943208266f9b6543b3ae308fab6284c5c90e627931446fb49b4221a072` |
| librttopo | `librttopo 1.1.0 h55b0958_21`, `1a3c7f637bfac44e7afee097f08b5ae0c367194f9608daea314ab616dc7757e0` | `5b4002b2b6be1fe59a487cff6edbc81db773dd1e437beb966fac6ac68e849f19` |

Both Conda records declare `GPL-2.0-or-later`. Both source archive root
`COPYING` files match their package `info/licenses/COPYING`, SHA256
`8177f97513213526df2cf6184d8ff986c675afb514d4e68a404010521b880643`,
the GPL version 2 text. Root license text alone does not prove an "or later"
grant. The run observed explicit “version 2 ... any later version” wording
in sampled LZO source, including `include/lzo/lzo1.h`, and in sampled
librttopo source, including `src/rtgeom_api.c`. These samples support the
recorded version choice for those files, but are not a complete file-by-file
license, provenance, binary-to-source or rights audit. The generic automated
regex used in that run did not recognize the grant wording across comment
markers; the specific excerpts were separately inspected rather than treating
its empty result as evidence of absence.

The [dynamic inspection](renderdem-runtime-closure-review.md#candidate-dynamic-link-follow-up-2026-11-06)
observed `renderdem → PDAL → GDAL → libarchive → LZO` and
`renderdem → PDAL → GDAL → libspatialite → librttopo` by matching
`DT_NEEDED`/SONAME names in one installed prefix. It did not observe actual
loader resolution, plugins, all code paths or all licenses in those works.

## Recommendation for the intended distribution

- Treat these GPL-covered dependencies as **real review items**, not merely
  unrelated names in a solver output. Their observed v2-or-later grants may
  permit GPL version 3 to be selected for covered code; that is not, by
  itself, a conclusion that the entire linked distribution is compatible
  with AGPLv3 or that every component grants the necessary rights. In
  particular, examine the actual libspatialite/MPL terms and all applicable
  alternatives and exceptions before reaching a conclusion.
- If distributing a combined or linked work that includes these libraries,
  have a qualified reviewer determine the applicable GPL/AGPL terms and
  comply with the relevant notices and corresponding-source obligations for
  the actual distributed work. Merely providing the RenderDEM upstream source
  bundle does not establish that those obligations are met. If distributing
  only RenderDEM and consumers obtain dependencies separately, assess the
  actual technical and distribution arrangement; separate packages or channels
  do not automatically settle whether works are combined or what duties apply.
- For any dependency source required by that decision, retain and verify the
  matching source, recipe modifications/patches, build instructions and
  applicable notices for the **exact selected builds**. These archives and
  package notices are evidence for the two versions above, not a complete
  source offer for their dependency chains. Do not treat an external source
  URL, binary package URL or recipe hash alone as proof of durable availability
  or complete corresponding source.
- Repeat the dependency and linkage review on the actual release build and
  intended runtime solve. Determine actual source-delivery/retention and, if
  relevant, AGPL network-service obligations with a qualified reviewer.

**Decision boundary:** this review reduces uncertainty about the two observed
grant wordings. It does not resolve all intervening component terms, establish
that the proposed source offer is complete, or approve any gate. All four
RenderDEM release checks remain false, and publication requires separate owner
authorization.
