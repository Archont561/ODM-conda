# JPEG XL third-party notices and source handoff: research review

## Decision

**Not ready for distribution.** The reduced plugin source is not yet a complete
or reviewed corresponding-source offer, and the research package is not a
reviewed notice package. The following observations narrow the work but do not
resolve the [project grant](pillow-jxl-project-grant-review.md), establish
legal obligations, prove all authorship, or approve publication. No release
gates or license metadata have been changed.

## Locked Rust inputs and notices

The pinned 1.3.4 sdist lock contains 40 registry crates. The earlier
[crate inventory](pillow-jxl-locked-crates-2026-11-11.json) records each exact
version, archive digest, declared license string and root notice hashes. For
the linux-64 `pyo3/extension-module,dynamic` normal/build dependency tree,
six lock entries (`cc`, `cmake`, `crunchy`, `jpegxl-src`, `portable-atomic`,
`shlex`) were not in that particular Cargo tree. The tree is not a link map;
build scripts, proc macros, target/feature differences and source-distribution
choices must be assessed separately. Do not assume every locked crate is in
the binary, or that every crate absent from this tree can lawfully be omitted.

Examples requiring explicit review:

- `jpegxl-rs` and `jpegxl-sys` 0.11.2+libjxl-0.11.1 declare
  `GPL-3.0-or-later`. Their license files explicitly grant version 3 or later,
  with copyright Inflation 2020–2022 and 2020 respectively. Both appear in the
  observed Cargo tree. This is not the plugin author's grant.
- `unicode-ident` 1.0.18 declares `(MIT OR Apache-2.0) AND Unicode-3.0`;
  its root `LICENSE-UNICODE` includes the Unicode copyright and permission
  notice (Unicode, Inc., 1991–2023). The declared conjunction should not be
  silently collapsed into an MIT/Apache choice. Assess the notice against the
  actual distribution and code, not merely the crate's dependency role.
- `target-lexicon` 0.13.2 declares `Apache-2.0 WITH LLVM-exception`;
  `byteorder` declares `Unlicense OR MIT`. Several crates use slash-style
  `Apache-2.0 / MIT` or `MIT/Apache-2.0` declarations. Review the actual
  texts and intended choices; do not mechanically normalize declarations into
  a concluded package license.

