<!--
title: '🧰 TOOLCHAIN ACTION'
description: 'The composite action that installs the pinned check tools in a GitHub Actions job, from the release it is called at, so CI runs the same tools as the image.'
type: index
-->

<div align="center">

# 🧰 TOOLCHAIN ACTION

<a name="top"></a>

**The image's check tools in any GitHub Actions job, from one release.**

_One `uses:` line. The same tools as the image._

</div>

---

## 💡 What This Folder Is For

[`action.yml`](action.yml) runs [`toolchain/install.sh`](../../../toolchain/install.sh)
for the job's user, then puts `~/.local/bin` on `PATH`, so every step after it
runs each check tool at the version the image holds. It is how the standards'
checks get their tools, and through them every repository's CI:

```yaml
- uses: tannergolden/environment/.github/actions/toolchain@v1
  with:
    tools: binaries
```

`tools` names what the job runs, so it fetches nothing else, and is `all`
when left out:

| Part       | What it installs                                                          | From                |
| :--------- | :------------------------------------------------------------------------ | :------------------ |
| `binaries` | actionlint, gitleaks, lychee, shellcheck, typos                           | GitHub's releases   |
| `python`   | pytest, ruff, zizmor and PyYAML                                           | PyPI                |
| `node`     | markdownlint-cli2 and Prettier, and Node.js 22 when the runner's is older | npm, and nodejs.org |

List more than one with commas, such as `binaries,python`.

- **The installer comes with it.** GitHub fetches the action from this
  repository's source archive at the tag the caller names, and `toolchain/`
  comes in the same archive, so the pins are that release's. The installer
  checks every download against its pin before it installs anything.
- **A failure fails the job.** The cloud setup never fails a session, but a
  check that ran on the runner's own tools would pass or fail for the wrong
  reason, so this has no fallback.
- **It belongs in a job that runs checks.** Its Python packages go into the
  user site of the `python3` on `PATH`, which comes ahead of site-packages, so
  in front of a repository's own tests it would shadow their pytest or PyYAML.
- **It needs a Linux runner**, amd64 or arm64, with curl, tar and xz, and
  Python 3.12 or newer with pip for the Python tools, as GitHub's Ubuntu
  runners have. A self-hosted runner without them fails the job, with the
  installer saying what is missing.

`@v1` moves with each release, as the image's `1` tag does: a release reaches
every job that calls it the next time that job runs, whatever the caller pins
the standards at. A job that must not move calls it at a release's full
commit SHA instead. 🚦 Checks proves it on a runner after every change here,
in its `toolchain` job, and 🏷️ Cut Release proves it on both architectures
before it tags.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                      | Purpose                                                                                                                                          |
| :------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------- |
| [`action.yml`](action.yml) | Installs the environment's pinned check tools for this job, ahead of the runner's own, and fails the job if any download does not match its pin. |
| [`README.md`](README.md)   | This file.                                                                                                                                       |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push to the default branch,
from what each file says about itself.

---

<div align="center">

**The image's tools, wherever a check runs.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the terms in [LICENSE](/LICENSE).

</div>
