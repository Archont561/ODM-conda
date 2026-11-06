# RenderDEM 1.0 build 1: proposed license and source decisions

This is a **recommendation**, not legal advice, a rights-holder representation,
owner approval or publication authorization. It concerns the standalone
linux-64 `renderdem` 1.0 build 1 candidate, not the whole ODM distribution.
The configured release checks remain false. The detailed technical evidence and
limitations are in [the RenderDEM gate review](renderdem-release-gate-review.md).

## Recommended package-level license decision

**Retain `AGPL-3.0-only AND MIT` as the conservative proposed package
expression**, subject to owner and qualified review of the exact candidate.

- The pinned RenderDEM source contains the AGPL version 3 license text and its
  README says `AGPLv3`; the reviewed project files do not provide an observed
  explicit later-version grant. This supports retaining the existing
  conservative `AGPL-3.0-only` choice; it is not proof that the project or
  every contributor granted precisely those terms.
- The included `cxxopts.hpp` carries an MIT permission and copyright notice.
  Compared with upstream v3.1.1 it includes one `noexcept` change. Retain its
  included notice, the complete modified source, and the modification evidence;
  the comparison does not independently establish authorship or rights for the
  change. Original packaging/test code carries its own MIT notice.
- The actual build-1 package's AGPL, cxxopts MIT and packaging MIT notice
  bytes were checked against their source in both the package payload and Conda
  metadata. On the reviewed evidence no additional direct-source notice is
  identified, but this is **not a complete notice or provenance certification**.
- Separately installed PDAL, GDAL, compiler runtimes and transitive packages
  retain their own licenses. Their metadata from a test solve must not be
  mistaken for a reviewed distribution closure or silently added as if every
  dependency were bundled into RenderDEM. Assess the actual linking,
  distribution arrangement and applicable terms for the final release.

This recommendation leaves the SPDX expression unchanged and does **not** set
`license_reviewed`. In particular, owner/qualified review must decide the exact
grant/version, rights for unmarked project code and the modified vendored
header, and whether the notices cover the intended distribution.

## Recommended corresponding-source approach

Use the existing protected release workflow as the delivery mechanism: rebuild
one approved exact component candidate, audit it, stage its matching source
bundle, attach the source and checksums to the GitHub Release **before** the
binary is uploaded to Prefix, and preserve the release-specific source URL
installed in `SOURCE.txt`. The owner must maintain source availability for the
period and recipients required by the applicable terms; the workflow's
14-day intermediate artifact retention is not a durable source offer.

The reviewed bundle contained the pinned original upstream archive and the
packaging files; all 353 manifest entries were verified and a local-path
reconstruction passed build, test and audit. The recipe source declaration was
changed for that test, conda-forge dependencies were obtained online, and the
reconstructed binary hash differed. Therefore this is encouraging technical
evidence, **not** proof that every required corresponding-source input or
instruction for a future distributed binary is present, or that the build is
fully offline or bit reproducible.

Before deciding `source_completeness_reviewed`, inspect the actual final release
source set, its build and installation instructions, modifications, and the
applicable source/notice obligations of the selected dependency and toolchain
inputs. Verify the final source asset and URL are accessible, and establish a
retention and availability plan. For a network service using a **modified**
AGPL-covered program, assess section 13 and the actual deployment with a
qualified reviewer; do not assume that merely using any unmodified executable
in a service automatically triggers a particular source-delivery duty.

## Explicit decision boundary

| Item | Recommendation | Still required |
| --- | --- | --- |
| Package expression | Keep `AGPL-3.0-only AND MIT` provisionally. | Owner/qualified review of grants, provenance and actual distribution. |
| Direct notices | Retain the three already verified notices and modified cxxopts source. | Confirm coverage and any additional applicable obligations. |
| Source delivery | Attach the reviewed corresponding source before Prefix upload and retain it at the release-specific URL. | Confirm the exact source set, instructions, availability, dependency and service obligations. |
| Native scope | Use the successful build, retests and bounded PLY/LAS/LAZ and fresh-prefix evidence as inputs. | Decide whether coverage is sufficient and verify the final release build; a fresh install is not a moved-prefix test. |
| Release | Do not publish or change any of the four gates yet. | Explicit owner decisions for this exact version/build and separate merge and publication authorization. |

The owner can accept or reject these recommendations after reviewing the linked
evidence. Acceptance of this document alone does not flip gates or authorize a
release. Do not infer a grant or legal clearance from a SHA256, a successful
build, or a prior approval of another AGPL component.
