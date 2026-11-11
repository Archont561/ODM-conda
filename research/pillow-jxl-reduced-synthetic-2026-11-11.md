# Image-excluded JPEG XL: scoped research candidate

This is a private linux-64 research trial, **not a release, legal clearance, source
offer, or approval to publish**. The existing release gates remain unchanged.

The deterministic candidate from the pinned sdist removes the 16 selected test
images/data files and verifies its expected SHA-256
`29941b25637e871e8c60a33b1bc65a67322b7d6951700b5574f0c85799be0f52`.
Preparation separately vendors pinned Cargo dependencies and checks retained
upstream files against that candidate, allowing only the expected dynamic-linking
patch. It then excludes the same verified fixtures, adds the candidate manifest,
and changes the private JPEG XL build identity from build 1 to
`research_reduced_*_2`. The candidate archive alone lacks the vendored Cargo
sources and is not a complete corresponding-source offer.

The generated recipe tests use deterministic, generated L, LA, RGB and RGBA
pixels, lossless and lossy decoding, EXIF and ICC metadata, JPEG reconstruction,
and malformed-input rejection. They do not replace the full upstream fixture
suite or establish independent codec interoperability. The test image pixels
are generated; the box parser in the synthetic script is adapted from James
Frost's MIT-licensed `jxl_decode` (revision
`902cd5d479f89f93df6105a22dc92f297ab77541`), with attribution in the script
and the license retained at `research/notices/pillow-jxl/fraetor-LICENCE.md`.

Hosted run [43052674361](https://github.com/Archont561/ODM-conda/actions/runs/43052674361)
built and retested the scoped package without uploading artifacts. Its private
package was `odm-research-pillow-jxl-plugin-1.3.4-research_reduced_873e7db_2.conda`,
SHA-256 `1a4bd2803b3f3cfebe6c273b410fa706de94505d24cb21fb9951bdbeaf96262b`;
fixture script SHA-256 `8a3317937b45a2450979d7fece547edfca6fb1831ca7e524c595ba9ce0ea436c`.
These are single-build observations, not reproducibility proof. The package
retains `LicenseRef-Unreviewed`.

For an isolated private trial on a suitably provisioned host, invoke
`pixi run python scripts/private_odm_bundle.py build --help` and use
`--runtime-profile reduced --reduced-jxl` with an external, empty destination
and optionally an external dataset. This selects a distinct ODM build 4 and
pins its JPEG XL dependency to the reduced build 2. It does not alter the
ordinary recipe or publish anything. A build with a dataset performs a relocated
lock replay, the synthetic codec test in that installed environment, and the
ODM raster/report checks. Those checks are scoped and are not a full product
validation.

Before publication: investigate the project license grant and third-party
notices, establish a complete and independently reviewed corresponding-source
path including crates and build modifications, examine fixture and dataset
rights, independently test interoperability and relevant ODM workloads, and
obtain owner approval for all affected gates. The narrowed test-data scope does
not resolve other components' outstanding rights or distribution restrictions.

Hosted integration run [43052862530](https://github.com/Archont561/ODM-conda/actions/runs/43052862530)
completed a private source build, 438-record relocated lock replay and Seneca
raster/report check; outputs were discarded, with no artifacts uploaded. The
observed JPEG XL build 2 package SHA-256 was
`f1bf4af7836311f54cd86b32f8085a39e321382d51cb2814732461a2e98b74b7` and ODM
build `hb0f4dca_4` SHA-256 was
`cada655f265113b31212bb303ea18f34aa4b0c57d7dbdad2a9e08366c2899478`.
This run predates the added explicit synthetic test in the replayed prefix; the
separate package test above is the observed codec evidence for that run.

Follow-up hosted run [43057210094](https://github.com/Archont561/ODM-conda/actions/runs/43057210094)
passed the same private build, relocated 438-record replay, explicit synthetic
codec test in the replayed prefix, and Seneca raster/report checks. No artifacts
were uploaded. Its JPEG XL build 2 SHA-256 was
`cdea0ce005054071d01d4e5ef5a5ac11d75ac4bda1489151379516412e171603`; ODM build
4 SHA-256 was `7b6ca1e101ad7fbab4dc9af0229e2bef10fc46156ba8aecc8c0e0750f16fc1dd`.
Different single-build hashes do not demonstrate bit-for-bit reproducibility.
