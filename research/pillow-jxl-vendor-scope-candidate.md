# JPEG XL vendor-scope research candidate

**Private research only.** This is not an approved corresponding-source offer,
license clearance or release artifact. The original 1.3.4 project grant and
third-party rights remain unresolved. No release or publication gate is changed.

`prepare_jxl_vendor_scope.py` accepts a previously prepared image-excluded
research tree and the original `jpegxl-src` 0.11.2 crate archive. It verifies
that archive against the Cargo lock SHA-256
`96c328aa9d824459bfb9aef47b8b3defa126df1bbd6fd3a1e59e703911d6dd00`,
compares the vendor crate's complete regular-file hashes and Cargo metadata to
the pinned archive, and allows exactly eight known Cargo-vendor omissions
(`.gitignore`/`.gitattributes` paths). It checks the copied vendor tree again,
removes the 1,488 vendored `libjxl/` file entries, retains eight crate files
including its root LICENSE, and writes sorted removed, retained and omitted
file hashes plus original and modified checksum-metadata hashes to
`VENDOR-SCOPE-MANIFEST.json`. The modified checksum file is explicit; its
original archive checksum does **not** authenticate the modified crate.
Unexpected inputs and symlinks fail closed for this transformation.

The script creates a research build 3 with a relative source path and can write
a deterministic private source archive. It independently checks **only the
`jpegxl-src` crate** against its original archive: the remaining source,
other vendored crates, recipe and build/host inputs require independent
verification and rights review. Treat the output as potentially sensitive
unreviewed third-party source; do not upload or distribute it. The crate
wrapper is retained for Cargo dependency resolution. It may not work with the
vendored feature or other targets and must not be presented as the complete
original crate.

Example on a trusted, provisioned host, using external local paths:

```sh
pixi run python scripts/prepare_jxl_reduced_research.py --source /private/pillow-jxl-plugin.tar.gz --destination /private/prepared
pixi run python scripts/prepare_jxl_vendor_scope.py --prepared /private/prepared --crate /private/jpegxl-src-0.11.2.crate --destination /private/scoped --archive /private/scoped.tar.gz
```

The output archive and destination must not already exist and must be outside
the repository. Preserve the printed archive SHA-256 separately; checking a
hash supplied alongside an untrusted archive is not independent verification.
The original sources must be obtained privately and their rights assessed.
For an optional private ODM trial, use `scripts/private_odm_bundle.py build
--vendor-scope-crate /private/jpegxl-src-0.11.2.crate` with an external
`--destination`, optionally `--runtime-profile reduced` and an external
`--dataset`. This selects JPEG XL `research_vendor_scope_*_3` and distinct ODM
build 5; it does not affect other build modes or publish anything.

## Validation and boundaries

Hosted [run 43078001318](https://github.com/Archont561/ODM-conda/actions/runs/43078001318)
created two transformations and deterministic archives, checked their hashes
match, copied one to a separate receiver directory, discarded producer inputs,
checked the receiver hash, extracted and built/retested the package from that
copy. Archive SHA-256 was
`7a2c2d0f7fab2651249676163880d16f0d699fa936bce6f8a8c0a8708888800d`.
That archive additionally embedded the pinned jxl-oxide independent-decoder
interop test in its recipe, so the hash is specific to that trial and is not a
universal expected archive hash. The receiver was a separate directory in the
**same hosted job**, not an independent recipient or host. The build used
Cargo offline but Conda channels for build/test dependencies. Synthetic tests
and independent-decoder lossless, lossy and JPEG-reconstruction checks passed.
The package SHA-256 was
`6ed7d91560d91ddb972c67a81b5f730da4ed0a1c19ba141367fbd9cd2479335e`;
no research sources, fixtures or binaries were uploaded. Two source archive
hashes matched in this trial, not a general proof of reproducible builds.

A real source offer still needs a separately received and independently checked
bundle, a reviewed legal source scope, all required notices, exact native and
build/host sources and instructions, and verification against the actual
release binary and target workloads. The independent shared `libjxl` dependency
is not eliminated by removing the bundled copy. See the
[notice and source review](pillow-jxl-third-party-source-review.md).

Hosted ODM integration [run 43077912169](https://github.com/Archont561/ODM-conda/actions/runs/43077912169)
used the vendor-scope build in a private 15-package source build, followed by
438-record relocated lock replay, the synthetic codec fixture in the replayed
prefix and Seneca raster/report checks. JPEG XL build
`research_vendor_scope_873e7db_3` had SHA-256
`08c84316a339e4378101e887ec195c67ce9785dbad94b1f5fbc700e39ac9cd72`;
ODM build `hb0f4dca_5` had SHA-256
`7a529bd3ff7397e780990073daad6c54610e37d0d53c55f1b7e6d6944b21158d`.
Both retained `LicenseRef-Unreviewed`, and all private outputs were discarded.
This is a separate build from the source-handoff/interop package above; it
predates the additional post-copy vendor verification guard and does not prove
bit-identical builds, full product coverage, or publication readiness.
