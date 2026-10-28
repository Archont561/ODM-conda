# PoissonRecon readiness review

2026-10-28. Interim engineering evidence, not a legal opinion, security
clearance, native validation of the current tree or permission to publish.

## Inputs, linkage and security

The pinned upstream archive at commit `97caa6d34d1b05b59888bed019dea89ced74445e`
was downloaded and verified as SHA256
`88743428a97cbeed7d55e713fcfa42caebbfb7dcb2467d68899bd8feab95364b`.
`PNG/png.h` identifies libpng 1.2.29 (2008), `ZLIB/zlib.h` identifies
zlib 1.1.4, and `JPEG/jpeglib.h` identifies JPEG ABI 62 (6b). These are
source/header identifications, not verified versions in the executable.

The reviewed Makefiles build bundled PNG C sources as `libmypng.a`, then
request `-ljpeg -lmypng -lz`. The recipe supplies host libpng, libjpeg-turbo
and zlib and declares libjpeg-turbo and libzlib runtime dependencies. The
source includes bundled PNG declarations and also `<png.h>`; upstream source
contains bundled zlib and JPEG. Command-line libraries do not establish which
archive members survive optimization or what dynamic dependencies are recorded.
No current package, link map, symbol table or resolved host dependency set was
inspected. In particular, do not assert that the vulnerable PNG code or the
bundled zlib implementation is present in the executable, or that it is absent.

Two published advisories identify ranges covering 1.2.29:
[CVE-2011-3048 / GHSA-mmpj-hr4h-5g99](https://github.com/advisories/GHSA-mmpj-hr4h-5g99)
reports potential heap overflow in text-chunk handling before 1.2.49; and
[CVE-2009-0040 / GHSA-m968-rq7m-646j](https://github.com/advisories/GHSA-m968-rq7m-646j)
reports an uninitialized-pointer free in PNG paths before 1.2.35. The pinned
source contains the named functions; patch equivalence and exploitability were
not established. `PoissonRecon.cpp` includes `Image.h`, with PNG reader and
writer support; its grid-to-image code is conditional on `Dim == 2` while the
configured default dimension is 3. This is not proof of reachability or absence
in the optimized executable. Treat the old code as an unresolved security risk,
not as proof of a remotely exploitable binary. TASK-55 tracks final linkage,
mitigation/non-reachability, and current native verification.

## Notice evidence and limitations

The root MIT license and initial BSD notice from `Src/PoissonRecon.cpp` did
not cover all identified copyright variants by name. The PLY headers identify
Georgia Institute of Technology and BSD-style binary-notice conditions; other
headers name additional years and authors. Build 1 adds ten conservative
first-comment notices for distinct identified variants, plus the existing MIT,
BSD, PNG and zlib notices. The extraction inputs were inspected from the
hash-verified archive. This is a notice subset, not a complete file-by-file or
transitive dependency audit; other files, bundled JPEG and the source archive
still need review. Verify both `info/licenses` and installed notice bytes in the
actual current package and source bundle. Owner/qualified review must decide
coverage, expression and redistribution terms.

## Historical versus current evidence

[Run 40686337935](https://github.com/Archont561/ODM-conda/actions/runs/40686337935)
at `21a57c9109725e5ae1713cbd0dd1ad3162080a17` passed build 0, packaged test,
fresh retest, audit and source-bundle steps. The artifact was not independently
inspected and its retention is limited. GitHub's comparison to merge commit
`6ba15ff480b4b61ec8f22b5f16fddae0946bb2ff` shows that the Poisson make branch
remained textually unchanged, while shared builder, functional-test, audit and
source-bundle scripts and workflow selection changed; this is not full context
equivalence. This change deliberately updates the Poisson recipe and notice
metadata to build 1, so the old run cannot validate it. The owner must dispatch
`build.yml` for Poisson on the proposed commit to produce current build, test,
audit and source evidence; independently inspect outputs and resolve TASK-55.
All release checks remain false; native CI passing alone does not close them.
