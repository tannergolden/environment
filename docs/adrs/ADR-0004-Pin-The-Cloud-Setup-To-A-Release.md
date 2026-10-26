<!--
title: '📄 ADR-0004: PIN THE CLOUD SETUP TO A RELEASE'
description: 'The decision to give Claude Code cloud sessions the toolchain through a setup script printed for one release, with the SHA-256 of every file it downloads, that installs for the session user and never fails the session.'
type: record
status: 'Accepted'
date: '2026-10-26'
evidence: 'N/A'
-->

<div align="center">

# 📄 ADR-0004: PIN THE CLOUD SETUP TO A RELEASE

<a name="top"></a>

**A cloud session gets the image's tools from one release, checked file by file, or keeps its own.**

_Pinned when it is printed. Harmless when it cannot help._

</div>

---

## 📋 Meta Information

| Attribute     | Specification                                                          |
| :------------ | :--------------------------------------------------------------------- |
| **Deciders**  | The maintainers listed in [GOVERNANCE.md](../../.github/GOVERNANCE.md) |
| **Consulted** | Everyone who reviews the pull request that implements it               |
| **Informed**  | The owner, who pastes the script into the cloud environment's settings |

---

## 🎯 Context & Problem Statement

A Claude Code cloud session starts from its own image, which carried ruff
0.16.9 against the standards' 0.15.8 and none of the other check tools, and
it cannot be pointed at this one. It takes a setup script instead, pasted into
the cloud environment's settings, and that field is shared with the
intelligence hub's setup script, which must still run after it. Whatever the
script downloads runs as root on every session start.

---

## 🚦 Decision Drivers

- **Driver 1**: A session gets the same check tools, at the same versions, as
  the image.
- **Driver 2**: Nothing runs that was not pinned before it was downloaded,
  and the script in the repository can never install something nobody pinned.
- **Driver 3**: The script never fails a session, never exits the script it
  is pasted into, and cannot hold a session's start indefinitely.

---

## 🏗️ Considered Options

1. **Option A**: A setup script that installs the tools with each language's
   package manager, at versions written into it.
2. **Option B**: A setup script that downloads the installer from the newest
   release, whatever it is.
3. **Option C**: A setup script printed for one release by
   `make cloud-setup VERSION=vX.Y.Z`, carrying the SHA-256 of each file it
   downloads from that tag, running the image's own installer for the session
   user, and always exiting 0.

---

## ✅ Decision Outcome

**Chosen Option**: Option C, a script printed for one release.

### Rationale for Selection

It runs the same installer the image runs, from the same release, so the tools
match the image (Driver 1, and [ADR-0002](ADR-0002-One-Installer-For-The-Image-And-Cloud-Sessions.md)).
The printer reads each file from the tag, not the working tree, and the copy in
the repository keeps placeholders that match no file, so an unpinned copy
installs nothing (Driver 2). It runs in a subshell, prints a notice for every
failure and exits 0, the installer changes nothing when a download fails, and
the installer is told to stop after 15 minutes (Driver 3). The tools go into
`~/.local/bin`, ahead of the session's own, and the session keeps its own
Python, and its own Node.js when that is 22 or newer.

---

## 📈 Consequence Matrix

| Category         | Impact / Consequence                                                                                                             |
| :--------------- | :------------------------------------------------------------------------------------------------------------------------------- |
| **Positive (+)** | Sessions run the image's check tools; every file is checked against a pin taken from a tag; a failure leaves a session as it was |
| **Negative (-)** | Each release has to be printed and pasted again by hand, so a session stays on the release it was given until then               |
| **Neutral (~)**  | A failure is a notice in the setup output, not an error, so it is quiet by design                                                |

---

## ⚖️ Trade-off Comparative

### Option A: Package managers, versions in the script

- ✅ No release needed.
- ❌ A second list of versions to drift from the image's, and nothing for the
  tools that are not packages.

### Option B: The newest release

- ✅ No re-pasting after a release.
- ❌ What a session runs changes without anyone choosing it, and no pin can be
  written down in advance for a file that has not been released yet.

### Option C: Printed for one release

- ✅ Pinned, checked, and identical to the image.
- ❌ A manual step after every release.

---

## 🔗 Traceability & Links

- [`setup/README.md`](../../setup/README.md): installing the script, and where
  it goes
- [`setup/claude-cloud-setup.sh`](../../setup/claude-cloud-setup.sh) and
  [`.github/scripts/print-cloud-setup.py`](../../.github/scripts/print-cloud-setup.py)
- [ADR-0002](ADR-0002-One-Installer-For-The-Image-And-Cloud-Sessions.md): the
  installer it runs

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
