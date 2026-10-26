<!--
title: '🧰 TOOLCHAIN'
description: 'Every tool the image and a cloud session install, the exact version and checksum of each, the installer both run, and how to move a version.'
type: index
-->

<div align="center">

# 🧰 TOOLCHAIN

<a name="top"></a>

**Every tool the standards' checks run, pinned once, installed one way.**

_One installer. One set of pins. Two machines._

</div>

---

## 💡 What This Folder Is For

The pins and the installer. The [`Dockerfile`](../Dockerfile) runs
[`install.sh`](install.sh) as it builds the image, a Claude Code cloud
session runs the same file from a release, through the
[cloud setup script](../setup/README.md), and a GitHub Actions job runs it
through the [toolchain action](../.github/actions/toolchain/README.md), which
is how the standards' checks get their tools. All three install the same
check tools at the same versions, by the same steps. A cloud session or a job
keeps its own Python, and its own Node.js when that is 22 or newer.

| Pinned in         | What                                                                                                   | Started from                                                |
| :---------------- | :----------------------------------------------------------------------------------------------------- | :---------------------------------------------------------- |
| `versions`        | Node.js, actionlint, gitleaks, lychee, shellcheck and typos: a version, and a SHA-256 per architecture | Its header says which check each one came from              |
| `requirements.in` | PyYAML, pytest, ruff and zizmor                                                                        | The standards' pins, and the scripts' PyYAML                |
| `package.json`    | markdownlint-cli2 and Prettier                                                                         | The standards' Prettier; markdownlint-cli2's newest release |
| The `Dockerfile`  | Ubuntu 24.04, by digest                                                                                | The Ubuntu release CI's `ubuntu-latest` runners use today   |

Each version started as the one the standards' checks ran when this folder
took them over. This folder owns them now: the standards install them through
the toolchain action, so a version moves here and the checks follow.

`requirements.txt` and `package-lock.json` are compiled from the two pin files
by `make lock`, never written by hand: every package in them, the ones the
tools depend on included, is pinned with its hashes.

**Nothing unchecked is installed, and a failed download changes nothing.**
`install.sh` fetches everything into a scratch folder and checks it there
first: every archive against its SHA-256, every wheel against its hash, with
pip resolving nothing of its own and building nothing from source, and every
npm package against its integrity hash, with `npm ci` running no install
scripts. Only then does it install anything, so a mismatch, or a host that
cannot be reached, stops it before it has changed anything.
[`tests/`](../tests/README.md) holds it to that.

---

## 🔁 Moving A Version

1. Change the pin: a version and both of its SHA-256 sums in `versions`, or
   a line in `requirements.in` or `package.json`.
2. For `versions`, take each sum from the project's own published checksums
   where it publishes them, and say in the file's header which ones it does
   not.
3. Run `make lock` after a change to `requirements.in` or `package.json`. It
   needs uv and npm.
4. Run `make test`, which builds the image and checks every version in it
   against the pins.
5. Change nothing in the standards: their checks install every version from
   here, through the toolchain action.

A release then publishes it: nothing reaches a repository's development
container until 🏷️ Cut Release moves `1`, and nothing reaches its checks until
it moves `v1`, the tag the standards call the toolchain action at.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                    | Purpose                                                                                                                                 |
| :--------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------- |
| [`install.sh`](install.sh)               | Installs the toolchain: every tool the standards' checks run, at the versions pinned in the files beside this one.                      |
| [`package-lock.json`](package-lock.json) | Compiled from package.json by make lock: every Node.js package the two tools need, each with its integrity hash.                        |
| [`package.json`](package.json)           | The Node.js tools the image and the cloud setup install, markdownlint-cli2 and Prettier, at exact versions.                             |
| [`README.md`](README.md)                 | This file.                                                                                                                              |
| [`requirements.in`](requirements.in)     | The Python tools the image and the cloud setup install, at the versions the standards pin, and the PyYAML the repository's scripts pin. |
| [`requirements.txt`](requirements.txt)   | This file was autogenerated by uv via the following command: make lock                                                                  |
| [`versions`](versions)                   | Every tool install.sh downloads, one value per line, read by install.sh and by the tests.                                               |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push to the default branch,
from what each file says about itself.

---

<div align="center">

**Pinned once. Installed the same way everywhere.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the terms in [LICENSE](/LICENSE).

</div>
