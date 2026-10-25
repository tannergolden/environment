<!--
title: '🧪 TESTS'
description: 'The tests that hold the toolchain to its pins: the unit tests that need nothing but Python, and the image tests that check a built image.'
type: index
-->

<div align="center">

# 🧪 TESTS

<a name="top"></a>

**The tests that hold the toolchain to its pins.**

_Fast checks on the pins, then the image itself._

</div>

---

## 💡 What This Folder Is For

Two kinds of test, run two ways:

| Kind                        | Needs            | Run by                              | Proves                                                                     |
| :-------------------------- | :--------------- | :---------------------------------- | :------------------------------------------------------------------------- |
| `test_*.py`, here           | Python           | `make test-unit`                    | The pins are complete and agree, the installer refuses what it should      |
| [`image/`](image/README.md) | Docker, an image | `make test-image`, which builds one | The image holds every tool at its pinned version, and the checks run in it |

`make test` runs both, and is the `test-command` that
[`.github/workflows/checks.yml`](../.github/workflows/checks.yml) runs on every
pull request; 🏷️ Cut Release runs it again on the commit it is about to tag.
None of them reaches the network: the installer's tests point its downloads at
a local folder, and the image tests run every container with no network.

Every test is standard-library `unittest`, and each reads what it expects from
the pins themselves, so moving a version is the whole of changing its test.

This directory is **yours**. Nothing here syncs: 🔄 Template Sync leaves this
whole folder to this repository, this README included.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                        | Purpose                                                                                                                                                              |
| :------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`image/`](image/README.md)                  | The tests that check a built image: every tool at its pinned version, Python, Node.js and git, the development user, and the account's own checks running inside it. |
| [`README.md`](README.md)                     | This file.                                                                                                                                                           |
| [`test_cloud_setup.py`](test_cloud_setup.py) | Tests for the Claude Code cloud setup script.                                                                                                                        |
| [`test_install.py`](test_install.py)         | Tests for the installer's refusals.                                                                                                                                  |
| [`test_toolchain.py`](test_toolchain.py)     | Tests that the toolchain's pins are complete and agree with each other.                                                                                              |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push to the default branch,
from what each file says about itself.

---

<div align="center">

**Every pin a promise, and a test that keeps it.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the terms in [LICENSE](/LICENSE).

</div>
