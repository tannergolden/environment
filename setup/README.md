<!--
title: '☁️ CLOUD SETUP'
description: 'The setup script that installs the toolchain into every Claude Code cloud session, pinned to one release, checked file by file, and never failing a session''s setup.'
type: index
-->

<div align="center">

# ☁️ CLOUD SETUP

<a name="top"></a>

**The image's tools in every Claude Code cloud session, from a pinned release.**

_Pinned at the source. Silent when it cannot help._

</div>

---

## 💡 What This Folder Is For

A Claude Code cloud session starts from its own image, not this one, and
takes a setup script instead. [`claude-cloud-setup.sh`](claude-cloud-setup.sh)
downloads one release's installer and pins, checks each file against its
SHA-256 before anything runs, and runs the installer for the session's user.
Every check tool lands in `~/.local/bin`, ahead of the copies the session's
image carries, at the version the image holds; the session keeps its own
Python, and its own Node.js when that is 22 or newer.

**It always exits 0.** The toolchain is something a session can start
without, so every failure prints a notice instead, and the session starts with
the tools its own image has. The installer fetches and checks everything
before it installs anything, so a failed download leaves those tools as they
were, and it is stopped if it runs past 15 minutes.

---

## 🚀 Installing It

1. Cut a release, then print the script with that release's pins:

   ```bash
   git fetch --tags
   make cloud-setup VERSION=v1.0.0
   ```

2. Paste the output into the cloud environment's settings: open the
   environment menu in a session's title bar, choose Edit, and put it under
   Setup script. New sessions run it.
3. After each new release, print it again and replace the old one.

**It shares the field.** The script runs in a subshell and never exits the
one it is pasted into, so it goes above another setup script in the same
field. Put it above the intelligence hub's, whose last line exits.

The copy in this folder keeps placeholders where the pins go, and installs
nothing until they are filled.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                            | Purpose                                                                |
| :----------------------------------------------- | :--------------------------------------------------------------------- |
| [`claude-cloud-setup.sh`](claude-cloud-setup.sh) | Installs the environment's toolchain into a Claude Code cloud session. |
| [`README.md`](README.md)                         | This file.                                                             |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push to the default branch,
from what each file says about itself.

---

<div align="center">

**Every cloud session starts with the toolchain, or starts anyway.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the terms in [LICENSE](/LICENSE).

</div>