In hosted [run 43072194551](https://github.com/Archont561/ODM-conda/actions/runs/43072194551),
all 40 vendored crate package digests matched the previously recorded lock
inventory, all 3,101 files listed in their Cargo checksum metadata matched
those per-file checksums, and every recorded root notice hash matched. This
checks metadata and bytes in that preparation; it is not an independent proof
of authorship, unlisted files, license scope or complete attribution.
A recursive filename scan found 13 additional nested license/copyright
candidates: 11 in `jpegxl-src`'s bundled libjxl tree and two in the `pyo3`
`pyo3-runtime` subtree. They include nested Brotli, Highway, skcms, zlib,
HEVC configuration and APNG-related notices. Filenames alone do not establish
which code is used or what must accompany a particular distribution, and the
scan does not inspect every file header or nested archive.

The same run's relocated private research package had only
`lib/python3.12/site-packages/pillow_jxl_plugin-1.3.4.dist-info/licenses/LICENSE`
in a filename-based license/notice/copyright scan of the package payload and
info files. Its `info/about.json` license remained `LicenseRef-Unreviewed`.
This corroborates the earlier bounded observation, not proof all notices are
absent from other file contents. A release needs a reviewed attribution and
notice plan for the actual artifact, not just this scan.

## Important limitation of the image-excluded source

The reduced candidate removes 16 verified files from the *plugin's*
`test/images` tree. It does **not** make the entire vendored tree image-free
or automatically safe to redistribute. In
[run 43072382566](https://github.com/Archont561/ODM-conda/actions/runs/43072382566),
a suffix scan of `jpegxl-src` found one PNG (Highway's documentation logo),
three PDFs (Brotli/zlib documentation), and four ZIPs in libjxl tools. Their
rights and necessity were not established. In
[run 43072540830](https://github.com/Archont561/ODM-conda/actions/runs/43072540830),
each ZIP's directory listed one `CTestCostData.txt` member; contents were not
reviewed. Other extensions, embedded data, nested archives and files without
matching suffixes were not comprehensively classified. Although `jpegxl-src`
was absent from the observed dynamic Cargo tree, current preparation vendors
all 40 locked crates; it is present in that prepared source. Do not publish the
whole prepared tree assuming the plugin image exclusion cleared these materials.

## Relocated source-build trial and gaps

Run 43072194551 prepared the pinned reduced source, including vendored Cargo
crates, generated `.cargo/config.toml` and modified recipe. It copied the
prepared directory to a new path, removed the original prepared tree and sdist,
rewrote the generated recipe's absolute source path, then built and separately
retested a private package using the existing recipe's `--locked --offline`
Cargo build. The package was
`odm-research-pillow-jxl-plugin-1.3.4-research_reduced_873e7db_2.conda`,
SHA-256 `fd5a0c6a7b29ba2d90fecc30b891d3c572132bf5e7be18a7073bc15d3464a137`.
No sources, packages or test fixtures were uploaded. This demonstrates a
relocated prepared tree can build in that hosted environment without Cargo
fetching during compilation; it does **not** prove an independently delivered
source offer, a fully offline build (Conda dependencies were resolved from
channels), or bitwise reproducibility. The recipe required an absolute-path
rewrite and build/host dependencies were not locked as a complete source set.

For a real offer, the reviewer must decide and document the exact source set
and rights, retain verified project and required crate sources, relevant
modifications, generated config, recipe, tests and build instructions, and
address exact native/build inputs and their source/notice obligations. In
particular, dynamic `libjxl`, Highway, Brotli and the toolchain are separate
inputs; the previous 438-record ODM lock is evidence for that particular
runtime, not proof of this trial's complete build/host closure. A separately
received source bundle should be verified and rebuilt, and the resulting exact
release package's notices and linkage audited before owner gate approval.

## Which vendored materials were needed in a bounded trial?

In [run 43075503011](https://github.com/Archont561/ODM-conda/actions/runs/43075503011)
(job `130714126821`), the fully vendored tree passed `cargo metadata --locked
--offline` with an empty Cargo home. The six crates absent from the earlier
linux-64 normal/build tree were then removed **one at a time** and restored.
For each of `cc`, `cmake`, `crunchy`, `jpegxl-src`, `portable-atomic` and
`shlex`, offline metadata failed with “no matching package named” that crate.
Thus the current unmodified lock and vendored resolution setup needs at least
something providing each package's metadata even when the tested dynamic
build does not compile that crate. This is a Cargo-resolution observation,
not proof the whole content of any particular crate is needed, nor proof of a
legal obligation to supply or omit it.

A second experiment retained the `jpegxl-src` crate wrapper, its root license,
manifest and other files, but deleted its entire bundled `libjxl/` directory
(1,488 paths listed in the generated per-file checksum map; eight entries
remained), and rewrote `.cargo-checksum.json` to remove those paths. On this
same host, `cargo metadata --locked --offline` then succeeded; a distinct
private build `research_vendor_scope_873e7db_3` built and passed the existing
synthetic recipe test and separate retest. Its package SHA-256 was
`ade61cc40177f36644486d711a4b44677a2b448adfc7122e0faf701c3afb06e1`.
No source, fixture or binary artifacts were uploaded. The trim removed the
previously identified `jpegxl-src` nested image, PDF, ZIP and notice files
along with the rest of that `libjxl` subtree; the experiment did not establish
the status of other files anywhere else in the source tree.

This is **not** the original checksum-verified crate: its local vendor checksum
metadata was intentionally changed and its original package checksum alone
cannot authenticate the transformed contents. The trial did not produce a
deterministic, independently verified transformation or an independently
received corresponding-source bundle. `--offline` applies to Cargo; Conda
build and test dependencies still came from channels. The result is limited
to the selected linux-64 dynamic feature set and synthetic tests, not the
vendored feature, other targets, full upstream suite, exact published package,
interoperability or ODM integration. It does not establish which materials a
license requires for any distribution. Native shared `libjxl` remains a
separate input; removing the bundled source subtree does not eliminate its
source and notice obligations.

**Next research step:** if this direction is pursued, implement a fail-closed,
hash-pinned transformation with a distinct research identity, explicit retained
and removed file manifest and original/modified checksum provenance; verify the
remaining notices, reproduce the private build from an independently received
source set, and rerun interoperability and ODM integration. Obtain a qualified
rights/source review and owner approval before any distribution. Do not use
this ad-hoc modified vendor tree as a release source offer.
