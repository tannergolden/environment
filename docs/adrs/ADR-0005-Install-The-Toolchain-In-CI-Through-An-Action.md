<!--
title: '📄 ADR-0005: INSTALL THE TOOLCHAIN IN CI THROUGH AN ACTION'
description: 'The decision to have the standards install every check tool through this repository''s toolchain action, which runs the image''s own installer, so this repository owns the versions and every repository''s checks run the image''s tools.'
type: record
status: 'Accepted'
date: '2026-10-26'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0005: INSTALL THE TOOLCHAIN IN CI THROUGH AN ACTION

<a name="top"></a>

**Every repository's checks run the image's tools, through the stubs they already have.**

_One copy of each version. One installer everywhere._

</div>

---

## 📋 Meta Information

| Attribute     | Specification                                                          |
| :------------ | :--------------------------------------------------------------------- |
| **Deciders**  | The maintainers listed in [GOVERNANCE.md](../../.github/GOVERNANCE.md) |
| **Consulted** | Everyone who reviews the change in the standards that adopts it        |
| **Informed**  | Every repository whose checks call the standards                       |

---

## 🎯 Context & Problem Statement

The standards' checks installed their tools themselves, each its own way:
typos and lychee through their own actions, gitleaks through its action and a
tarball, actionlint built with `go install`, zizmor from pip, and the
standards' own pytest, ruff and Prettier in their self-checks. shellcheck was
whichever the runner carried. This repository copied those versions into
`toolchain/`, so every version had two copies to move together, and the one CI
ran was the one no test held to the image. Every repository reaches the
standards' checks through its workflow stubs, so what those checks install is
what every repository's CI runs.

---

## 🚦 Decision Drivers

- **Driver 1**: Every repository's checks run the image's tools, with nothing
  to change in any repository that calls the standards.
- **Driver 2**: One copy of each version, held by the tests that check the
  image.
- **Driver 3**: Nothing new in the path of every repository's CI that can fail
  on its own, and nothing that changes a repository's own tests.

---

## 🏗️ Considered Options

1. **Option A**: Run the standards' check jobs inside the image, with
   `container: ghcr.io/tannergolden/environment:1`.
2. **Option B**: Have the standards' check jobs run this repository's installer
   through a composite action,
   `tannergolden/environment/.github/actions/toolchain@v1`.
3. **Option C**: Leave the standards' own pins, and keep the two copies in step
   by hand.

---

## ✅ Decision Outcome

**Chosen Option**: Option B, the toolchain action.

### Rationale for Selection

The action runs the installer the image runs, from the same release
([ADR-0002](ADR-0002-One-Installer-For-The-Image-And-Cloud-Sessions.md)), so
CI gets the image's versions (Driver 1). One `uses:` line in each of the
standards' check jobs replaces that tool's own install, and the standards keep
no version of their own, so this repository owns them (Driver 2). It downloads
from the upstream sources the standards already downloaded from, checks each
file against its pin, needs neither GHCR nor the image, and took about 12
seconds when tried here (Driver 3). It runs only in the jobs that run the
standards' checks: its Python packages go into the user site, ahead of
site-packages, so in front of a repository's own tests they would shadow its
pytest or PyYAML (Driver 3).

The standards call it at the moving major, as they call their own actions and
the intelligence hub's: moving `v1` is how a release here reaches every
repository's checks.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                                                                                     |
| :--------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Positive (+)** | One copy of each version; shellcheck is pinned in CI for the first time; the standards drop their separate ways of installing each tool                  |
| **Negative (-)** | Moving `v1` here changes the tools every repository's checks run, the next time each runs; Dependabot no longer moves tool versions through action bumps |
| **Neutral (~)**  | The runner's own system packages, such as git, still differ from the image's                                                                             |

---

## ⚖️ Trade-off Comparative

### Option A: Inside the image

- ✅ Exactly one machine, everywhere.
- ❌ Every job pulls an 848 MB image from GHCR, the image has no `gh`, which
  several of the standards' jobs use, and a job that builds an image cannot run
  inside one.

### Option B: The toolchain action

- ✅ The image's versions, from the image's installer, in seconds.
- ❌ A release here reaches every repository's checks at once, so it is
  released like the image: dry run first, both architectures tested.

### Option C: Two copies in step

- ✅ Nothing changes.
- ❌ Two copies of every version to move together, and shellcheck unpinned.

---

## 🔗 Traceability & Links

- [`.github/actions/toolchain/`](../../.github/actions/toolchain/README.md):
  the action, and why it belongs only in jobs that run checks
- [`toolchain/README.md`](../../toolchain/README.md): moving a version, now
  only here
- [ADR-0002](ADR-0002-One-Installer-For-The-Image-And-Cloud-Sessions.md): the
  installer the action runs
- [ADR-0003](ADR-0003-Release-The-Image-From-Cut-Release.md): the release that
  moves `v1`

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
