# Independent JPEG XL decoder trial

This local-only linux-64 research test checks one direction: generated images
encoded by the image-excluded pillow-jxl-plugin 1.3.4 research build 2 are
decoded by the separately implemented Rust decoder
[jxl-oxide 0.12.6](https://github.com/tirr-c/jxl-oxide/tree/f8ae722ef2d6b782941c89517d19cfbf605c4a9d),
commit `f8ae722ef2d6b782941c89517d19cfbf605c4a9d` (upstream describes the
project as a pure Rust JPEG XL decoder, licensed MIT OR Apache-2.0). The CLI was
built from that revision with its Cargo lock and `--no-default-features`. It was
used only as a temporary test tool, not included in the research package.

Hosted run [43067105209](https://github.com/Archont561/ODM-conda/actions/runs/43067105209)
built and separately retested the reduced package with the independent decoder
in its test prefix. No package, source or fixture artifacts were uploaded.
The package filename was
`odm-research-pillow-jxl-plugin-1.3.4-research_reduced_873e7db_2.conda`,
SHA-256 `36466c516fefb908046a9f63ce548dd8727d8f75b11b7a7284d743c46c675f38`;
the embedded interoperability script SHA-256 was
`4beaa17891f1a71fc6a71e331228b96659dbf70854897d19838625a59a47308b`.
This trial temporarily embeds the interop test in the local-only recipe, so
that package hash is not the same artifact as prior ODM replay builds. It is
not a reproducibility claim or a release package.

The checks generate nonconstant 17x13 8-bit L, LA, RGB and RGBA pixels, require
exact independent lossless PNG pixels, reconstruct a generated JPEG and require
byte-for-byte identity, and compare a lossy RGB decode against the plugin with
at most 2/255 per channel. This does not test independent encoding, EXIF or ICC
interoperability, animation, high bit depths, adversarial input, upstream
fixtures, broad conformance, or production ODM datasets. Both decoders may
share system libraries for color management, so this is not full implementation
independence for every code path.

To repeat, build/install a verified decoder executable and the reduced research
package in a private environment, then run
`python scripts/jxl_interop_fixture.py --decoder /absolute/path/to/jxl-oxide`
using the package's Python. All test images are created in a temporary directory.
The script expects the CLI interface of the pinned decoder; use only a trusted
executable. The existing `prepare_jxl_reduced_research.py` and
`private_odm_bundle.py` procedures prepare the private plugin.

Publication remains blocked. The
[release review](pillow-jxl-release-review-2026-11-11.md) identifies the
unresolved project-level GPL grant, required third-party notice and provenance
review, and the incomplete source-offer assessment. The reduced candidate alone
omits locked Cargo sources; the vendored research preparation is not a reviewed
corresponding-source offer. Other ODM components have independent gates. Owner
review and approval are required; this trial does not change any release gate.
