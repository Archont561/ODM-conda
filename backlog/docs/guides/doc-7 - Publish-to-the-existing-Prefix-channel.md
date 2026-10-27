---
id: doc-7
title: Publish to the existing Prefix channel
type: other
created_date: '2026-10-26 19:39'
updated_date: '2026-10-27 16:34'
---
# Publish to the existing Prefix channel

## Locations

- Packaging repository: `Archont561/ODM-conda` (created; first publication
  2026-10-27, `fpcfilter 0.2` build 1 — see TASK-15).
- Canonical Prefix channel: **`archont561/archont561`**.
- Package repository URL: `https://prefix.dev/archont561/archont561`.
- GitHub publishing workflow: **`release.yml`**.
- Protected GitHub Environment: **`prefix`**.

CloudCompare and ODM can share this channel. Do not create a channel per component
and do not move/reconfigure the existing CloudCompare publisher.

## Initial repository setup

Create an empty public repository in the intended account, then from this folder:

```bash
git init -b main
git add .
git commit -m "chore: scaffold modular ODM Conda packaging"
git remote add origin https://github.com/Archont561/ODM-conda.git
git push -u origin main
```

If you choose a different repository name, update `recipes/components.json` and any
repository URLs before building. Installed `SOURCE.txt` links are generated from
that manifest, so wrong repository metadata can break source access.

Protect the default branch and publishing workflow. Configure required reviews
for the `prefix` environment if your GitHub plan supports them.

## Prefix Repository Access (OIDC)

In the existing channel's settings, add a **new** authorized source:

```text
Provider:      GitHub
Owner:         Archont561
Repository:    ODM-conda
Workflow file: release.yml
Environment:   prefix
Access:        Read/write
```

Names, especially the environment, must match the identity emitted by the job.
Do not use an all-channel API key, a personal access token, or Read/write/delete
when normal publication only needs Read/write. Keep the CloudCompare mapping.

Current Prefix documentation calls this Repository Access; older pages call it
Trusted Publishing. See https://prefix.dev/docs/prefix/channels/access.

### OIDC failure signatures (learned 2026-10-27, first publication)

Two distinct rattler-build failures point at different halves of the entry:

- `attestation requested but trusted publishing is not configured` — the token
  mint (`POST /api/oidc/mint_token`) failed: the job identity (owner,
  repository, workflow file, environment) matches no authorized source, or the
  runner cannot request an ID token.
- `authentication failed (HTTP 403)` at the package-upload step — the mint
  succeeded, so the identity matched, but the minted token was denied write
  access to the target channel. Check the entry's Access mode (`Read` blocks
  uploads; publication needs Read/write) and that the entry is attached to the
  channel being uploaded to.

The first three attempts failed with the upload-stage 403 until the owner
corrected the entry; run 40515263476 then published
`fpcfilter-0.2-h873e7db_1.conda` with an attestation. If a failed release's
Release/tag were deleted, retry by re-pushing the same annotated tag on the
same default-branch HEAD and recreating the Release with identical notes —
the guard's tag == HEAD check leaves no other latitude, and a UI re-run of an
old run cannot work once the tag is gone.

A successful upload may not appear in the public repodata immediately: during
the dem2points publication (2026-10-27) the prefix.dev edge cache kept serving
a copy generated seconds after the upload for several minutes. Re-fetch the
repodata with a cache-busting query parameter before diagnosing a "missing"
package.

## First validation, without publication

Run the manual **Build and test native components** workflow. It builds the selected
implemented recipes, repeats packaged tests in fresh environments, audits their
contents/native paths and produces corresponding-source bundles.

CI artifacts expire after 14 days. They are for validation, **not** a substitute
for a persistent source-distribution location or a public package channel.

## Release gates

Each component has four booleans in `recipes/components.json`, initially false:

| Gate | What the maintainer acknowledges |
|---|---|
| `native_validation_passed` | Appropriate native/integration tests ran on the supported target; limitations reviewed |
| `license_reviewed` | Upstream, bundled code and assets have been reviewed |
| `source_completeness_reviewed` | The release source set and its durable availability satisfy the actual distribution's obligations |
| `publishable` | This specific component/version/build is intentionally approved for public distribution |

The script refuses a release if any value is not the boolean `true`. It cannot
replace legal review or prove dataset quality. Review FPCFilter's known upstream
non-normals sampling issue before acknowledging readiness.

Reset the relevant gates after source, patch, ABI, source-staging or license changes.
The repository does not try to infer legal approval from a successful compiler exit.

## Tags and release flow

A tag must exactly match:

```text
<component>-v<package-version>-b<build-number>
```

Examples for the initial pins, **only after review**:

```text
fpcfilter-v0.2-b0
dem2points-v0.0.0.dev20220721-b0
```

Commit reviewed gates, run checks, and tag the **current default-branch HEAD**.
Publish a non-prerelease GitHub Release for that tag. The guard requires clean
checkout + exact HEAD/tag equality; it deliberately fails if the default branch
has advanced to a different commit before the release job checks out the code.

The build job:

1. Checks out the trusted default branch with all tags, without stored Git credentials.
2. Checks repository identity, release gates and tag/HEAD equality.
3. Builds and tests the selected component.
4. Reinstalls it into a fresh test environment and audits the artifact.
5. Stages the binary, complete starter source set, audit report and SHA256SUMS.

The separate `publish` job (the only job with `id-token: write`):

1. Downloads that exact artifact set without checking out the repository.
2. Verifies checksums and expected counts.
3. Uploads the source bundle, audit and checksums to the persistent GitHub Release.
4. Uses rattler-build OIDC and attestation to upload the `.conda` to
   `archont561/archont561`.
5. Attaches the successfully published binary to the same release.

Source precedes channel publication so the installed `SOURCE.txt` URL can resolve
when a user obtains the public binary. GitHub's autogenerated source zip alone is
not used as the claimed corresponding-source bundle.

## Immutability and failure handling

The workflow intentionally uses neither `--clobber` nor `--skip-existing`.
Do not silently replace a public artifact or hide a filename collision. Review a
partial release before retrying. Prefer a new build number/tag for a corrected
release. Source-only assets left by a failed binary upload are harmless, but must
not be mistaken for a successful binary publication.

Retain source access for as long as required. Yanking/deleting packages is not a
substitute for source obligations to existing recipients. Do not rely on expiring
Actions artifacts, caches, or upstream branches remaining unchanged.

Check your Prefix account's current storage/package-size allowance; multiple
channels do not eliminate storage planning. Consider its Open Source plan if the
multi-component/platform history outgrows the current allowance.
