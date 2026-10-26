<!--
title: '📄 ADR-0003: RELEASE THE IMAGE FROM CUT RELEASE'
description: 'The decision to publish the image in the same 🏷️ Cut Release run that tags the version, after testing each architecture on a runner of its own, with SBOMs made by jobs that can only read, and with every version kept.'
type: record
status: 'Accepted'
date: '2026-10-26'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0003: RELEASE THE IMAGE FROM CUT RELEASE

<a name="top"></a>

**The tag and the image it names are published in one run, and only once both architectures pass.**

_Tested where it runs. Published where it is tagged._

</div>

---

## 📋 Meta Information

| Attribute     | Specification                                                                    |
| :------------ | :------------------------------------------------------------------------------- |
| **Deciders**  | The maintainers listed in [GOVERNANCE.md](../../.github/GOVERNANCE.md)           |
| **Consulted** | Everyone who reviews the pull request that implements it                         |
| **Informed**  | Every repository whose development container names the image, through its README |

---

## 🎯 Context & Problem Statement

Repositories consume the environment by tag: a development container names
`ghcr.io/tannergolden/environment:1`, and a cloud setup script downloads its
files from a git tag. So a release has to put the image behind its tag, for
`linux/amd64` (Codespaces and Actions) and `linux/arm64` (Apple silicon), with
a provenance attestation and an SBOM. The standards' release workflow, which
tags a version, creates the release with the run's own token, and GitHub
starts no other workflow from what that token does: a stub waiting for the
release event would never run. The template's 📦 Release workflow assumes a
repository that releases by publishing a draft, which this one does not.

---

## 🚦 Decision Drivers

- **Driver 1**: The image must exist for every tag, published from the commit
  the tag names, with no long-lived secret.
- **Driver 2**: Each architecture must be built and tested on its own hardware
  before anything is tagged, since an Apple silicon Mac pulls the arm64 image.
- **Driver 3**: Jobs that run third-party tools hold the least permission they
  can, and every version stays resolvable, because a pinned cloud setup
  script downloads from its own tag.

---

## 🏗️ Considered Options

1. **Option A**: Tag with the standards' release workflow, and publish the
   image from a stub triggered by the release event.
2. **Option B**: The same, with a personal access token in place of the run's
   own, so the release event starts the stub.
3. **Option C**: One 🏷️ Cut Release run: test on an amd64 runner and an arm64
   one, tag through the standards' release workflow, then publish the image
   through the standards' publisher in the same run, and attach SBOMs made by
   read-only jobs.
4. **Option D**: Build both architectures on one amd64 runner under emulation.

---

## ✅ Decision Outcome

**Chosen Option**: Option C, publishing from 🏷️ Cut Release.

### Rationale for Selection

The image job runs after the tag, on the same commit, in the same run, so the
image exists for every tag and no token has to be kept (Driver 1). Two verify
jobs build and test the image natively, and nothing is tagged unless both
pass; the publisher then builds each architecture again on its own runner
(Driver 2). The SBOMs are made per architecture, on that architecture's
runner, by jobs that can only read, and a last job attaches them; the standards'
prune is turned off with `keep-versions` (Driver 3). The run plans the image's
tags from the version typed in: `X.Y.Z`, and, when it moves the major, `X` and
`latest`. A dry run, on by default, does everything but publish. The template's
📦 Release workflow is deleted, since its weekly draft, its publish and its
prune all assume the other model.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                                                                                          |
| :--------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Positive (+)** | A tag never names an untested image; no secret to rotate; least privilege for the SBOM generator; every version keeps resolving                               |
| **Negative (-)** | A job that fails after the tag is re-run, which rebuilds and re-points that version's tags; a failure inside the tagging job itself spends the version number |
| **Neutral (~)**  | The standards' release workflow still does the tagging and its guards; the image published is a fresh build of the tested commit, not the tested image        |

---

## ⚖️ Trade-off Comparative

### Option A: A release-event stub

- ✅ The usual shape for a release pipeline.
- ❌ Never runs: a release made with the run's own token starts no workflow.

### Option B: A personal access token

- ✅ Lets the release event start the stub.
- ❌ A long-lived secret with write access, to rotate and to leak.

### Option C: Publish from Cut Release

- ✅ One run, no secret, each architecture tested natively before the tag.
- ❌ A partial failure leaves a tag waiting for its image until the failed
  jobs are re-run.

### Option D: Emulated multi-architecture build

- ✅ One runner.
- ❌ Slow, and it never runs the arm64 image on arm64.

---

## 🔗 Traceability & Links

- [`.github/workflows/cut-release.yml`](../../.github/workflows/cut-release.yml):
  the release, and why each job is shaped as it is
- [README: Releasing](../../README.md#-releasing): how to cut one, and how to
  recover a failed one
- [Release Verification](../distribution/Release-Verification.md): how a user
  checks what a release published

### 🔗 See also

> [!TIP]
> Every canonical guide is indexed in the [&#x1F4DA; Standards Index](https://github.com/tannergolden/standards/blob/Development/docs/README.md). If you rename or move a file, update every reference to it across the repository to prevent link drift.

---

<div align="center">

**One decision. One record. Zero ambiguity.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the terms in [LICENSE](/LICENSE).

</div>
