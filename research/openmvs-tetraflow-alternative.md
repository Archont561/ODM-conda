# OpenMVS TetraFlow alternative: private feasibility trial

This is **not** a production recipe, a legal conclusion, or an authorization to
publish. The historical ODM fork archive still contains restricted IBFS/TRWS
sources. No existing source, binary, release or audit gate is relaxed here.

## Candidate and scope

[OpenMVS commit 0aebb63a7dc72f2831615b441fdf2f474d7a0ea0](https://github.com/OpenDroneMap/openMVS/commit/0aebb63a7dc72f2831615b441fdf2f474d7a0ea0)
removes IBFS and replaces it with `libs/Math/TetraFlow.h`. At this commit the
Git tree has no files under `libs/Math/IBFS` or `libs/Math/TRWS`. The header
states Boost Software License 1.0 and says the implementation is independent
and no existing max-flow source was consulted. These are upstream assertions,
not independent provenance verification or a clearance of the whole tree.
Codeload archive SHA-256: `4701b4490c8036bc548f23b949d871bd2c133386051aad051d1f3de912b26014`.

This commit is on the fork's develop line, not the pinned ODM master revision.
The two histories diverge substantially: 471 files changed in the tree diff,
including ODM-specific changes and upstream changes. It is not a drop-in
replacement merely because the graph solver changed. In particular, this
upstream `ReconstructMesh` lacks the previously developed explicit visibility
validation; its point-cloud reader differs from the hardened ODM research
patch. Do not use it with untrusted or malformed PLY inputs. The existing
negative and separate-cloud fixture suite has **not** been run against it.

## Experiment

The isolated linux-64 `research/recipes/openmvs-tetraflow-research/recipe.yaml`
builds only `ReconstructMesh`, excluding three dense/refine/texture translation
units and unrelated SFM apps. The build checks exact hashes of the changed
source inputs, rejects the named restricted directories, and applies the
existing named link-map check to a static-library link. Neither this check nor
absence of those directory names establishes complete provenance, rights,
source coverage or absence of restricted material elsewhere.

A temporary GitHub runner build and separate package retest
[43092563761](https://github.com/Archont561/ODM-conda/actions/runs/43092563761)
passed, including reconstruction of the repository's generated two-camera
scene. Package SHA-256 was
`2b4de6a38722d9a2e1ccb7ecf0217beb164243722dfdae9ff7702e0a62b60f85`.
The research sources and binary were discarded with the job; only the hash
was retained. This does not test ODM integration, all command-line options,
mesh quality, separate PLY loading, real-world scenes, or full OpenMVS.
Conda dependencies were solved online, not against a retained final lock.

To repeat privately on a trusted host, use `rattler-build build --recipe
research/recipes/openmvs-tetraflow-research/recipe.yaml --target-platform
linux-64 --variant-config recipes/variants.yaml --channel conda-forge
--channel-priority strict --output-dir <private-directory>` and independently
retest the resulting package. The build script expects the repository checkout;
never upload its output or source without approval.

## Remaining work before a production candidate

1. Independently review the exact source archive, TetraFlow authorship and all
   included third-party sources/notices; owner decides rights and policy.
2. Port or redesign the existing strict PLY/visibility checks for this changed
   implementation. Run the entire generated positive and negative fixture
   suite, and verify ODM-required command-line options, formats and behavior.
3. Test with scoped OpenSfM and ODM end-to-end on suitably cleared data, and
   assess functionality/quality relative to the historical fork. Review all
   other ODM-specific changes lost across the diverged histories.
4. Finish OpenSfM asset and JPEG XL project/native/source reviews; assemble
   complete source/notice obligations for the actual selected closure.
5. Build and retain the final exact packages, source materials, inventory and
   replay lock in owner-controlled storage; replay and audit them. Owner must
   approve gates and dispatch the release workflow before publication.
