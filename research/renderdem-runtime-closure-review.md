# RenderDEM build-1 runtime dependency review

This is a bounded technical review, not legal advice or release approval. It
concerns the retained standalone RenderDEM 1.0 build-1 binary, not the future
protected release rebuild or an ODM application environment.

## What was inspected

[Run 42225313740](https://github.com/Archont561/ODM-conda/actions/runs/42225313740)
verified the owner build artifact ZIP SHA256
`cd2671e9f6184102887b08b01f843309210c2fddad7825439bb05e8f7bdd2385`
and extracted the exact RenderDEM package, SHA256
`a681202611aa3fa25281055825b75a89e1a256260a954ce69bcd5393a834d94c`.
It installed that binary in a fresh linux-64 Pixi environment using a disposable
local channel and conda-forge. The resulting runtime solve had **66 installed
Conda records**, including RenderDEM, each with a recorded SHA256 and license
field. The package itself was independently hashed before installation.

The [sanitized metadata inventory](renderdem-runtime-closure-2026-11-06.json)
records all 66 identities, binary URLs, hashes, declared licenses and heuristic
installed notice paths, plus RenderDEM's embedded package metadata. Its JSON
was recovered from run annotations and verified against the run's SHA256
`3267cad41439be16e8101aee4cfb53781978966fe553ed1461fc531a5b8875b8`.
No binary or source artifact was uploaded. Metadata URLs are binary package
locations, not source offers. For 11 selected dependencies the runner also
independently downloaded the exact Conda package, compared its bytes to the
recorded SHA256, and recorded package-index dependencies, `about` fields,
embedded recipe source declarations, and `info/licenses` file hashes. The
remaining dependencies' package bytes were not independently hashed here.

Installed-record notice path matching is a filename heuristic, **not** an
inventory of `info/licenses` or a finding that a notice is missing. Conversely,
a recorded license or notice file does not establish applicable terms, rights,
or complete compliance. Embedded recipe source references and patch names are
leads, not a verified complete corresponding-source set; some use HTTP or
unexpanded templates, and the referenced files were not downloaded here.

## Review findings and priorities

- RenderDEM's embedded runtime constraints include `libpdal-core
  >=2.10.0,<2.10.1`, `libgdal-core >=3.12.2,<3.12.3`, `libgomp >=14`,
  `libstdcxx >=14`, `libgcc >=14`, `_openmp_mutex >=4.5` and glibc
  `>=2.28,<3.0.a0`. Additional broad PDAL/GDAL constraints also appear in
  the index. The package's recorded direct ELF needs and RPATH are in the
  [candidate review](renderdem-release-gate-review.md); this is not a full
  transitive ELF or dynamic-plugin analysis.
- In this solve, PDAL `2.10.0 he93afd0_1` declares `BSD-3-Clause`; GDAL
  `3.12.2 h4f65170_3` declares `MIT`. Their package indices show GDAL among
  PDAL's dependencies, and geos, libarchive and libspatialite among GDAL's.
  These are dependency metadata edges, not proof every library is loaded or
  that package metadata captures all applicable obligations.
- The selected `libarchive` build has a `gpl_` build string, declares
  `BSD-2-Clause` itself, and depends on `lzo`, which declares
  `GPL-2.0-or-later`. The selected `libspatialite` build also has a `gpl_`
  build string, declares `MPL-1.1` itself, and depends on `librttopo`, which
  declares `GPL-2.0-or-later`. `readline` declares `GPL-3.0-only` and `geos`
  declares `LGPL-2.1-only`. These are concrete review leads, **not** an
  incompatibility finding: inspect actual linkage, source, applicable
  license versions and the intended distribution with a qualified reviewer.
- The selected `libgcc`, `libgomp`, and `libstdcxx` records declare
  `GPL-3.0-only WITH GCC-exception-3.1`; their installed records report
  runtime-exception files. The package `info` inspection found no regular
  `info/licenses/` files for those three or for PDAL/GDAL; this does not mean
  their licenses are absent from their payloads or elsewhere. Verify the
  actual license and exception texts, required notices and source obligations.
- The RenderDEM package embeds its recipe and variant values GCC/G++ 14 and
  sysroot 2.28. Those are variant inputs, **not** exact installed build/host
  package records. This inspection could not recover the original complete
  build or host closures, and the final release build has not happened.

## What remains before source-completeness approval

Capture the **final release build's** actual build, host and runtime closures,
archive identities and source/patch references; retain the appropriate evidence
and review any terms that apply to the intended distribution, especially the
leads above. Inspect the full transitive ELF/plugin situation as appropriate
for that scope. Verify corresponding-source contents, instructions and durable
availability for the final binary, and have the owner and a qualified reviewer
decide completeness. A fresh solve of the retained candidate is valuable
candidate evidence but is not a release lock and cannot pre-approve a later
live solve. All four RenderDEM release gates remain false; no publication is
authorized by this review.
