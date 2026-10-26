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

[`action.yml`](action.yml) runs [`toolchain/install.sh`](../../../toolchain/README.md)
for the job's user, then puts `~/.local/bin` on `PATH`, so every step after it
runs each check tool at the version the image holds. It is how the standards'
checks get their tools, and through them every repository's CI:

```yaml
- uses: tannergolden/environment/.github/actions/toolchain@v1
```

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

`@v1` moves with each release, as the image's `1` tag does: a release reaches
every job that calls it the next time that job runs. 🚦 Checks proves it on a
runner after every change here, in its `toolchain` job.

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
