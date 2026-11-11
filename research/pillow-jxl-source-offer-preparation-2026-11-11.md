# JPEG XL source delivery: test-image evidence and reduced-source trial

This is a **local-only research experiment**, not a corresponding-source
offer, legal conclusion or authorization to redistribute. A reduced tree may
not contain all files needed to satisfy the actual license obligations or to
run the upstream test suite. No release recipe or gate is changed.

## Exact input and test-image provenance

The [image inventory](pillow-jxl-test-image-inventory-2026-11-11.json)
(SHA256 `6f23a9c2a71327b39215236a863667b6b77cb64048b2be7eece03e0b90c9ea4e`)
records all 17 regular files under `test/images` from the hash-verified
pillow-jxl-plugin 1.3.4 sdist, including its README. SHA256 values identify the
bytes; Git blob SHA1 was used only to compare against the complete Git tree of
[libjxl/testdata at 73695d303670c90e4d506ea89d9901b081385089](https://github.com/libjxl/testdata/tree/73695d303670c90e4d506ea89d9901b081385089),
the latest commit found before the plugin's v1.3.4 commit. One exact blob
match was found: `metadata/1x1_exif_xmp.jpg` matches
`jxl/jpeg_reconstruction/1x1_exif_xmp.jpg`. This is a Git blob identity match,
not an independent SHA256 verification of the remote file or proof of original
source, author or rights. The other 16 files, including the README, did not
match any blob in that tree; this does **not** rule out derived images, other
revisions or origins. The testdata repository has a root CC-BY-4.0 license,
but repository-level labels do not establish rights for each file or third-party
content.

The pinned plugin's own image README says most samples were copied from
libjxl/testdata under CC-BY-4.0, states `bench.png` is the author's photo
under CC-BY-SA-4.0, and points to a Stack Overflow source for `62AHB.jpg`
under CC-BY-SA-4.0. The author added that README in
[commit a8cb1918](https://github.com/Isotr0py/pillow-jpegxl-plugin/commit/a8cb1918e2f1c0e20e5188dbe496186f106ead43);
`bench.png` was introduced in [e676784f](https://github.com/Isotr0py/pillow-jpegxl-plugin/commit/e676784fe8933f7993f9e751fecf6feabc7cba0c),
and `62AHB.jpg` in [d41efa20](https://github.com/Isotr0py/pillow-jpegxl-plugin/commit/d41efa20b6b62ebbc5c5d3c6d1fff0ccaf43f72e).
Those are useful upstream claims and chronology, not proof the uploader or
project held all rights, nor identification of every derivative or required
attribution. The original Stack Overflow image and its history were not
independently verified here.

## Image-excluded research source

[`jxl_reduced_candidate.py`](../scripts/jxl_reduced_candidate.py) accepts only
the pinned original sdist, uses guarded extraction, verifies the exact file set
and SHA256 for the 16 non-README test-image files, and writes a deterministic,
mode-0600 candidate archive outside the repository. It retains the upstream
image README and records hashes and modes for retained files and hashes for
the excluded paths in a manifest. It rejects unknown or altered test-image
files rather than silently dropping them. It needs the original archive and
**does not grant rights to obtain or redistribute it**, nor establish that the
image-excluded output is an adequate source offer. It does not include the
40 locked crate sources; those and native build inputs are separate.

[Run 43047947149](https://github.com/Archont561/ODM-conda/actions/runs/43047947149)
(job `130616861949`), commit `435a56a`, verified the
candidate manifest and each retained file hash. The original and reduced
research trees were separately built and retested with the existing JXL recipe
and locked vendor preparation; each passed the recipe's synthetic 8×8 lossless
roundtrip. The candidate source archive SHA256 was
`29941b25637e871e8c60a33b1bc65a67322b7d6951700b5574f0c85799be0f52`,
with 22 retained source files and 16 excluded inputs. The unchanged upstream
test suite was **not** run against the reduced source and may require the
removed files.

The two fresh research packages shared an identity but had different SHA256s:
original `847f44881bdd53d4aaa6d56b2befaa63c2b849a349dbe94f7a6fadd5861a8ca2`,
reduced `19e9e83d494e6634c0dbd795699daf9a559d68b6c6660210b5a1d741545455fe`.
Six payload files differed, including the ELF extension, Python bytecode and
build metadata; the causes were not established. This is not binary
reproducibility or proof that removed assets have no effect. A release must
use a distinct immutable identity and independently validated exact binary.
No package, image, original sdist, vendor source or candidate archive was
uploaded, and all temporary outputs were discarded.

## Remaining decisions before distribution

- Determine a lawful source set and whether excluded test fixtures must be
  supplied for the specific distribution; obtain necessary permissions and
  attribution where required. A transformation is not a rights decision.
- Resolve the project's version grant and all retained files' provenance,
  assess the Rust crates and linked native libraries, and prepare complete
  notices and independently retrievable corresponding source, modifications,
  scripts, toolchain requirements and build instructions.
- Build a uniquely identified release recipe from the chosen source set, run
  suitable functional and upstream or substitute tests, audit notices and
  dynamic/static links, and validate against the final ODM lock. Reproducibility
  and source delivery need separate evidence.
- A qualified reviewer and owner must make the final legal and component-gate
  decisions. Do not publish the research package or infer a GPL-free stack.
