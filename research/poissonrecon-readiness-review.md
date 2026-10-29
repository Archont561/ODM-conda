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

## TASK-55 investigation and proposed build 2 (2026-10-29)

A **research-only**, modified `FAST_COMPILE`, `-O0`, system GCC 12 build of the
unpatched Poisson target was linked against the restored development environment.
Its GNU link map selected `libmypng.a` members including `pngread.o`,
`pngrutil.o` and `pngset.o`; `nm` found `png_handle_pCAL`, `png_read_png` and
`png_set_text_2`. `readelf` showed `libjpeg.so.8` and `libz.so.1` among its
NEEDED entries. This establishes inclusion in that reduced, unoptimized binary,
not in the historical package or the full recipe; it does not establish
exploitability.

Build 2 proposes a reviewed source patch: the Poisson target links to host
shared libpng rather than building or linking `libmypng.a`; headers use public
libpng APIs compatible with 1.6, with explicit zlib header inclusion. Both host
and runtime require `libpng >=1.6.59,<1.7`. This version floor is not a claim
that the dependency is immune to all current or future advisories. The bundled
source remains in the original archive and still needs legal/source review.
The builder checks hashes of the patched Makefile and PNG headers, requests a
GNU link map, fails on bundled/static PNG inputs, and requires the selected
`libpng.so` from the isolated host prefix. A path-free link-input inventory and
raw-map SHA256 are packaged as `link-evidence.json`; the raw map remains in the
build tree, not the package. Artifact audit checks this inventory, the
`libpng16.so.16` ELF dependency, declared libpng runtime dependency and RPATH.
These named-input checks do not prove the absence of equivalent code under other
names or establish full dependency provenance.

With the same reduced research configuration, the patched target linked and its
map passed the new guard; ELF NEEDED contained `libpng16.so.16` and no
`libmypng.a` member was observed. The existing generated-sphere fixture passed.
A separate compiled harness exercised the patched source adapter by writing and
reading 8-bit grayscale, RGB and RGBA PNGs, including `nextRows`; the builder
also runs that harness. This harness is not a test that the Poisson CLI exposes
PNG input or output. Neither experiment proves the unmodified full recipe,
compiler wrappers, Conda artifact, ABI or current runtime solve.

Local `pixi run check` and focused Python tests passed. A local source bundle was
assembled from the hash-verified cached archive and contains the patch, guard and
harness; it is preliminary and not an approved corresponding-source offer. The
attempted isolated native package build applied the patch but could not solve its
compiler dependencies: access to conda-forge repodata failed with EOF. It did not
produce a package. Fresh retest and package audit could not run. The owner must
dispatch `build.yml` for Poisson build 2 at the proposed commit, inspect the
resulting package, link evidence and runtime dependencies, and review the
complete source and license/security obligations. All four release gates remain
false; TASK-55 remains open until its native evidence and mitigation criteria are
actually met.

### Native run update

Owner-dispatched [run 40835639537](https://github.com/Archont561/ODM-conda/actions/runs/40835639537)
at `3ffabd94f2b1858b662e8ec66541fe5ac05fe3d5` succeeded after the earlier
local solve failure. Build 2 passed the map guard, PNG adapter smoke, packaged
sphere test, fresh retest, artifact audit and source-bundle steps. The run's
logs report `poissonrecon-odm-13.8-h873e7db_2.conda`, with libpng 1.6.59,
libjpeg-turbo 3.2.1 and libzlib 1.3.2 in both host and fresh test environments;
GCC/G++ 14.4.0 and sysroot 2.28 were used to build it. The log reports source
bundle SHA256 `943f6b5e3e76b1c2a28ec80b8f1213738901aab3f2bd74dafb10029d05237eeb`.
GitHub reports artifact ID `12880822311` and ZIP SHA256
`cd3f7ab8b1fe3ebd3b77bd246b02af5b78035095c8c67b64336915a53ccca7d1`.
The artifact download failed with EOF: its bytes, link inventory, report and
source bundle were not independently inspected or rehashed here and are
retention-limited. The guard only checks named link-map inputs and does not
rule out equivalent code or establish general security. Neither passing CI nor
this evidence is legal, complete-source, security or publication approval.
All release gates remain false and TASK-55 remains open for the remaining
review and evidence.
