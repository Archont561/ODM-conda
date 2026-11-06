# RenderDEM 1.0 build 1: release gate review

Review date: 2026-11-04. This is a bounded technical and evidence review for
linux-64, not legal advice, an owner approval, or permission to publish.
All four configured checks for `renderdem` remain false. The artifact is
retention-limited; a future protected release rebuild can produce different
bytes or resolve different dependencies.

## Exact source and package correspondence

Owner-dispatched [run 41843213137](https://github.com/Archont561/ODM-conda/actions/runs/41843213137)
at commit `8c0619224de35ceef02a4f5863b182a9a4574947` produced
`renderdem-1.0-h873e7db_1.conda` SHA256
`a681202611aa3fa25281055825b75a89e1a256260a954ce69bcd5393a834d94c`
and `source-renderdem-1.0-b1.tar.gz` SHA256
`bf806435fc489b73c059e409b85c159e2b01f3bac7537f996e39d842bd6f8ec1`.
[Run 41844146569](https://github.com/Archont561/ODM-conda/actions/runs/41844146569)
independently verified the artifact ZIP, re-audited the package, retested it
in a fresh environment and verified all 353 source-manifest entries.

Further read-only [run 41853735397](https://github.com/Archont561/ODM-conda/actions/runs/41853735397)
verified those hashes, compared all **352 packaging entries** byte-for-byte
with the recorded Git commit, and rehashed the one upstream source archive.
That archive matches the pinned SHA256
`748cb2839db7d24ee3fdce034e8637829630a9d68ec6561fb76523e25d24af8d`
and contains 11 regular files. The pinned README says `AGPLv3`, the root
license file is AGPLv3 text, and the recipe currently declares the provisional
expression `AGPL-3.0-only AND MIT`. That does not independently establish the
precise grant, provenance of unmarked code, or every applicable obligation.

The same run compared all three expected notice files byte-for-byte against
both the installed payload and `info/licenses` metadata:

| Notice | Compared to | SHA256 |
| --- | --- | --- |
| `renderdem-AGPL-3.0.txt` | Pinned upstream `LICENSE` | `8486a10c4393cee1c25392769ddd3b2d6c242d6ec7928e1414efff7dfb2f07ef` |
| `cxxopts-MIT.txt` | First C-style comment of pinned upstream `vendor/cxxopts.hpp` | `470d8fdce3367cd3a15953cd7c039afc19baf80f6fc38298856a30d7846e4a48` |
| `packaging-MIT.txt` | Packaging root `LICENSE` at the recorded commit | `c15a984a751b806989faa1cd801779c5cccf1ce7aea674f09842cdd30867e435` |

These comparisons establish the examined bytes and provenance paths, not that
all required notices, rights or corresponding source have been identified. The
source manifest does not hash itself or `README-SOURCE.txt`. The bundle captures
the upstream archive and packaging inputs; a reviewer still must decide whether
it meets the actual source-offer obligations for the final distribution.

## Rebuilding from the source bundle (2026-11-04)

Read-only [run 41862738817](https://github.com/Archont561/ODM-conda/actions/runs/41862738817)
retrieved the owner-dispatched build-1 artifact, verified the artifact, source
bundle and pinned upstream archive hashes recorded above, and rehashed all 353
listed source-manifest entries. It staged the **352 packaging files** from the
bundle, safely unpacked the bundled upstream archive, and rebuilt the package
using those inputs. The temporary reconstruction changed the staged recipe's
source declaration from the pinned HTTPS URL and checksum to a local unpacked
source path; no claim is made that the recipe itself was byte-identical to the
original. Conda-forge build, host and retest dependencies were solved and
retrieved online, so this was **not an offline or fully retained-input build**.

The reconstructed package `renderdem-1.0-h873e7db_1.conda` passed its
packaged tests, a fresh isolated retest and package audit. Its SHA256 was
`027dbe9ed25b9fd106a0ed94932ff047ca7a8a0f9224682652ac97c5c96dbb4e`,
which differs from the original candidate's
`a681202611aa3fa25281055825b75a89e1a256260a954ce69bcd5393a834d94c`.
The cause of the difference was not determined; the result does not establish
bit-for-bit reproducibility. The audit reported RPATH `$ORIGIN/../lib` and ELF
NEEDED entries `libpdalcpp.so.20`, `libgomp.so.1`, `libpthread.so.0`,
`libstdc++.so.6`, `libgcc_s.so.1`, and `libc.so.6`. These are bounded binary
evidence, not a complete source, license, ABI or vulnerability review.

This narrows the technical source-reconstruction gap for this candidate: the
bundle's listed packaging files and upstream archive were sufficient for this
one build when substituted into a local-path recipe with externally obtained
dependencies. It does **not** resolve rights, source-offer sufficiency, exact
release dependency closure, or service obligations. The reconstructed binary
and staged sources were discarded; no package was uploaded or published.

## Direct-source provenance follow-up (2026-11-04)

The pinned RenderDEM archive was re-fetched and matched the source SHA256
above. GitHub's path history for that pinned revision reports the root
[`LICENSE` was added in the initial commit](https://github.com/OpenDroneMap/RenderDEM/commit/339ca680c9504a6247f83f0b1512cedecbea9ba6)
on 2023-11-21. Its bytes match the pinned AGPLv3 license file. The initial
README contained only the project heading; the explicit `AGPLv3` README
statement was added by [commit 2cd04f1](https://github.com/OpenDroneMap/RenderDEM/commit/2cd04f17393f9122d21372e48a882925a1fae549)
on 2023-11-27 and matches the statement in the pinned source. The six
non-vendor C++ source/header files were added after the initial license file,
in commits [`6d2ea72`](https://github.com/OpenDroneMap/RenderDEM/commit/6d2ea72b14ecfabee23cfe8db676cd1f7c84ebd4),
[`fb26b89`](https://github.com/OpenDroneMap/RenderDEM/commit/fb26b8995e76080e5c0d7ca8c23e648fcd4f6989)
and [`c92a397`](https://github.com/OpenDroneMap/RenderDEM/commit/c92a397559886e6cd5802959e0b5e1e21f4b078b).
This chronology is evidence about repository history, **not** proof that each
contributor held all rights, that files contain no third-party material, or that
`AGPL-3.0-only` rather than another expression is definitively established.

The vendored `cxxopts.hpp` declares version 3.1.1 and is unchanged between its
RenderDEM import `6d2ea72` and the pinned revision (SHA256
`eca7139d047c5ce06473dccf847ca57dd016b981090831c554ab52a6220b3b58`).
The upstream [`v3.1.1` tag](https://github.com/jarro2783/cxxopts/tree/eb787304d67ec22f7c3a184ee8b4c481d04357fd)
resolves to commit `eb787304d67ec22f7c3a184ee8b4c481d04357fd`;
its `include/cxxopts.hpp` SHA256 is
`2b1acb0d80ddd9ef1e7b197aaee028a55315bdabe7d4b06db4c3771cfcad2ea3`.
A byte comparison found exactly one change: ` noexcept` was added to the
`KeyValue(std::string key_, std::string value_)` constructor. The vendor file
contains the MIT permission and copyright notice verified in the package above.
This comparison identifies a close upstream reference and an observable change,
not the author, provenance, rights or complete obligations of that change.

## Decisions still needed for this exact release

On 2026-11-06 the owner confirmed the proposed RenderDEM license grant.
This limited confirmation does not establish third-party rights or cover the
remaining distribution, source-completeness, native-validation or publication
decisions; no release checks have been changed.

See the [license and source-delivery recommendation](renderdem-license-recommendation.md)
for the proposed package expression and explicit owner/qualified-review boundaries.

- **License grant:** the owner has confirmed the proposed `AGPL-3.0-only`
  grant choice for the included project code. Qualified review should still
  consider whether unmarked code and the modified cxxopts header require
  further provenance or notices.
- **Distribution and source:** decide whether the verified source archive plus
  packaging and scripts, and the intended source location and retention, meet
  the obligations for the actual binary and any service deployment. The
  dependency metadata observed in one solve is not the complete source or
  notice analysis for a future distribution.
- **Native scope:** decide whether synthetic PLY, LAS and compressed LAZ and a
  fresh locked install at a second path provide sufficient intended-workload
  evidence. They do not establish moved-prefix relocation, all LAZ encodings,
  a final released ODM stack or geographical accuracy.
- **Owner authorization:** separately decide all four gates for the exact
  version/build and authorize a release only after the preceding reviews. No
  affirmative decision is implied by a request for review.

The subsequent [runtime closure review](renderdem-runtime-closure-review.md)
retains a complete 66-record candidate solve and examines selected dependency
package metadata; it is not the final release closure.

## Fresh runtime solve and scope

The same [review run](https://github.com/Archont561/ODM-conda/actions/runs/41853735397)
installed the hash-verified build-1 package through a temporary loopback
channel into a fresh Pixi prefix. Its solve contained **66 Conda records**. The
following are installed-record metadata from that one solve, not a lock or
complete assessment of the 66-package dependency closure:

| Package | Version / build | Installed record SHA256 | Recorded license |
| --- | --- | --- | --- |
| `libpdal-core` | `2.10.0 he93afd0_1` | `42ac62b4fa340b33c33c3110917ec520ccd8ddc3f7b06b5174054f56ec605c68` | `BSD-3-Clause` |
| `libgdal-core` | `3.12.2 h4f65170_3` | `7ea31130adc61b2cda72c02f51086deec699bb30ec6f51b37b6c67d02c93d061` | `MIT` |
| `libgomp` | `16.2.0 he0feb66_7` | `92a0bb350c7be6a4eedcb4e111c60aefd176018e6b1c009a6e025dbe9bbcd758` | `GPL-3.0-only WITH GCC-exception-3.1` |
| `libgcc` | `16.2.0 ha9f2e26_7` | `e031634c3a928f9594eba868bc46ef5230d6571a364a0c63215b06c4563bfcea` | `GPL-3.0-only WITH GCC-exception-3.1` |
| `libstdcxx` | `16.2.0 h934c35e_7` | `fa7018298629fc429971fffd6ecba3d27a7b02e4e890d6a93ea01ffebe8cb745` | `GPL-3.0-only WITH GCC-exception-3.1` |

These hashes are installed-record metadata, not independently hashed package
bytes or proof of applicable licenses. The run did not retain its lock, all
records, dependency source archives or environment. The previous fresh package
retest and the recipe's deterministic PLY and uncompressed LAS raster tests
passed; this new install is a separate solve and did not itself run those
fixtures. The audit checks ELF RPATH, not movement of the entire prefix. LAZ,
additional inputs, full ODM-stack integration and geographic accuracy were not
tested in that release-candidate review; the later LAZ experiment is below.

## Compressed LAZ and fresh-prefix locked replay (2026-11-04)

[Private validation run 41856233714](https://github.com/Archont561/ODM-conda/actions/runs/41856233714)
installed the same hash-verified build-1 package plus the separately selected
PDAL 2.10.0 CLI. It generated the existing synthetic PLY and uncompressed LAS
fixtures, converted the LAS to compressed LAZ with PDAL, confirmed the LAS
compression flag, and passed `renderdem` on all three. For LAZ it checked a
65×65 uncompressed Float32 raster, elevation 42 throughout, and the expected
geotransform. It repeated the tests after a `--locked` install in a distinct
project prefix with a fresh HOME and package cache. The locks were byte-identical
and **196** installed Conda identity/version/build/hash/URL records matched.
This is a fresh installation at a second path, **not** moving an already
installed prefix; it does not demonstrate all LAZ variants, full ODM integration,
geographic accuracy or offline reproducibility. The additional PDAL CLI and its
dependencies make this solve different from RenderDEM's 66-record runtime-only
solve above.

The generated lock SHA256 was
`5d42e36a0cdf959044d3edfb8d9bb9355125b4493a4fd63c8adf9521eb078e40`.
The [lightweight metadata artifact](https://github.com/Archont561/ODM-conda/actions/runs/41856233714/artifacts/13338760264)
contains the generated manifest, lock, installed-record inventory, scope note and
checksums; it expires on 2026-11-18. Its localhost channel URL references the
discarded package channel, so the metadata alone is **not replayable**. No
binaries, source archives, fixture inputs or outputs were uploaded. This is a
research solve, not an approved release lock; the future release rebuild and
its external dependencies can differ. To repeat the fixture on a trusted Linux
prefix that has both RenderDEM and the separately installed PDAL CLI:

```sh
pixi run python scripts/validate_renderdem_laz.py --prefix /path/to/prefix
```

For source delivery and a local-source rebuild procedure, see the
[RenderDEM source-offer preparation](renderdem-source-offer.md). It is not a
legal completeness attestation or a public source offer.

## Gate decision: not yet ready to approve

1. **`license_reviewed`: open.** Qualified reviewer and owner need to decide
   unmarked-code provenance, cxxopts terms,
   service/network obligations where relevant, and the applicable terms and
   notices of the actual distributed dependency set. Installed metadata is not
   a legal conclusion; another component's AGPL approval does not transfer.
2. **`source_completeness_reviewed`: open.** Decide and verify the exact
   release's corresponding source, build scripts, modifications, dependencies,
   durable source location, and any service-source obligations. The verified
   archive and local-path reconstruction above are useful evidence, not a
   completeness attestation. The existing release workflow attaches source before the binary.
3. **`native_validation_passed`: open pending owner decision.** Candidate
   builds, audit and isolated tests passed, but the final release rebuild and
   actual dependency solve need verification, and the intended workload and
   relocation coverage need an explicit decision. The LAZ and fresh-prefix
   checks above add bounded evidence, not a moved-prefix or full-stack test. The tested package artifact
   expires 2026-11-18; retain appropriate evidence if needed.
4. **`publishable`: open.** It depends on the preceding exact-candidate
   decisions and explicit owner authorization. No gate change, tag, merge of an
   approval, or publication is authorized by this review.

Recommended sequence: retain and inspect final-commit release evidence and a
versioned dependency inventory; resolve or explicitly decide the identified
license/source and validation gaps with the appropriate reviewer; then request
an explicit owner decision for each gate. Only after a separate publication
authorization should the existing protected per-component release process run.
See also [TASK-42](../backlog/tasks/task-42%20-%20Review-renderdem-package-readiness-evidence.md),
[the four-component gate review](four-component-release-gates.md), and the
[publishing guide](../backlog/docs/guides/doc-7%20-%20Publish-to-the-existing-Prefix-channel.md).
