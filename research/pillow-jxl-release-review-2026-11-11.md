# Pillow JPEG XL research: source and native evidence

Scope: pinned `pillow-jxl-plugin` 1.3.4 research input and fresh linux-64
research builds. This is a bounded technical review, **not** legal advice,
source-completeness approval or permission to distribute. The release artifact,
all corresponding source, exact runtime and build/host closures and their
notice obligations remain to be established. See the broader
[Python input review](python-research-source-review-2026-11-07.md).

## Project provenance and grant

The pinned PyPI sdist SHA256 is
`8ea589fc559ea7c5dfccb42af4d8148f5db508f5f4d4518328bab5a31fcb268e`.
The GitHub v1.3.4 tag points to commit
[`1aaa8a3142aa1d5c3f77e8410e1ddda2d26666ed`](https://github.com/Isotr0py/pillow-jpegxl-plugin/tree/1aaa8a3142aa1d5c3f77e8410e1ddda2d26666ed).
A locally downloaded GitHub archive of that commit had SHA256
`c958464e9d2258b17643adde7b3e69e69d5a98645ad7d05deb2a1ba23a6fc2ea`.
All 36 regular files in that archive matched the sdist's corresponding paths
and bytes; the sdist additionally contained `Cargo.lock` and `PKG-INFO`.
This bounded comparison establishes correspondence for those files, not an
authenticated tag, independent authorship or rights to every included input.

The root LICENSE in both archives has SHA256
`3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986`
and contains GPL v3 text. The upstream [initial commit](https://github.com/Isotr0py/pillow-jpegxl-plugin/commit/54abc4e23dc7a0f36ff89c10c28e49a40dd872c3)
contained an MIT license, and a later [license commit](https://github.com/Isotr0py/pillow-jpegxl-plugin/commit/284a7f01124159d5da8de52a107c4da56fb66ed0)
by Isotr0py says “Update LICENSE to GPLv3.0”. The tag includes the changed
license. That history adds project-level context, but neither the generic GPL
text nor the commit message alone resolves an explicit only-versus-or-later
grant for every project file or the rights of other contributors. A qualified
reviewer should resolve the grant and provenance before setting release metadata.

## Locked Rust source inventory

[Run 43045146192](https://github.com/Archont561/ODM-conda/actions/runs/43045146192)
(job `130606994135`, commit `1f7dd8e`) prepared the recipe's dynamic-feature
source and Cargo vendor tree. It separately downloaded each of the 40 registry
crate archives and checked each SHA256 against the sdist's Cargo.lock. The
[metadata inventory](pillow-jxl-locked-crates-2026-11-11.json) (SHA256
`21b48b27922396dd9f342d1e3504b0f2be1c1f015ed81c3a48c307973ba0373e`)
records the archive hashes, crate `Cargo.toml` license declarations and hashes
of matching root notice filenames. All 40 had at least one root filename
matching the scan. This is not verification of notice contents, all nested or
vendored files, copyright provenance, correct license expressions, or source
completeness. Declarations such as `Apache-2.0 / MIT` are recorded verbatim,
not silently normalized into a legal conclusion. Neither archives nor sources
were uploaded; the inventory was recovered from bounded job annotations and
its SHA256 verified.

The offline Cargo tree for target `x86_64-unknown-linux-gnu`, with
`pyo3/extension-module,dynamic`, includes `jpegxl-rs` and `jpegxl-sys` as
well as build dependencies and proc macros. Six locked crates (`cc`, `cmake`,
`crunchy`, `jpegxl-src`, `portable-atomic`, `shlex`) were not in this specific
normal/build tree. Inclusion in the lock or tree does not prove linked or
executed code; absence under these features does not establish absence under
another target or configuration. All sources needed for an actual build and
corresponding-source plan still need review.

`jpegxl-rs 0.11.2+libjxl-0.11.1` and `jpegxl-sys
0.11.2+libjxl-0.11.1` each declare `GPL-3.0-or-later` in their Cargo manifests.
In [run 43045400660](https://github.com/Archont561/ODM-conda/actions/runs/43045400660)
(job `130607891695`) each crate's root LICENSE expressly granted GPL version 3
or later and attributed copyright to Inflation (2020–2022 and 2020,
respectively). This is evidence of those crate grants, not a conclusion about
the combined work, all files, third-party authors or obligations for the final
binary. The separate test-image terms in the broader Python review remain open.

## Fresh package and notice observation

Run 43045400660 freshly built and retested
`odm-research-pillow-jxl-plugin-1.3.4-research_873e7db_1.conda`
(package SHA256
`793e47c236d104437a8707242d9a64e06b1c189d9aebfc411ef39683d00fba36`),
which is not the earlier integration candidate or a release artifact. It found
one ELF extension with SHA256
`9e8e58b6e7ab44b2b371e6be6735e8bdfb7164bae3321db9cbb72f84f7c47e93`.
`readelf -d` reported `$ORIGIN/../../..` RPATH and DT_NEEDED entries for
`libjxl.so.0.11`, `libjxl_threads.so.0.11`, `libgcc_s.so.1`, `libpthread.so.0`,
`libc.so.6` and `ld-linux-x86-64.so.2`. This is a dynamic metadata observation,
not actual loader resolution or proof of static linkage absence.

A filename scan of the package's info and payload found only the project
`.dist-info/licenses/LICENSE`, which matches the GPL text noted above. The
scan did **not** identify separate crate-named license files; this does not prove
that every relevant attribution is absent elsewhere in package contents.
Before a release, inspect all installed notices and relevant code, resolve
which Rust and native notices must accompany the actual artifact, and test the
final source offer. The research package's `LicenseRef-Unreviewed` metadata and
all relevant release gates remain unchanged. No package, source or fixture was
uploaded in either run.

The later [test-image and reduced-source trial](pillow-jxl-source-offer-preparation-2026-11-11.md)
provides additional provenance and bounded build evidence; it is not a source offer.
