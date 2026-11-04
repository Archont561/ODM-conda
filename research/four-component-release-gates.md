# Release gate preparation: four native components

Snapshot: 2026-11-04. This is a decision aid for the exact linux-64 candidates
below, not a license opinion, owner approval, or permission to publish. The
four release checks in [`recipes/components.json`](../recipes/components.json)
remain **false for every candidate**. Native success is evidence for review,
not a gate decision. None of these packages is a full ODM distribution.

## Current candidate and technical evidence

[Temporary run 41840541554](https://github.com/Archont561/ODM-conda/actions/runs/41840541554)
on clean commit `a94c8041e081eccad6e5141cc30c4d656b238259` independently built
each production recipe, ran packaged and fresh-environment tests, audited its
package, made a local source bundle and rehashed every file listed in that
bundle's source manifest. Each job ran separately with no artifact upload;
all packages, archives and test inputs were discarded. The temporary harness
is included in that run's packaging-source bundle but is removed from the
proposed final tree, so its bundle hashes are historical evidence, not hashes
for a future release commit. The tests do not prove legal compliance, full
source completeness, bit reproducibility, or every supported workload.

| Component and candidate | Native run job | Package SHA256 | Source bundle SHA256 | Listed source files checked |
| --- | --- | --- | --- | ---: |
| `dem2mesh` `0.0.0.dev20231207` build 1 | [126610645618](https://github.com/Archont561/ODM-conda/actions/runs/41840541554/job/126610645618) | `0d1b6e9f17e31eb4db51d0ff6019c7e2a7eee369e9b486e313cf8f5a5d2a795e` | `bbe2d4cac7a5e232c96339167d23004eb9dc24a2fb616b091c5e0022d633f4bf` | 353 |
| `renderdem` `1.0` build 1 | [126610645213](https://github.com/Archont561/ODM-conda/actions/runs/41840541554/job/126610645213) | `01096cf87bf517b317eef91dac693afe841d02e49345dd6bb6810f5299d8bf59` | `c59a7d33f96355d0a7d2fb6b92311aec86324b76753e3bdad5fc1d47d4cc6fc6` | 353 |
| `poissonrecon-odm` `13.8` build 3 | [126610646004](https://github.com/Archont561/ODM-conda/actions/runs/41840541554/job/126610646004) | `ec16be3b45c87079a63d928b14d7567a3c2f197d04df738a19ba48f755e4d58f` | `baab7a2568dc3d6c2bcd697c29b1db12f815de1f28e7f00e2dab0735e8db7866` | 353 |
| `mvs-texturing-odm` `0.0.0.dev20250818` build 2 | [126610645778](https://github.com/Archont561/ODM-conda/actions/runs/41840541554/job/126610645778) | `cc57707d03572a15e1b4c67b7f7766ac70fc9b74d0e38c0dee113970a7d82f90` | `01fdabc565eb0ab0330566726fd2e9851d5ecfcd5e476c76ae5a65b69caab66f` | 357 |

The source manifest's listed files were rehashed within the same job, not
independently after retention; its own manifest and source README are not in
that file list. A correct digest does not prove that the listed set is complete
or lawfully redistributable. Builds use live conda-forge solves; reruns and the
actual release build can differ. Run the owner-dispatched build workflow and
inspect the exact proposed release commit and artifacts again before approval.

If these exact candidate versions and build numbers remain unchanged, their
registered release tags would be `dem2mesh-v0.0.0.dev20231207-b1`,
`renderdem-v1.0-b1`, `poissonrecon-odm-v13.8-b3`, and
`mvs-texturing-odm-v0.0.0.dev20250818-b2`. These are prospective identifiers,
not existing release authorization. Any changed candidate requires its own
review and matching tag.

## Gate-by-gate decision inputs

The configured fields are `license_reviewed`, `source_completeness_reviewed`,
`native_validation_passed` and `publishable`. Each exact candidate needs an
explicit owner decision; the checkboxes below record **remaining work**, not
permission to flip flags. A qualified reviewer should assess licensing and
rights. Do not count approval of another component, build, or private research
variant as approval of any candidate here.

### dem2mesh build 1

- **License:** candidate metadata is `GPL-3.0-or-later AND GPL-2.0-or-later
  AND BSD-3-Clause AND MIT`. Review compiled JMeshLib, third-party code and the
  historical origin and applicable MIT grant of the vendored simplification
  source; the later added MIT notice is conservative evidence, not proof of
  the earlier grant. See [TASK-32](../backlog/tasks/task-32%20-%20Review-dem2mesh-package-readiness-evidence.md)
  and [decision record](../backlog/docs/reviews/doc-12%20-%20Remaining-package-licensing-decision-record.md).
- **Source completeness:** review the pinned upstream archive, patch, packaging
  scripts, build instructions and actual dependency/source obligations; a
  matching source manifest does not establish completeness.
- **Native validation:** the run above and earlier exact build-1
  [run 40862757220](https://github.com/Archont561/ODM-conda/actions/runs/40862757220)
  and its independent inspection provide bounded Linux fixture and artifact
  evidence. Revalidate the final release candidate, actual GDAL ABI and
  intended workloads; no universal relocation or coverage claim is made.
- **Publishable:** pending the above, review of the exact release set, the
  owner's four-gate decision and separate publication authorization.

### renderdem build 1

- **License:** provisional `AGPL-3.0-only AND MIT`. The pinned 11-file direct
  source tree and cxxopts notice were inventoried, but the precise grant/version,
  unmarked-code provenance, AGPL network-service obligations, dependency and
  compiler-runtime terms need qualified and owner review. See
  [RenderDEM review](component-readiness-review.md#renderdem-direct-source-license-inventory-2026-10-29).
- **Source completeness:** verify the complete release source and scripts,
  exact resolved PDAL/GDAL and transitive obligations, and actual source-offer
  and notice delivery. Earlier exact-artifact review concerned build 0; the
  later build-1 inspection below does not resolve source completeness.
- **Native validation:** current production build 1 passed the run above;
  its fixture exercises synthetic PLY and uncompressed LAS. LAZ, broader input
  coverage and full integration with the final released stack remain unproven.
- **Publishable:** pending all decisions above and a release-candidate-specific
  owner authorization; the prior fastrasterfilter AGPL decision does not apply.

#### Owner-dispatched RenderDEM artifact inspection (2026-11-04)

The owner-dispatched [build run 41843213137](https://github.com/Archont561/ODM-conda/actions/runs/41843213137)
at `8c0619224de35ceef02a4f5863b182a9a4574947` passed build, packaged and
fresh-environment tests, audit and source bundling. Read-only
[inspection run 41844146569](https://github.com/Archont561/ODM-conda/actions/runs/41844146569)
verified the reported artifact ZIP SHA256
`cd2671e9f6184102887b08b01f843309210c2fddad7825439bb05e8f7bdd2385`
and confirmed exactly one package, one audit report and one source bundle,
all for RenderDEM build 1. The package
`renderdem-1.0-h873e7db_1.conda` SHA256 is
`a681202611aa3fa25281055825b75a89e1a256260a954ce69bcd5393a834d94c`;
`source-renderdem-1.0-b1.tar.gz` SHA256 is
`bf806435fc489b73c059e409b85c159e2b01f3bac7537f996e39d842bd6f8ec1`.
All 353 entries listed in its source manifest matched, with the expected clean
packaging commit. The inspector reran the current package audit and a fresh
isolated package test; no artifact was re-uploaded. The original non-published
artifact is retention-limited and expires 2026-11-18.

Package metadata requires `libpdal-core >=2.10.0,<2.10.1` and
`libgdal-core >=3.12.2,<3.12.3` among other runtime dependencies; these are
constraints, not a locked or fully reviewed resolved closure. The source
manifest does not list itself or the source README; matching listed hashes does
not establish corresponding-source completeness, notices or redistribution
rights. The tests do not establish LAZ support or geographic accuracy. All
four release gates remain false and publication requires separate owner
approval. The release workflow will rebuild, so these artifact hashes do not
prove the bytes of a future release build.

### poissonrecon-odm build 3

- **License:** preliminary `MIT AND BSD-3-Clause AND Libpng AND Zlib` does not
  settle the provenance and obligations of JPEG source present in the original
  archive. An unaltered IJG README is added by a patch and audited; whether the
  underlying archive, modifications and accompanying binary acknowledgement
  meet applicable terms remains for qualified review. See
  [TASK-56](../backlog/tasks/task-56%20-%20Resolve-missing-IJG-terms-in-PoissonRecon-source-distribution.md)
  and [Poisson review](poissonrecon-readiness-review.md).
- **Source completeness:** evaluate the original archive plus patches,
  documented differences, exact build instructions and dependencies, including
  a lawful source offer. The JPEG-reduced candidate is research-only and is
  not the production bundle or legal clearance.
- **Native validation:** production build 3 passed the run above, including
  packaged and fresh tests and package audit; the named-input link checks do
  not prove absence of equivalent static code or settle all security risks.
  Review the final binary, actual library solve and intended workloads.
- **Publishable:** pending the unresolved source, notice and security decisions,
  exact-candidate owner gate approval and separate release authorization.

### mvs-texturing-odm build 2

- **License:** the provisional expression includes `LicenseRef-COLAMD` and
  `LicenseRef-SuperLU`; confirm their scope, Eigen/MPL terms, MVE notices,
  third-party code and dependency obligations. MVE's SIFT/SURF disclaimer
  requires appropriate source and patent review; a named link-map check is not
  a legal determination. See [texturing review](mvs-texturing-license-review.md).
- **Source completeness:** review all five source archives, patches, build
  inputs, notices, disabled download paths and source-offer terms. The MVE
  source archive still includes the warned-about files, even if the final link
  avoids named objects. Do not distribute it solely on the strength of this
  technical run.
- **Native validation:** the production build, fresh retest, audit and source
  manifest check passed above. The link-map guard addresses named inputs, not
  all equivalent code; verify the final candidate and representative usage.
- **Publishable:** pending those decisions and explicit owner authorization
  of the exact release candidate and publication.

## Once blockers are resolved

1. Retain a reviewed candidate's exact source inputs, build recipe, binary,
   audit, dependency inventory and corresponding-source set in appropriate
   owner-controlled storage. Rerun the owner-dispatched
   [build workflow](https://github.com/Archont561/ODM-conda/actions/workflows/build.yml)
   for the final candidate and inspect its outputs; workflow artifacts expire.
2. Record the owner's decision on **each of the four checks for that exact
   component/version/build**, via reviewed changes to `recipes/components.json`.
   These decisions are not a legal certification and must not be inferred from
   the technical steps alone.
3. Obtain separate authorization to merge the approval and publish. Follow the
   [publishing guide](../backlog/docs/guides/doc-7%20-%20Publish-to-the-existing-Prefix-channel.md):
   one exact registered component tag at trusted default-branch HEAD and a
   published non-prerelease GitHub Release trigger the protected Prefix job.
   It builds anew, audits, attaches source before binary upload, and uses the
   protected `prefix` environment. No publication is performed here.
