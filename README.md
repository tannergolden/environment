<!--
title: '🐳 GOLDEN IMAGE'
description: 'The account''s development environment: one pinned, versioned container image holding the tools the standards'' checks run, published once and pulled by tag, and the installer and action that put the same tools in a cloud session and in CI. Read it before you add a tool or change a version.'
type: index
-->

<div align="center">

# 🐳 GOLDEN IMAGE

<a name="top"></a>

**One pinned toolchain behind every repository's checks, so a check means the same thing everywhere.**

_Defined once. Pulled everywhere._

</div>

---

## 💡 What It Is

The account's development machine: Ubuntu 24.04, git, Python 3.12, Node.js
22, and the tools the [standards](https://github.com/tannergolden/standards)'
checks run, each at an exact version. It publishes them as one container
image, `ghcr.io/tannergolden/environment`, which a repository names by tag
instead of carrying a container of its own. The same installer puts the same
tools in a Claude Code cloud session and, through the standards' checks, in
every repository's CI.

So a development container, a Codespace, a cloud session and CI run the same
check tools at the same versions, and a check passes or fails because of the
code, not because two machines had different tools.

- **Status**: Active, released on the `v1` line by 🏷️ Cut Release.

---

## 🚀 Quick Start

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

---

## 📖 Using It

### 🔌 How A Repository Uses It

- **The repositories other repositories call**, the standards and the
  intelligence hub, name the image in their own development containers. A
  repository generated from the templates names it only when it chooses to,
  and then switches off the two `.devcontainer` lines in its
  `.github/template-sync`, so 🔄 Template Sync never merges the template's
  container back.
- **A Claude Code cloud session** takes the [cloud setup script](setup/README.md)
  instead, which installs the same check tools at the same versions.
- **CI**: the standards' checks install their tools with this repository's
  [toolchain action](.github/actions/toolchain/README.md), at `@v1`, so every
  repository that calls them runs the image's tools with nothing to change.

A machine keeps the `:1` it pulled through rebuilds: a new release reaches it
after `docker pull ghcr.io/tannergolden/environment:1`. Each release tags the
image with its version, the moving major `1` and `latest`; a repository that
wants exactness pins the image's digest instead.

### 🧱 What It Holds

| Part                                                                | What it is                                                                                  |
| :------------------------------------------------------------------ | :------------------------------------------------------------------------------------------ |
| [`Dockerfile`](Dockerfile)                                          | The image's definition, at the root, where the release's publish job looks for it           |
| [`toolchain/`](toolchain/README.md)                                 | Every tool's pin, and the installer the image, a cloud session and the toolchain action run |
| [`.github/actions/toolchain/`](.github/actions/toolchain/README.md) | The action that runs that installer in a GitHub Actions job                                 |
| [`setup/`](setup/README.md)                                         | The Claude Code cloud setup script, printed pinned to a release                             |
| [`tests/`](tests/README.md)                                         | Checks that the pins agree, and that a built image holds each tool at its pinned version    |

### 🔖 Releasing

1. **Dry run.** Dispatch 🏷️ Cut Release from the Actions tab with the next
   `vX.Y.Z` and `dry-run` left on. It lints, then builds and tests the image on
   an amd64 runner and an arm64 one, and publishes nothing.
2. **Release.** Dispatch it again with `dry-run` off. It tags the version and
   moves `v1`, pushes the image with its provenance attestation, and attaches an
   SBOM of each architecture to the release.
3. **Check the package is public**, under this repository's Packages, so a
   development container elsewhere can pull it without signing in.
4. **Pin the cloud sessions**: `make cloud-setup VERSION=vX.Y.Z` prints the
   setup script for that release, and [`setup/`](setup/README.md) says where it
   goes.

If a job after the tag fails, re-run the failed jobs within a week; if the
tagging job itself failed after pushing the tag, cut the next patch. A release
changes the tools every repository's checks run, so treat it as a production
change to all of them at once.

[`.github/workflows/README.md`](.github/workflows/README.md) logs every
workflow, and why CI installs the tools through the action rather than running
inside the image is
[ADR-0005](docs/adrs/ADR-0005-Install-The-Toolchain-In-CI-Through-An-Action.md).

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
| [`setup/`](setup/README.md)                 | The setup script that installs the toolchain into every Claude Code cloud session, pinned to one release, checked file by file, and never failing a session's setup.                                |
| [`tests/`](tests/README.md)                 | The tests that hold the toolchain to its pins: the unit tests that need only Python and git, and the image tests that check a built image.                                                          |
| [`toolchain/`](toolchain/README.md)         | Every tool the image, a cloud session and the toolchain action install, the exact version and checksum of each, the installer all three run, and how to move a version.                             |
| [`.dockerignore`](.dockerignore)            | Docker sends a build only what the Dockerfile reads: the toolchain it installs.                                                                                                                     |
| [`.editorconfig`](.editorconfig)            | The editor settings every file shares: UTF-8, LF line endings, a final newline, two-space indents, and each language's own formatter defaults.                                                      |
| [`.env.example`](.env.example)              | Environment variable template for this project.                                                                                                                                                     |
| [`.gitattributes`](.gitattributes)          | Git attributes - line endings, diffs, and what counts as binary                                                                                                                                     |
| [`.gitignore`](.gitignore)                  | &#x1F5C4;&#xFE0F; Universal Ignore Patterns                                                                                                                                                         |
| [`.markdownlint.json`](.markdownlint.json)  | Repository-wide markdownlint rules. Discovered by mechanism, which is why this lives at the root.                                                                                                   |
| [`AGENTS.md`](AGENTS.md)                    | How AI coding agents work in environment: the universal rules first, then this repository's own.                                                                                                    |
| [`Dockerfile`](Dockerfile)                  | The account's development machine: Ubuntu 24.04 pinned by digest, git, Python 3.12, Node.js 22, and the tools the standards' checks run, each at the exact version toolchain/ pins.                 |
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

## 🤝 Getting Involved

- **Questions**: [`SUPPORT.md`](/.github/SUPPORT.md) says where to ask.
- **A bug or an idea**: open an issue from one of the forms.
- **A change**: [`CONTRIBUTING.md`](/.github/CONTRIBUTING.md) explains how,
  every change follows the
  [standards](https://github.com/tannergolden/standards/blob/Development/docs/README.md)
  by link, and every contribution follows the
  [code of conduct](/.github/CODE_OF_CONDUCT.md).
- **Who decides**: [`GOVERNANCE.md`](/.github/GOVERNANCE.md) names the
  maintainers.

---

## 🛡️ Security

Report a vulnerability privately, never in an issue:
[`SECURITY.md`](/.github/SECURITY.md) says how, and how fast a fix follows.

---

## ⚖️ Licence

This repository's own files are released under the terms in [LICENSE](/LICENSE).
The image redistributes software under each one's own licence: inside it, each
pinned tool's licence is in `/opt/environment/licenses/<tool>/`, and Ubuntu's
packages' in `/usr/share/doc/<package>/copyright`.

---

<div align="center">

**One image. Every machine.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by [@tannergolden](https://github.com/tannergolden). Distributed under the terms in [LICENSE](/LICENSE).

</div>
