# RenderDEM source-offer preparation

Scope: standalone RenderDEM 1.0 build 1, linux-64. This is a technical
preparation and checklist, **not** a complete corresponding-source legal
attestation or authorization to publish.

## What is prepared

The component recipe pins the upstream archive and build dependencies, and the
release workflow builds and audits the selected component, creates a matching
source bundle and attaches that bundle, its checksums and the audit to the
GitHub Release before uploading the binary to Prefix. The installed `SOURCE.txt`
points to the release-specific bundle URL. Intermediate workflow artifacts
expire after 14 days; they are not the public source offer. The GitHub Release
asset must remain available for the applicable period and recipients.

The source bundle includes the pinned upstream archive, vendored cxxopts, the
project's packaging scripts, recipe, tests, notices and Pixi tooling lock. Its
manifest hashes the listed inputs. Run 41862738817 reconstructed a working
package from the earlier build-1 bundle with the recipe changed to use local
source and dependencies obtained online. The reconstructed and original binary
hashes differ; the cause has not been established. See the
[gate review](renderdem-release-gate-review.md) for identities and limits.

New RenderDEM bundles include explicit commands and
`scripts/prepare_renderdem_source_rebuild.py`. The helper checks an independently
supplied bundle SHA256, rejects unsafe or unlisted entries, verifies each
manifest-listed file, stages the packaging and original source in a new directory,
and replaces only a matching source URL/checksum stanza with a local source
path in the staged recipe. The bundle's README describes the build command.
This is a reconstruction aid: it does not verify the authenticity of the
independently supplied checksum, obtain or freeze the exact Conda dependency
closure, prove offline/bit-identical reproduction, or decide legal completeness.

## Release-specific checks still required

1. On the approved release commit, run the owner-dispatched native build and
   verify its exact binary, source bundle, checksums, installed notices and
   `SOURCE.txt`. A future protected release rebuild is a different artifact;
   verify its generated release set rather than assuming earlier hashes apply.
2. Obtain and review the actual release build/host/runtime dependency closure,
   linking and applicable source and notice obligations, including PDAL, GDAL
   and compiler runtimes. Those packages are not included in this bundle and
   a prior research solve does not identify the final release closure.
3. A qualified reviewer and owner must decide whether the source set,
   instructions, offer, retention and any applicable service obligations meet
   the terms for the actual distribution. Owner confirmation of the proposed
   grant is not a source-completeness decision.
4. After explicit approval of each release gate and separate authorization to
   publish, verify the final source asset and checksum are accessible at the
   URL before channel publication and preserve access as required. The release
   workflow enforces source attachment before the upload, but long-term
   availability is an operational responsibility, not guaranteed by the code.

No source asset is made publicly available by this preparation, and all four
RenderDEM release gates remain false.
