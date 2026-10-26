<!--
title: '📄 ADR-0002: ONE INSTALLER FOR THE IMAGE AND CLOUD SESSIONS'
description: 'The decision to install the toolchain with one POSIX script, reading one set of pins that mirror the standards, which the image runs as it is built and a Claude Code cloud session runs through its setup script, and which checks everything before it installs anything.'
type: record
status: 'Accepted'
date: '2026-10-26'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0002: ONE INSTALLER FOR THE IMAGE AND CLOUD SESSIONS

<a name="top"></a>

**One script and one set of pins, so a tool cannot be two versions on two machines.**

_Checked before it is installed, everywhere it is installed._

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

The environment exists so that a check means the same thing on every machine:
a development container, a Codespace, and a Claude Code cloud session. Before
it, each repository's container floated on a moving base tag with its tools
resolved at build time, and a cloud session brought versions of its own. A
cloud session cannot start from this image: it starts from its own and takes a
setup script. So the same tools have to reach two kinds of machine, by two
routes, at one set of versions, and the versions have to be the ones the
standards' checks run, or the image would disagree with CI.

---

## 🚦 Decision Drivers

- **Driver 1**: A tool must be the same version in the image and in a cloud
  session, and the same version the standards' checks pin.
- **Driver 2**: Nothing may be installed that was not checked against a pin,
  and a failed check, or a host that cannot be reached, must change nothing.
- **Driver 3**: Moving a version must be one change, tested by the same suite,
  for both machines.

---

## 🏗️ Considered Options

1. **Option A**: Install each tool in the Dockerfile, and write the cloud setup
   script as a second, separate list of installs.
2. **Option B**: Use development container features and each language's
   package manager, resolved when the container is built.
3. **Option C**: One POSIX `sh` installer, `toolchain/install.sh`, reading one
   set of pins (`toolchain/versions`, and hash-locked Python and npm manifests),
   run by the Dockerfile system-wide and by the cloud setup for the user.

---

## ✅ Decision Outcome

**Chosen Option**: Option C, one installer reading one set of pins.

### Rationale for Selection

Only one code path can install a tool, so the image and a session cannot drift
apart (Driver 1), and a version moves in one file, which the unit tests and the
image tests both read (Driver 3). Every archive has a SHA-256 per
architecture, every wheel and npm package a hash in its lock, and the installer
fetches and checks all of them into a scratch folder before it installs
anything (Driver 2). It is POSIX `sh` because the image runs it with `/bin/sh`,
and it reads its pins as data, never as shell. Each version mirrors the one the
standards' checks pin, and the header of `toolchain/versions` says where each
comes from.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                                                                                     |
| :--------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Positive (+)** | The same check tools at the same versions in every container and every cloud session, each checked before it is installed                                |
| **Negative (-)** | The pins move by hand, in step with the standards; Dependabot proposes only their security updates. typos and shellcheck publish no checksums to compare |
| **Neutral (~)**  | A cloud session keeps its own Python, and its own Node.js when that is 22 or newer; Ubuntu's own packages in the image float with its archive            |

---

## ⚖️ Trade-off Comparative

### Option A: Two separate lists of installs

- ✅ Each file reads simply on its own.
- ❌ Two lists drift: the first version moved in one and not the other is the
  drift this repository exists to end.

### Option B: Features and package managers resolved at build

- ✅ Little code of its own.
- ❌ Versions are whatever resolves on the day, not the standards' pins, and
  nothing reaches a cloud session, which builds no container.

### Option C: One installer, one set of pins

- ✅ One version everywhere, every byte checked, one place to move a version.
- ❌ An installer to maintain, and pins to move by hand.

---

## 🔗 Traceability & Links

- [`toolchain/README.md`](../../toolchain/README.md): the pins, and how to move
  a version
- [`setup/README.md`](../../setup/README.md): how a cloud session runs the
  installer
- [ADR-0004](ADR-0004-Pin-The-Cloud-Setup-To-A-Release.md): the cloud setup
  script that runs it in a session

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
