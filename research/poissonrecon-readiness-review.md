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

### Independent retained-artifact inspection

A temporary read-only workflow [run 40838038046](https://github.com/Archont561/ODM-conda/actions/runs/40838038046)
downloaded the original artifact, confirmed the reported ZIP SHA256 and
independently re-audited the contained package. Package SHA256:
`0bfffd4b42c1f844ea536d3f17bd81e446f5f5600c47d06340e25a8648cb2f9c`.
It verified the source bundle SHA256 reported above and all 229 manifest file
hashes, including the patch and inspection inputs; a further fresh isolated
package retest passed. The packaged link-input list names `PoissonRecon.o`,
`libpng.so`, `libjpeg.so` and `libz.so` and no `libmypng.a`; its reported raw
map SHA256 is `277e99846f11a1831f4289ec44d68dfbf5087127192119e922c53b34e67a89cf`.
The raw map itself was not retained or independently inspected. The package ELF
NEEDED list includes `libpng16.so.16` and `libjpeg.so.8`; its RPATH is
`$ORIGIN/../lib`. These checks do not establish complete security, source or
license compliance. All release gates remain false.

### IJG source-archive notice gap (2026-10-29)

Re-fetched the exact pinned PoissonRecon archive from GitHub codeload and
verified its SHA256 against `recipes/components.json`. Its 193 regular files
include 59 under `JPEG/`. `JPEG/jpeglib.h` says it is Independent JPEG Group
(IJG) software and refers to an accompanying README for distribution terms;
`JPEG/jversion.h` identifies 6b, 27 March 1998. No README or license file is
present in `JPEG/`. The recipe's current source bundle embeds the entire
original archive, so the bundled JPEG source is a source-distribution issue
regardless of whether its object code enters the linux executable. The current
notice inventory has no IJG 6b README. This is a concrete unresolved gap, not
just a hypothetical need for more review.

A [third-party IJG 6b mirror at immutable commit
`3d8e50d`](https://github.com/jrmwng/jpeg-6b/blob/3d8e50d2fb0d5555d5236570a75f575317b2dc8e/README)
contains a 6b README, SHA256
`4cf9c190f184019b61c36bcc49d4a24ffeb2a838c6f1690d6c4db14cfb2d0478`.
It asks that source distributions include the unaltered README and identify
changes, and specifies an acknowledgement for executable-only distributions.
The mirror is evidence, not established authority for these exact vendored
files. Compared each of the 59 Poisson `JPEG/` files byte-for-byte against the
mirror, comparing `.cpp` to the corresponding `.c`: 49 match, eight differ,
and two (`Makefile`, `jconfig.h`) have no same-named counterpart. Some source
changes are marked inline; a complete change documentation has not been
verified. The matching `jpeglib.h` SHA256 is
`b34b3d9897820302cc23ba60217157f75e03db8c537a7d4703ff0bc8c9fc048b`.
These comparisons support, but do not prove, provenance and applicability of
that README to every modified file.

On linux, `Src/JPEG.h` includes system JPEG headers, and the inspected CI
package needs shared libjpeg.so.8; that does not establish all applicable
binary notice duties or decide terms of the separately resolved libjpeg-turbo
package. TASK-56 tracks confirming authoritative terms and provenance,
documenting changes, fixing the actual source-distribution material, and
reviewing binary notices. Do not distribute an existing source bundle or
publish this package based on the mirror comparison alone.

### Candidate IJG notice remediation for build 3

The [second third-party 6b mirror](https://github.com/Andrewich/jpeg-6b/blob/00bb651cd60996a92f1cacaf70e097219052fb1b/README.md)
has the same README bytes as the first (SHA256
`4cf9c190f184019b61c36bcc49d4a24ffeb2a838c6f1690d6c4db14cfb2d0478`).
This corroborates the text but neither mirror is independently established as
an authoritative record or proof of provenance for all modified vendored files.
Build 3 adds the unaltered text as `JPEG/README` via a pinned source patch and
conservatively includes it in both installed and conda-metadata notices. The
package audit now checks the exact bytes in both locations. The original
upstream archive in the source bundle remains unchanged: the bundle includes
the patch and a standalone readable copy at
`packaging/research/notices/ijg-6b-README.txt`. Upstream source must be patched
to reconstruct the build tree; no claim is made that the original archive
itself contained a README.

The comparison reference is the first mirror's codeload archive at commit
`3d8e50d2fb0d5555d5236570a75f575317b2dc8e`, SHA256
`6b70354c88f27f087661989a0f7a6eeefb4c29d7706d7e2689bf02254fbbc41e`.
`research/notices/ijg-6b-poisson-differences.json` contains JSON arrays of complete textual
unified-diff lines (concatenate the array for each file) for the eight differently-contented matching-name files
(`.cpp` compared to `.c`): jcapistd, jchuff, jcphuff, jdapimin, jdapistd,
jdatadst, jdatasrc, and jmorecfg.h. Its SHA256 is
`7d3f6aec7926b81f01f1aa3f0bb4d3d7ca3e0a60beac0684b541be0ab6d66241`.
The 49 exact matches include C sources renamed to `.cpp`; the two unmatched
names are the Poisson-specific `Makefile` and `jconfig.h`. The diff is a
comparison with a mirror, not evidence of the author's original changes or a
complete proof of every applicable license. It preserves substantial original
IJG text; the unmodified README is kept alongside it. The comparison and README
are packaging source files and thus included in generated source bundles. A
qualified reviewer must determine whether this is sufficient accompanying
change documentation and whether the original archive's distribution plus
supplemental README satisfies the terms.

The linux target selects host headers in `Src/JPEG.h` and previous build 2
needed libjpeg.so.8. For binary distributions, the README calls for the
acknowledgement “this software is based in part on the work of the Independent
JPEG Group” where applicable. The conservative full README includes it; review
whether an explicit acknowledgement in accompanying documentation and/or the
separately distributed libjpeg-turbo environment is required. Adding a notice
does not establish static/dynamic link provenance, a final SPDX expression,
complete dependency obligations or owner approval. The build number bump means
build 2's successful native results cannot validate build 3; no release gate is
changed.

### Earlier JPEG import history (2026-10-29)

The pinned source ZIP SHA256 `88743428a97cbeed7d55e713fcfa42caebbfb7dcb2467d68899bd8feab95364b` was reverified. GitHub's path history for `JPEG/` reports the directory introduced at [514b259](https://github.com/OpenDroneMap/PoissonRecon/commit/514b259540ae995d078d56110f99a37b3cb26639) on 2018-04-15 (the API lists the 58 files including `jconfig.h` as additions); its codeload archive SHA256 is `b1e101338430905e782c0e9f2e3323d6c8e42188deb26578355b7c487690e07f`. Byte comparison against this initial import found that all eight files differing from the examined 6b mirror, and `jconfig.h`, are unchanged in the pinned archive since that import. This locates the changes *before or at* that import, not their author or legal origin. `jconfig.h` says it was generated by `ckconfig.c` and refers to `jconfig.doc`; the 6b mirror has several platform-specific `jconfig.*` files but no same-named `jconfig.h`. The unmatched `JPEG/Makefile` was absent from the first import and GitHub path history attributes its addition to [b97aaf4](https://github.com/OpenDroneMap/PoissonRecon/commit/b97aaf4653ef7c4cac513e47cae0535dfecc8c44), followed by [99e3d90](https://github.com/OpenDroneMap/PoissonRecon/commit/99e3d90da0e798ad4f3f83a675bd343aa3238092). This is a build file for the JPEG library, not evidence that all other changed files originated there.

The observable history and comparisons do not establish an authoritative IJG distribution for the exact files, who made the earlier modifications, or the sufficiency of a source or executable notice. TASK-56 remains open for qualified review; retain the original source plus candidate README and detailed comparison without representing them as cleared for redistribution.

The same initial 2018 import commit is also present in the author-owned
[mkazhdan/PoissonRecon repository](https://github.com/mkazhdan/PoissonRecon/commit/514b259540ae995d078d56110f99a37b3cb26639),
not only the ODM fork. This corroborates the observed upstream history; it does
not identify the source of the JPEG files before that commit or prove that the
compared mirror is authoritative. The missing original README, eight
non-matching files, and generated configuration still require provenance and
terms review; source and binary distribution remain unapproved.

### Comparison with libjpeg-turbo's historical IJG tag

The libjpeg-turbo project's annotated [`jpeg-6b` tag](https://github.com/libjpeg-turbo/libjpeg-turbo/tree/5ead57a34a398aa798f35bd7a6abad19b2e453e2)
points to commit `5ead57a34a398aa798f35bd7a6abad19b2e453e2`; its commit and
annotated tag describe it as the Independent JPEG Group's 6b release. The commit
lists Thomas G. Lane as author and a libjpeg-turbo maintainer as 2015 committer;
the tag is unsigned, and this is a maintained historical reference, not a
cryptographically authenticated original IJG archive. Its codeload tarball
SHA256 is `90834a52eec5929caeaf076bfddf9778759b6ce763678014e46756d263b65f45`.
Its `README` has the same SHA256
`4cf9c190f184019b61c36bcc49d4a24ffeb2a838c6f1690d6c4db14cfb2d0478` as the
candidate already retained in packaging.

Comparing this reference to the 58 files of the first observable Poisson import
(commit 514b259), mapping `.cpp` to same-stem `.c`, yields 49 byte-identical,
eight different and one without a same-named counterpart (`jconfig.h`), the
same eight previously identified against the independent mirror. The later
Poisson-specific Makefile is a 59th file. Selected actual differences include
commented-out `INLINE` in `jcphuff.cpp`; `jdapistd.cpp` changes a return type
from `boolean` to `unsigned char`; and `jmorecfg.h` changes `INT32` and
`boolean` typedefs. Some modified source comments say “Misha changed here”;
those comments identify claimed modifications but do not independently prove
author identity, permission or completeness of attribution. Other edits include
formatting and input/output buffer macro changes. The full retained comparison
remains against the earlier mirror, whose README matches this reference.

This stronger independent reference supports version identification and the
candidate README but does not establish the exact pre-2018 source, authority
for all modifications, or whether source/binary notices and accompanying change
documentation are sufficient. TASK-56 remains open; no release or license gate
is approved by this comparison.

### Private host-JPEG and reduced-source experiments

The native Poisson build guard now requires the link map to name the host-prefix
`libjpeg.so`, rejects named bundled JPEG objects and static JPEG archives, and
requires both `libjpeg.so` in the packaged input inventory and
`libjpeg.so.8` in the executable's `DT_NEEDED` list during artifact audit. It
also retains the existing shared-libpng checks. Synthetic negative cases and a
real GNU toy link-map test exercise the guard. [Run 40974102649](https://github.com/Archont561/ODM-conda/actions/runs/40974102649)
at `c213735` built the ordinary patched source with this guard, passed packaged
and fresh tests and the strengthened artifact audit. The guard covers named
link-map inputs and `DT_NEEDED`, not every compiler dependency, transitive
library, source or license obligation.

In separate [run 40974184592](https://github.com/Archont561/ODM-conda/actions/runs/40974184592)
at `8108563`, the exact 59 original `JPEG/` file names and SHA256s from the
pinned archive were checked in the staged build after patches, then removed;
the candidate IJG README remained. The PoissonRecon target built, passed the
host JPEG/link-map guard, installed and fresh tests and artifact audit. The
original archive was fetched before removal, and the normal source metadata
in this experimental binary does **not** describe this temporary deletion. No
binary, archive or dataset was uploaded. The normal recipe still builds from
the full original archive and the normal corresponding-source bundle embeds
that archive; this experiment is not an approved sanitizing transformation or
corresponding-source distribution. Reviewing all retained source, Windows and
other targets (which reference vendored JPEG), dependency notices and legal
rights remains necessary. No gate or release approval changed.

### Deterministic reduced-source candidate (local only)

`scripts/poisson_reduced_candidate.py` accepts only the pinned original archive
(SHA256 `88743428a97cbeed7d55e713fcfa42caebbfb7dcb2467d68899bd8feab95364b`),
unpacks it with the existing safe single-root archive validator, verifies that
`JPEG/` contains exactly 59 regular files, and creates a deterministic gzip tar
candidate outside the repository. It includes the retained source, an empty
`source/JPEG/` directory, a focused packaging copy and a manifest of retained
file hashes, excluded paths/hashes and original archive identity. The original
archive itself is **not** included. The packaging copy includes the recipe's
candidate IJG README patch and other notices, but omits the separate research
directory (including the full JPEG comparison). This is an intentionally
scoped local-research artifact, not a source offer or a legal conclusion.

[Run 40979099535](https://github.com/Archont561/ODM-conda/actions/runs/40979099535)
at `19b0a10` produced two identical candidate archives, verified their manifest
hashes and empty JPEG directory, and built using a temporary copy of the recipe
pointing at the candidate tree. Installed and fresh tests and normal artifact
audit passed with the host shared-JPEG guard. The candidate SHA256 was
`cba96de67035450ffc8ef016ac9440d5e0680ec2ccb8898465809b60944cc9a0`, recovered
from the build log by [run 40979919908](https://github.com/Archont561/ODM-conda/actions/runs/40979919908).
No candidates, original source or binaries were uploaded. Packaging files are
part of the candidate, so a different checkout or file mode changes its bytes.
The experimental package's usual source metadata still describes the original
archive and **does not describe the reduction**; it is not a release candidate.
Complete corresponding-source and dependency scope, accurate provenance
metadata, other targets, rights and qualified review are still required. The
normal source-bundle command remains unchanged and still includes the original
archive; all release gates remain closed.

For a private local experiment with an already obtained original archive:

```sh
pixi run python scripts/poisson_reduced_candidate.py \
  --source /path/to/original.tar.gz --output /outside/repository/candidate.tar.gz
```

After adding exclusive destination creation, the updated candidate generator
at `910804f` was independently validated in
[run 40982191055](https://github.com/Archont561/ODM-conda/actions/runs/40982191055):
two archives matched, their manifest hashes and absent JPEG tree were checked,
and the private native build, installed and fresh tests, and normal package
audit passed. All outputs were discarded. This does not change the source or
release limitations above.
