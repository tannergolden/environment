<!--
title: '🐳 DEVELOPMENT CONTAINER'
description: 'The development container for working on the environment: the image this repository defines, built from its own Dockerfile, with Docker inside to build and test it.'
type: index
-->

<div align="center">

# 🐳 DEVELOPMENT CONTAINER

<a name="top"></a>

**The machine this repository defines, built from the change you are making.**

_Work inside the toolchain you are changing._

</div>

---

## 💡 What This Folder Is For

Open the repository in a dev container - <kbd>Reopen in Container</kbd> in VS
Code, or a Codespace - and this folder decides what you get: the image built
from this repository's own [`Dockerfile`](../Dockerfile), not the published
one. A change to [`toolchain/`](../toolchain/README.md) is tried in the
container it makes, before 🏷️ Cut Release publishes it to every repository.

It adds Docker, through the `docker-in-docker` feature, so `make test` builds
the image and checks every tool in it from inside. Docker's engine, CLI and
buildx come from Microsoft's signed moby packages; the feature's own downloads
of the newest buildx and of Compose, which nothing checks against a pin, are
switched off. When it is created it does
what the template's container does: installs the scripts' requirements,
switches on the [git hooks](../.github/scripts/hooks/README.md), and sets the
commit message template. The image already holds gitleaks, which the
`pre-commit` hook scans with.

**This is the one repository whose container builds the image.** Every other
repository will name the published image instead, once the templates point at
it, as the [README](../README.md#-how-a-repository-uses-it) shows, which is why the two
files here are switched off in [`.github/template-sync`](../.github/template-sync):
a sync never puts the template's container back.

`.gitattributes` marks this folder `export-ignore`, so `git archive` leaves it
out of a source tarball.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                    | Purpose                                                                      |
| :--------------------------------------- | :--------------------------------------------------------------------------- |
| [`devcontainer.json`](devcontainer.json) | Development container for this repository: the image it defines, built here. |
| [`README.md`](README.md)                 | This file.                                                                   |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push to the default branch,
from what each file says about itself.

---

## ⚙️ Keeping It In Step

- A change to the `Dockerfile` or to `toolchain/` takes effect here at the
  next **Rebuild Container**.
- Not everything here is pinned. Resolved when the container is built are
  the Ubuntu packages the `Dockerfile` adds, as in the published image; the
  `docker-in-docker` feature, at its newest `4.x`, which Dependabot's
  `devcontainers` ecosystem proposes new versions of like any other
  feature; and the moby packages that feature installs, with the key that
  signs them, from Microsoft's apt repository.
- It works as `vscode`, and `devcontainer.json` says so itself: building
  the image here, the dev container tools take their settings from the
  `Dockerfile`'s base rather than from the label the image sets, and the
  label they write when they add the feature replaces it.
- Building behind a proxy that inspects TLS needs its CA bundle as the
  `ca-bundle` build secret. This file passes none, since the bundle's path is
  each machine's own: build from a terminal with `make build BUILD_FLAGS=...`,
  as the [Makefile](../Makefile) says.

> [!NOTE]
> **There is no `settings` block, deliberately.** VS Code reads
> [`.vscode/settings.json`](../.vscode/settings.json) inside the container like
> anywhere else, so a copy here would be a second source of truth, and the copy
> that drifts is always the one nobody remembers.

`devcontainer.json` is JSON with comments, which is what dev containers read.
The repository validator parses it the same way, so a comment is never reported
as an error.

---

<div align="center">

**Build the machine, then work inside it.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the terms in [LICENSE](/LICENSE).

</div>
