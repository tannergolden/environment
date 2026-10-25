<!--
title: '🐳 GOLDEN IMAGE'
description: 'The development environment every repository on the account shares: one pinned, versioned container image holding the toolchain the standards'' checks run on, published once and pulled by tag. Read it before you add a tool or change a version.'
type: index
-->

<div align="center">

# 🐳 GOLDEN IMAGE

<a name="top"></a>

**One pinned machine for every repository, so a check means the same thing everywhere.**

_Defined once. Pulled everywhere._

</div>

---

## 💡 What This Is

The repository that defines the machine every piece of work runs on: Ubuntu
24.04, git, Python 3.12, Node.js 22, and every tool the
[standards](https://github.com/tannergolden/standards)' checks run, each at an
exact version. It publishes them as one container image,
`ghcr.io/tannergolden/environment`, and a repository points at the image by
tag instead of carrying its own copy, the way it already calls
`tannergolden/standards@v1` instead of copying workflows.

A development container on a Mac, a Codespace and a Claude Code cloud session
then get the same tools at the same versions. A check that passes or fails
does so because of the code, not because two machines had different tools.

> [!IMPORTANT]
> **Status: built, waiting on its first release.** The image, its tests, the
> release and the cloud setup script are all here and tested. Nothing is
> published until 🏷️ Cut Release cuts `v1.0.0`: see [Releasing](#-releasing).

---

## 🎯 What It Fixes

- **The development container is copied into every repository, not called.**
  Each one generated from the templates carries the same `devcontainer.json`,
  on the moving `mcr.microsoft.com/devcontainers/base:ubuntu` tag, with its
  features resolved when it is built and gitleaks taken from Ubuntu's archive,
  a release behind the one CI scans with. None of the other check tools is in
  it.
- **Versions are pinned by hand, in several places.** The standards keep ruff
  and pytest in three files, and actionlint and zizmor in two workflows each,
  while `.github` runs markdownlint-cli2 with no version at all.
- **A cloud session brings its own.** A Claude Code cloud session on this
  account carried ruff 0.16.9 in October 2026, where the standards pin 0.15.8,
  and none of actionlint, zizmor, shellcheck, gitleaks, typos or lychee.
- **A fix means editing every copy.** One change here reaches them all.

---

## 🧱 What It Holds

| Part                                | What it is                                                                                                                                                                                                                                                                                      |
| :---------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The image                           | Ubuntu 24.04 pinned by digest; git, curl, make and Python 3.12 with pip, from Ubuntu's archive; Node.js 22; and actionlint, gitleaks, lychee, shellcheck, typos, ruff, pytest, zizmor, PyYAML, Prettier and markdownlint-cli2, each at the version `toolchain/` pins. A `vscode` user with sudo |
| [`Dockerfile`](Dockerfile)          | The image's definition, at the root, where the release's publish job looks for it                                                                                                                                                                                                               |
| [`toolchain/`](toolchain/README.md) | Every pin, and the installer the image and a cloud session both run                                                                                                                                                                                                                             |
| [`setup/`](setup/README.md)         | The Claude Code cloud setup script, pinned to a release                                                                                                                                                                                                                                         |
| [`tests/`](tests/README.md)         | Checks that the pins agree, that the installer refuses what it should, and that a built image holds each tool at its pinned version                                                                                                                                                             |
| Each release                        | The image for `linux/amd64`, for Codespaces and Actions, and `linux/arm64`, for Apple silicon, each built natively, with a provenance attestation, and an SBOM of each architecture on the release                                                                                              |

Each release tags the image with its version, such as `1.0.0`, the moving
major `1`, and `latest`. A repository that wants exactness pins the image's
digest instead.

**What is exact and what is not.** The base is pinned by digest, and every tool
the checks run by version and checksum. The packages from Ubuntu's archive are
its current ones when the image is built, so a rebuild takes Ubuntu's security
fixes. A published image never changes.

---

## 🔌 How A Repository Uses It

```jsonc
// .devcontainer/devcontainer.json
{
  "name": "My Project",
  "image": "ghcr.io/tannergolden/environment:1",
}
```

The image's own label makes a development container work as `vscode`, so that
is the whole file. Add `features` or a `postCreateCommand` for what one project
needs beyond it.

- **A repository generated from the templates**: once the templates carry this
  file, 🔄 Template Sync brings it to each repository that runs it, as a pull
  request.
- **A Codespace**: it starts from the same file, and your dotfiles'
  `install.sh` then installs the agent rules from the intelligence hub, with
  the `curl` and `python3` the image carries.
- **A Claude Code cloud session**: it starts from its own image, and takes the
  [cloud setup script](setup/README.md) instead, which installs the same tools
  at the same versions for the session's user.
- **CI**: the standards' checks install their tools on the runner, at the
  versions this image mirrors. Running them inside the image would be a change
  to the standards, not to this repository.

`:1` is read when a container is built, so an open container keeps its tools
until it is rebuilt.

---

## 🗺️ Where It Sits

| Repository     | Decides                                                              |
| :------------- | :------------------------------------------------------------------- |
| `standards`    | Which checks run, and how                                            |
| `environment`  | Which tools, at which versions, those checks run with                |
| `path`         | A new repository's folders, workflow stubs and development container |
| `intelligence` | How AI agents behave, not what their machine has installed           |
| `dotfiles`     | Your Mac's own shell and apps, and the agent rules on it             |

---

## 🚀 Releasing

1. **Dry run.** Dispatch 🏷️ Cut Release from the Actions tab with the version,
   such as `v1.0.0`, and `dry-run` left on. It lints, builds and tests the
   image on that commit, then builds both architectures natively, and
   publishes nothing.
2. **Release.** Dispatch it again from `Development` with `dry-run` off. It
   tags `v1.0.0` and moves `v1`, pushes the image as `1.0.0`, `1` and `latest`
   with its provenance attestation, and attaches an SBOM of each architecture
   to the release.
3. **Check the package is public**, on its page under this repository's
   Packages. A development container elsewhere pulls it without signing in
   only if it is; if it is not, change its visibility in the package's
   settings.
4. **Pin the cloud sessions.** `make cloud-setup VERSION=v1.0.0` prints the
   setup script for that release; [`setup/`](setup/README.md) says where it
   goes.

A release changes what every repository naming `:1` gets at its next rebuild,
so treat one as a production change to all of them at once.

---

## 🧭 After The First Release

What this repository cannot do on its own:

- [ ] Point both golden path templates' `.devcontainer/devcontainer.json` at
      `ghcr.io/tannergolden/environment:1`, together, and release them, so
      🔄 Template Sync offers it to every repository generated from them.
- [ ] Do the same by hand where a container does not come from them, such as
      the knowledge vault template's.
- [ ] Update the standards' Environment & Technologies document, which still
      says to pin runtimes with version managers.
- [ ] Decide whether the standards' checks run inside the image, which would
      make CI and every container one machine, and would put GHCR in the path
      of every repository's CI.

---

## 🌿 The Workflows

This repository holds **triggers**. The logic lives in
[`tannergolden/standards`](https://github.com/tannergolden/standards) and is
pulled in by `uses:`, so a fix there reaches this repository without a commit
here. 🏷️ Cut Release is the one with jobs of its own.

| Workflow                   | Gives you                                                                                                    |
| :------------------------- | :----------------------------------------------------------------------------------------------------------- |
| `checks.yml`               | The gates: `make lint` and `make test`, which builds and tests the image, secret scan, CodeQL, workflow lint |
| `semantic-pr.yml`          | The `pr` check: PR title, branch name, commit messages, DCO sign-off                                         |
| `governance.yml`           | Onboarding, triage, stale sweep, slash commands                                                              |
| `cut-release.yml`          | The release: the tags, the image for both architectures, and their SBOMs                                     |
| `release.yml`              | Draft notes, publish assets, registries, prune old releases on request                                       |
| `maintenance.yml`          | Prunes stale deployments; deletes draft releases on request                                                  |
| `prune-runs.yml`           | Prunes workflow run history, with its logs and artifacts                                                     |
| `lifecycle.yml`            | Claimed this repository once; tells you when a new major exists                                              |
| `dependabot-automerge.yml` | Approves and queues Dependabot's patch and minor updates                                                     |
| `ci-failure-alert.yml`     | Opens an issue when a watched workflow fails, closes it on green                                             |
| `apply-standards.yml`      | Dispatch-only. The label taxonomy, the settings and branch protection                                        |
| `auto-format.yml`          | Formats what a push touched                                                                                  |
| `preview-deploy.yml`       | Deploys pushes to a preview target, once one is configured                                                   |
| `verify-stubs.yml`         | Proves every job's permission ceiling matches its called workflow                                            |
| `auto-index.yml`           | Redraws every folder log and index after a push, as a pull request                                           |
| `scorecard.yml`            | A weekly OpenSSF Scorecard score, filed under code scanning                                                  |
| `template-sync.yml`        | Proposes the template's later fixes as one pull request, when run                                            |
| `intelligence-sync.yml`    | Proposes the shared agent rules as one pull request, every Monday                                            |

**Do not rename the job ids** `ci` and `secrets` (in `checks.yml`) or `pr` (in
`semantic-pr.yml`). A called workflow reports its checks as
`<job id> / <job name>`, so branch protection depends on them.

---

## 🔑 Tokens

- **🎯 Apply Standards** applies the label taxonomy with no token. Writing the
  settings and the rulesets needs an `ADMIN_TOKEN` with **Administration: Read
  and write** and nothing else:
  [Creating the ADMIN_TOKEN](https://github.com/tannergolden/standards/blob/Development/docs/operations/Branch-Protection.md#-creating-the-admin_token).
- **🔄 Template Sync** needs a `BOT_ACCESS_TOKEN` to update the files under
  `.github/workflows/`, which GitHub's default token cannot write. Without it,
  those files wait in an issue while everything else arrives.
- **🏷️ Cut Release** needs none: GHCR takes the run's own token.

---

## 📦 What's Inside

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                       | Purpose                                                                                                                                                                                             |
| :------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`.devcontainer/`](.devcontainer/README.md) | The development container for working on the environment: the image this repository defines, built from its own Dockerfile, with Docker inside to build and test it.                                |
| [`.github/`](.github/)                      | Everything GitHub reads from this repository: the workflows and the scripts they run, the issue and discussion forms, and the community health files.                                               |
| [`.vscode/`](.vscode/README.md)             | The VS Code settings and extension recommendations this repository shares, and why every other file in this folder stays out of git.                                                                |
| [`assets/`](assets/README.md)               | Where this project keeps what presents it: four folders to start, a name ready for every other kind, and the rules every file follows.                                                              |
| [`docs/`](docs/README.md)                   | Where this project keeps its own documents, and where the engineering standards it follows actually live.                                                                                           |
| [`setup/`](setup/README.md)                 | The setup script that installs the toolchain into every Claude Code cloud session, pinned to one release, checked file by file, and unable to stop a session from starting.                         |
| [`tests/`](tests/README.md)                 | The tests that hold the toolchain to its pins: the unit tests that need nothing but Python, and the image tests that check a built image.                                                           |
| [`toolchain/`](toolchain/README.md)         | Every tool the image and a cloud session install, the exact version and checksum of each, the installer both run, and how to move a version.                                                        |
| [`.dockerignore`](.dockerignore)            | Docker sends a build only what the Dockerfile reads: the toolchain it installs.                                                                                                                     |
| [`.editorconfig`](.editorconfig)            | The editor settings every file shares: UTF-8, LF line endings, a final newline, two-space indents, and each language's own formatter defaults.                                                      |
| [`.env.example`](.env.example)              | Environment variable template for this project.                                                                                                                                                     |
| [`.gitattributes`](.gitattributes)          | Git attributes - line endings, diffs, and what counts as binary                                                                                                                                     |
| [`.gitignore`](.gitignore)                  | &#x1F5C4;&#xFE0F; Universal Ignore Patterns                                                                                                                                                         |
| [`.markdownlint.json`](.markdownlint.json)  | Repository-wide markdownlint rules. Discovered by mechanism, which is why this lives at the root.                                                                                                   |
| [`AGENTS.md`](AGENTS.md)                    | How AI coding agents work in environment: the universal rules first, then this repository's own.                                                                                                    |
| [`Dockerfile`](Dockerfile)                  | The machine every repository's checks run on: Ubuntu 24.04 pinned by digest, git, Python 3.12, Node.js 22, and every tool the standards' checks run, each at the exact version toolchain/ pins.     |
| [`LICENSE`](LICENSE)                        | MIT License                                                                                                                                                                                         |
| [`Makefile`](Makefile)                      | The commands CI runs, so a contributor runs the same ones: &#x1F6A6; Checks calls `make lint` and `make test`, and &#x1F3F7;&#xFE0F; Cut Release calls them again on the commit it is about to tag. |
| [`README.md`](README.md)                    | This file.                                                                                                                                                                                          |

<!-- AUTO-INDEX:END -->

The root carries only what a tool discovers there by mechanism.

**Every folder carries a `README.md` that logs each file inside it**, with one
exception. GitHub shows a README in `.github/` in place of this page, so that
folder's own files are logged here instead. 🗂️ Machined Indexes redraws both
tables after every push:

<!-- AUTO-INDEX:BEGIN dir=./.github style=log -->

| Entry                                                           | Purpose                                                                                                                                              |
| :-------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`actions/`](.github/actions/README.md)                         | The composite actions this repository keeps for its own workflows, and for any other repository that calls them.                                     |
| [`DISCUSSION_TEMPLATE/`](.github/DISCUSSION_TEMPLATE/README.md) | The discussion category forms, each bound by its file name to the category it shapes.                                                                |
| [`ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE/README.md)           | The issue forms a reporter chooses from, and the chooser configuration that offers them.                                                             |
| [`scripts/`](.github/scripts/README.md)                         | The checks this repository runs on its own configuration, and the tests that guard them.                                                             |
| [`workflows/`](.github/workflows/README.md)                     | Every workflow in this repository: the name it shows in the Actions tab, what triggers it, and what it does.                                         |
| [`ACCESSIBILITY.md`](.github/ACCESSIBILITY.md)                  | The accessibility this project aims for, how to report a barrier, and what happens after you do.                                                     |
| [`CODE_OF_CONDUCT.md`](.github/CODE_OF_CONDUCT.md)              | The code of conduct governing participation in this project, how to report a violation, and how harm is addressed and repaired.                      |
| [`CODEOWNERS`](.github/CODEOWNERS)                              | Folder-based ownership rules                                                                                                                         |
| [`commit-template.txt`](.github/commit-template.txt)            | &lt;type&gt;(&lt;scope&gt;): &lt;emoji&gt; &lt;subject starting lowercase, no em dash&gt;                                                            |
| [`CONTRIBUTING.md`](.github/CONTRIBUTING.md)                    | How to contribute, covering branching, commits, code style, testing, and the pull-request process.                                                   |
| [`dependabot.yml`](.github/dependabot.yml)                      | Dependabot - automated dependency updates                                                                                                            |
| [`FUNDING.yml`](.github/FUNDING.yml)                            | &#x1F496; Funding Options                                                                                                                            |
| [`GOVERNANCE.md`](.github/GOVERNANCE.md)                        | How this project is led, who decides what, how access continues, and the review and security standards every change meets.                           |
| [`pull_request_template.md`](.github/pull_request_template.md)  | This template becomes the body of your pull request.                                                                                                 |
| [`release.yml`](.github/release.yml)                            | GitHub auto-generated release notes configuration.                                                                                                   |
| [`SECURITY.md`](.github/SECURITY.md)                            | How to report a vulnerability privately, what happens after you do, which versions receive security fixes, and the protections this repository runs. |
| [`SUPPORT.md`](.github/SUPPORT.md)                              | Where to get help with this repository - the right channel for every kind of question.                                                               |
| [`template-sync`](.github/template-sync)                        | Every path tannergolden/path ships, and whether &#x1F504; Template Sync, when you run it, keeps it current in this repository.                       |
| [`template-sync.lock`](.github/template-sync.lock)              | Where each file here was last synced from.                                                                                                           |
| [`template-sync.md`](.github/template-sync.md)                  | How this repository takes its template's later fixes when you run &#x1F504; Template Sync, what you control, and what waits on you.                  |
| [`VULNERABILITY_REPORT.yml`](.github/VULNERABILITY_REPORT.yml)  | Report a suspected vulnerability privately, so the maintainers can fix it before it is made public.                                                  |

<!-- AUTO-INDEX:END -->

---

## 📚 The Standards

Everything about how to branch, review, release and secure a repository lives
in the [Standards Index](https://github.com/tannergolden/standards/blob/Development/docs/README.md).
This repository follows it **by link**.

---

## 🔒 Licence

MIT. See [`LICENSE`](LICENSE).

---

<div align="center">

**One image. Every machine.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by [@tannergolden](https://github.com/tannergolden). Distributed under the terms in [LICENSE](/LICENSE).

</div>
