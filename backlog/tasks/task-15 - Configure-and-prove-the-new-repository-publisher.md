---
id: TASK-15
title: Configure and prove the new repository publisher
status: To Do
assignee: []
created_date: '2026-10-26 19:05'
updated_date: '2026-10-26 20:59'
labels:
  - release
  - maintainer
dependencies:
  - TASK-3
  - TASK-2
  - TASK-24
  - TASK-27
priority: high
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Repository owner action, not completed by the scaffold. Create or configure Archont561/ODM-conda, protect the prefix GitHub Environment, and add an OIDC Repository Access entry to the EXISTING archont561/archont561 Prefix channel for release.yml and environment prefix. Keep the existing CloudCompare publisher unchanged. Do not store a long-lived all-channel token.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The new repository/workflow/environment identity is authorized with narrow Read/write access.
- [ ] #2 The release source URL resolves before a binary is published; the binary checksum and attestation match the validated artifact.
- [ ] #3 A real release is intentionally approved only after technical/source/license reviews; no automatic release is tied to a work session.
<!-- AC:END -->
