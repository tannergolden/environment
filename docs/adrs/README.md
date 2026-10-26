<!--
title: '🧭 ARCHITECTURE DECISIONS'
description: 'Architecture decision records, one file per decision, each logged with its status, date and evidence.'
type: index
-->

<div align="center">

# 🧭 ARCHITECTURE DECISIONS

<a name="top"></a>

**Every significant decision this project has made, and why, one record each.**

_One decision per record. One row per decision._

</div>

---

## 💡 What This Folder Is For

An architecture decision record (ADR) captures one significant decision: the
context it was made in, the options weighed, and the consequences accepted.
Every record lives in this folder, one file per decision, and the log below is
their index.

The folder is a living record, not a fill-in form, and its records are **yours
from the first commit**: nothing upstream ever writes, moves or removes one. It
arrives with one decision in it,
[ADR-0001](ADR-0001-Record-Architecture-Decisions.md), the decision to keep
these records, which doubles as a worked example, and gains a row each time a
record is written. Only this README is ever updated from the template - when you
run 🔄 Template Sync - merged with the rows your records add.

---

## 🎯 Why Decisions Are Recorded

The _why_ matters as much as the _what_. An auditable record of how the system
evolved lets every later contributor, human or AI, see the constraints and
trade-offs that shaped it before changing it.

- **Traceability**: every major architectural pivot is documented and numbered.
- **Context**: each decision is recorded with the situation it was made in.
- **Consequences**: the benefits and the technical debt are both written down.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log fields=status,date,evidence -->

| Entry                                                                                                                      | Status   | Date       | Evidence | Purpose                                                                                                                                                                                                                                                                     |
| :------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`ADR-0001-Record-Architecture-Decisions.md`](ADR-0001-Record-Architecture-Decisions.md)                                   | Accepted | 2026-10-24 | N/A      | The decision to record every significant architecture decision as a numbered record in this folder, and the first example of one.                                                                                                                                           |
| [`ADR-0002-One-Installer-For-The-Image-And-Cloud-Sessions.md`](ADR-0002-One-Installer-For-The-Image-And-Cloud-Sessions.md) | Accepted | 2026-10-26 | N/A      | The decision to install the toolchain with one POSIX script, reading one set of pins that mirror the standards, which the image runs as it is built and a Claude Code cloud session runs through its setup script, and which checks everything before it installs anything. |
| [`ADR-0003-Release-The-Image-From-Cut-Release.md`](ADR-0003-Release-The-Image-From-Cut-Release.md)                         | Accepted | 2026-10-26 | N/A      | The decision to publish the image in the same &#x1F3F7;&#xFE0F; Cut Release run that tags the version, after testing each architecture on a runner of its own, with SBOMs made by jobs that can only read, and with every version kept.                                     |
| [`ADR-0004-Pin-The-Cloud-Setup-To-A-Release.md`](ADR-0004-Pin-The-Cloud-Setup-To-A-Release.md)                             | Accepted | 2026-10-26 | N/A      | The decision to give Claude Code cloud sessions the toolchain through a setup script printed for one release, with the SHA-256 of every file it downloads, that installs for the session user and never fails the session.                                                  |
| [`ADR-0005-Install-The-Toolchain-In-CI-Through-An-Action.md`](ADR-0005-Install-The-Toolchain-In-CI-Through-An-Action.md)   | Accepted | 2026-10-26 | N/A      | The decision to have the standards install every check tool through this repository's toolchain action, which runs the image's own installer, so this repository owns the versions and every repository's checks run the image's tools.                                     |
| [`README.md`](README.md)                                                                                                   | -        | -          | -        | This file.                                                                                                                                                                                                                                                                  |

<!-- AUTO-INDEX:END -->

**This log is the decision index, and nobody types its rows.** 🗂️ Machined
Indexes redraws it after every push to the default branch, from each record's
own frontmatter.
**Status** is Proposed, Accepted, Superseded, or Deprecated; **Date** is when
the decision was made; **Evidence** links the research report(s) that informed
it, or reads N/A.

---

## 🌿 Adding A Decision

- [ ] Copy the [ADR template](../templates/ADR.md) into this folder as
      `ADR-NNNN-Short-Slug.md`, taking the next number.
- [ ] Set `type: record`, `status`, `date`, and `evidence` in its frontmatter, and write every
      section.
- [ ] Propose it in a pull request. Once merged, it is **Accepted**.

A later decision supersedes an earlier one rather than rewriting it: mark the
old record **Superseded** and link the new one.

---

## 🔗 See also

- [Documentation index](../README.md) - every document this project keeps
- [Standards Index](https://github.com/tannergolden/standards/blob/Development/docs/README.md) - the canonical engineering standards

---

<div align="center">

**Write the decision down while the reasons are still fresh.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the terms in [LICENSE](/LICENSE).

</div>
