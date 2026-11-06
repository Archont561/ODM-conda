# RenderDEM: libspatialite license assessment

Scope: `libspatialite 5.1.0 gpl_h03b4e02_121` from the retained RenderDEM
build-1 candidate's **fresh** runtime solve. This is a technical review, not
legal advice or approval of any release gate. The future release and consumer
solves can differ.

## Source and package evidence

[Run 42232618310](https://github.com/Archont561/ODM-conda/actions/runs/42232618310)
independently retrieved and hash-verified the exact Conda package SHA256
`de6a2bd161084805226e37880deb28724a240dbc9ca315b2f1f5099c5e160b47`
and its recipe-pinned [upstream archive](https://www.gaia-gis.it/gaia-sins/libspatialite-sources/libspatialite-5.1.0.tar.gz)
SHA256 `43be2dd349daffe016dd1400c5d11285828c22fea35ca5109f21f3ed50605080`.
The package declares `MPL-1.1` and `info/licenses/COPYING` matches the root
MPL 1.1 `COPYING` in that source archive, SHA256
`b81965482914858383484d7e63b5de1d0c4647fa7f527e78d4499e4a7b76aab5`.
The embedded recipe lists two Linux patches; their actual bytes were present in
its `info/recipe` but were not validated as a complete corresponding-source
set. No package or source was uploaded by the inspection.

The `src/headers/spatialite/gaiaexif.h` header explicitly offers **MPL 1.1,
GPL 2 or later, or LGPL 2.1 or later** as alternatives for that file. A
heuristic scan of the first 12,000 bytes of C/C++-extension files no larger
than 2 MiB found all three terms in 298 files, GPL-only token patterns in 10, LGPL-only
in one, and no matching terms in 36. Those categories are text matches, not
verified grants, compiled-file counts or a complete rights inventory. In
particular, a missing marker does not imply a missing license. The archive
contains 8,782 regular files in total, including non-code inputs.

## GPL-related control-point code

The source archive's `src/control_points/` contains a separate GPLv2
`COPYING` (SHA256
`8177f97513213526df2cf6184d8ff986c675afb514d4e68a404010521b880643`).
Headers in `gaia_control_points.c`, `grass_crs3d.c`, `grass_georef.c`,
`grass_georef_tps.c` and `grass_crs.h` state GPL version 2 **or later**.
The upstream `src/control_points/Makefile.am` lists those four C files in
`libcontrol_points.la`, and `src/Makefile.am` lists that library in
`libspatialite_la_LIBADD`. The embedded package build script enables GCP and
RTTOPO when its `license_family` build variant is `gpl`; the selected build
identifier contains `gpl`.

The independently extracted shared object `lib/libspatialite.so.8.1.0`
SHA256 `030cd425434ebf429c28a697ccfe377f1ca90f7e359bbb947134a879cdaad3e4`
defines `gaiaCreateControlPoints`, `gaiaAddControlPoint2D`,
`gaiaAddControlPoint3D` and `gaiaFreeControlPoints`. This is strong evidence
that control-point functionality was included, though exported symbol names and
upstream makefiles are not a full binary/source correspondence or link-map
proof. The package also has a `DT_NEEDED` entry for `librttopo.so.1` in the
[earlier ELF inspection](renderdem-runtime-closure-review.md#candidate-dynamic-link-follow-up-2026-11-06).

The inspected package's `info/licenses` contained only the MPL `COPYING`, and
a scan of regular package payload names found no name containing `license`
or `copying`. This is a **notice-coverage concern for review**, not proof that
no relevant notice exists anywhere, or a determination of which party has
which obligations. A separate GPLv2 text is present in the upstream source;
the source and binary of this dependency are **not** included in the RenderDEM
source bundle. Determine how the actual dependency is distributed and obtain
qualified review rather than assuming the package's MPL-only metadata fully
describes its GPL-enabled build.

A separate [alternative-variant assessment](renderdem-alternative-dependency-assessment.md)
shows a bounded PLY/LAS/LAZ test path without the selected GPL libspatialite
and libarchive variants; it is not a complete legal or feature review.

## Recommended disposition

Do not declare this dependency chain cleared based solely on the MPL package
metadata. The sampled tri-license alternatives and GPL-2-or-later control-point
grants are promising inputs for a GPLv3-based compatibility analysis, but they
do not establish the license choice or rights for every compiled file, the
terms of all linked libraries, or complete GPL/AGPL compatibility. Resolve the
36 unclassified source paths and other relevant generated code/inputs according
to the actual build, examine selected patches and attribution, and ask a
qualified reviewer to decide the applicable licenses and notice coverage for
the intended distribution. Consider raising the apparent metadata/notice issue
with the dependency maintainers after validating its scope.

If the intended distribution requires corresponding source or notices for
libspatialite or the combined work, prepare and retain the exact matching
source, patches, build instructions and required notices under the applicable
terms. A reachable upstream URL or a hash alone is not a complete or durable
source offer. Review the actual release build and consumer solve, and separately
consider any applicable network-service obligations. No gate is changed and no
publication is authorized by this assessment.
