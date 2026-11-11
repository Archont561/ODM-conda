# JPEG XL native inputs and notice review

## Result and limits

The bounded review identifies native source archives, embedded build recipes,
selected notices and ELF dependencies for seven **historical** conda-forge
packages from the [alternate ODM runtime inventory](odm-alternate-candidate-2026-11-07/conda-inventory.json).
It does **not** establish complete rights, a comprehensive notice package,
corresponding-source compliance, or permission to publish. The actual release
package, all its build/host and runtime inputs, dynamic loader resolution and
indirect dependencies must be determined and reviewed separately. The
[pinned plugin's grant](pillow-jxl-project-grant-review.md) remains unresolved.
No release gate is changed.

The metadata-only [package evidence](pillow-jxl-native-package-evidence.json)
SHA-256 `5e507d4f5e3ab3f4dd13db8a3709e6e9073dec2dd4a660c030755edde4d550c5`
was captured from [hosted run 43086211426](https://github.com/Archont561/ODM-conda/actions/runs/43086211426)
(job `130751164476`). Each binary archive was checked against its recorded
SHA-256 before inspecting `info/index.json`, `info/about.json`, recipe and
filename-matched notice data, and selected real shared-library ELF dynamic
sections. Recipe-file inventory hashes summarize sorted filename/hash maps;
the embedded recipes, not upstream identity or legal authorship, are what
the package declares. No packages or sources were uploaded. These binaries
are from the earlier alternate runtime, not proven to be the exact dependency
set of every subsequent JPEG XL or future release build.

## Native dependencies and source observations

| Historical input | Declared package license | Source / notice observations |
| --- | --- | --- |
| `libjxl 0.11.2 h174a0a3_1` | BSD-3-Clause | Embedded rendered recipe identifies libjxl v0.11.2, skcms commit `b2e692629c1fb19342517d7fb61f1cf83d075492`, libjpeg-turbo commit `8ecba3647edb6dd940463fedf38ca33a8e2a73d1`, four patches and `install.sh`. The package `info/licenses` includes libjxl and skcms LICENSE files. |
| `libhwy 1.4.0 h57c4cff_2` | Apache-2.0 OR BSD-3-Clause | Recipe identifies Highway 1.4.0 and two patches; root LICENSE is included in `info/licenses`. The source root license describes a choice of Apache 2.0 or BSD 3-Clause. |
| `libbrotlidec`, `libbrotlienc`, `libbrotlicommon` 1.2.1 | MIT | Their recipes identify the same Brotli 1.2.1 source; all three contain the same root LICENSE hash in `info/licenses`. |
| `libgcc` / `libstdcxx` 16.2.0 | GPL-3.0-only WITH GCC-exception-3.1 | The recorded recipe refers to GCC 16.2.0, patches and zlib 1.3.1. Filename scan found the runtime exception in each package payload; it did not find `info/licenses` entries. That scan is not proof no other notices occur elsewhere. GCC/zlib source archives were not fetched or verified here. |

The exact source URLs, archive hashes, versions, recipe hashes, dependencies,
selected patch hashes and notice hashes are in the evidence JSON. For libjxl,
skcms, libjpeg-turbo, Highway and Brotli, the corresponding GitHub codeload
archives were separately fetched and SHA-256 matched the embedded recipes;
root libjxl, skcms, Highway and Brotli license hashes also matched the selected
package notice hashes. The libjpeg-turbo source root `LICENSE.md` and
`README.ijg` were observed; an independent file-level use and notice review
is still needed. Hash equality is not proof of authorship or a complete
corresponding-source offer. The [libjxl CMake source](https://github.com/libjxl/libjxl/blob/v0.11.2/CMakeLists.txt)
conditionally enables jpegli when a libjpeg-turbo input exists, and its
[jxl CMS source](https://github.com/libjxl/libjxl/blob/v0.11.2/lib/jxl/cms/jxl_cms.cc)
refers to skcms; those source observations alone do not prove the exact code
linked into the distributed binary or establish all notices required.

For the inspected `libjxl.so.0.11.2`, `readelf -d` reported DT_NEEDED on
`libjxl_cms.so.0.11`, `libhwy.so.1`, Brotli decoder/encoder, libstdc++, libm,
libgcc_s, pthread and libc. The observed Brotli libraries depend on
`libbrotlicommon`, and `libjxl_threads` has its own listed dependencies. This
is static ELF metadata, not observed loader resolution, a complete process
closure, or proof of absence of static linkage and dynamically loaded code.

## Native build trial

[Run 43087788748](https://github.com/Archont561/ODM-conda/actions/runs/43087788748)
verified the historical libjxl binary SHA-256
`0c8a78c6a42a6e4c6de3a5e82d692f60400d43f4cc80591745f28b37daad9c70`,
then used its embedded rattler-build recipe and source settings for a private
rebuild and separately retested the result. The rebuilt package SHA-256 was
`7cff64383ea4ab14169d3d0d9b44d82b3450fddb088f421918e597cc2973e851`,
different from the historical package. Rattler-build 0.68.0 warned the original
was built with 0.63.0; the original build path had to be recreated on the
hosted runner. Conda/source downloads were allowed, so this is not an offline,
independent-source handoff, proof of equivalence or reproducibility, or a
release build. Artifacts and downloaded sources were discarded, not uploaded.

## Private Cargo notice draft

`scripts/jxl_crate_notice_draft.py` stages the 40 locked crates' previously
hash-inventoried root license/notice files and two additional hash-pinned
`pyo3-runtime` nested licenses into a new private directory, verifying each
selected file and its copied digest. It does not determine which notices are
required, review every file, verify all crate source files, or include the
project license, native notices, transitive dependencies or build tools. It
must not be treated as a release notice package. With a private prepared
vendor tree, run:

```sh
pixi run python scripts/jxl_crate_notice_draft.py --vendor /private/scoped/source/vendor --destination /private/crate-notice-draft
```

The destination must be new and outside the repository. In
[run 43086619000](https://github.com/Archont561/ODM-conda/actions/runs/43086619000),
two independent stagings of the scoped prepared vendor tree produced equal
75-file manifests, SHA-256
`dbf578cfc8e20d4534c151caaac0e2ace9eb39ffc1ebdfd5cb9fc79c4676c1a8`.
This is repeatability of the selected local draft, not an audit of notice
completeness or permission to redistribute. No draft was uploaded.

## Release decisions still required

- A qualified reviewer and owner must decide the pinned plugin's grant and
  provenance, the actual Rust and native material used, license choices and
  notice requirements; the earlier deferred maintainer clarification remains
  unobtained. Do not infer owner approval from this review.
- Assemble and independently examine the actual notices including retained
  project and Rust sources, embedded skcms/jpeg-turbo and applicable native,
  toolchain and other dependency terms. Check file-level origins and any
  nested or asset material; simple filename scans cannot settle these issues.
- Establish a complete, independently received source set for the exact
  release build, including matching native archives, patches, scripts, compiler
  inputs and required build/host records. Verify rebuild and linkage against
  the exact target package. A different native rebuild or URL/hash list alone
  is not an offer or a source-completeness decision.
