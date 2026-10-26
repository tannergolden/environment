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

The repository that defines the machine every piece of work runs on. It holds
the toolchain, meaning a base operating system, the language runtimes and the
exact versions of the tools the
[standards](https://github.com/tannergolden/standards)' checks run, and
publishes it as a container image. Every other repository points at the image
by tag instead of carrying its own copy, the way it already calls
`tannergolden/standards@v1` instead of copying workflows.

A dev container on a Mac and a Codespace then start from the same image, and CI
can run its checks inside it. A check that passes or fails does so because of
the code, not because two machines had different tools.

> [!IMPORTANT]
> **Status: planned, nothing published yet.** This repository holds the
> scaffold it was generated with and the plan below. The first image arrives
> with the first release.

---

## 🎯 What It Fixes

- **The dev container is copied into every repository, not called.** Each one
  generated from the templates carries the same language-neutral
  `.devcontainer/devcontainer.json`, on the moving
  `mcr.microsoft.com/devcontainers/base:ubuntu` tag, with no runtime pinned.
  Opening a repository a month apart can give a different machine.
- **Versions are pinned by hand, in several places.** The standards alone keep
  their ruff and pytest versions in three files.
- **A fix means editing every copy.** One change here reaches them all.

---

## 🧱 What It Will Hold

| Part         | What it is                                                                                                                                                                                                                                           |
| :----------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| The image    | `ghcr.io/tannergolden/environment`: an Ubuntu base pinned by digest, git, Python and Node, and the tools the checks run (ruff, pytest, actionlint, zizmor, shellcheck, gitleaks, typos, lychee, markdownlint and Prettier), each at an exact version |
| `Dockerfile` | The image's definition, at the root, where the release's package job looks for it                                                                                                                                                                    |
| `tests/`     | Checks that the built image holds each tool at the version it promises                                                                                                                                                                               |
| Each release | The image for `linux/amd64`, for Codespaces and Actions, and `linux/arm64`, for Apple silicon, with an SBOM and a provenance attestation from the standards' release workflows                                                                       |

The release's package job tags each image with its version, such as `1.0.0`,
and `latest`. A moving major tag, `1`, needs that job's `tags` input set, and a
repository that wants exactness pins the image's digest instead.

---

## 🔌 How A Repository Uses It

```jsonc
// .devcontainer/devcontainer.json
{
  "name": "My Project",
  "image": "ghcr.io/tannergolden/environment:1",
}
```

- **Every new repository**: [`tannergolden/path`](https://github.com/tannergolden/path)
  ships this file, and 🔄 Template Sync keeps it current in each repository
  generated from it.
- **CI**: a job can run its checks inside the same image, so local and CI match.
- **A Codespace**: your dotfiles' `install.sh` layers your shell on top.
- **A Claude Code cloud session**: it starts from its own image and takes a
  setup script instead, so it installs the same versions by script, as the
  [intelligence](https://github.com/tannergolden/intelligence) hub's cloud
  setup script already installs the agent rules.

---

## 🗺️ Where It Sits

| Repository     | Decides                                                     |
| :------------- | :---------------------------------------------------------- |
| `standards`    | Which checks run, and how                                   |
| `environment`  | Which tools, at which versions, those checks run with       |
| `dotfiles`     | Your personal shell and Mac apps, layered on top            |
| `path`         | A new repository's folders, and the reference to this image |
| `intelligence` | How AI agents behave, not what their machine has installed  |

---

## 🚀 Getting It Built

- [x] Generated from `tannergolden/path`, and initialised.
- [ ] Write the `Dockerfile`, with the base pinned by digest and every tool at
      an exact version.
- [ ] Add the image's tests to `tests/`, and point the `ci` job in
      `checks.yml` at them.
- [ ] Turn on container publishing in `.github/workflows/release.yml`, with
      `container: true` and `container-platforms: 'linux/amd64,linux/arm64'`,
      then run it once as a dry run.
- [ ] Adopt `cut-release.yml`, and cut the first release.
- [ ] Give this repository's own dev container Docker inside it, after putting
      a `#` in front of its two lines in `.github/template-sync`, so a sync
      never swaps it back.
- [ ] Point `path`'s `.devcontainer/devcontainer.json` at the image, so every
      new repository starts on it.
- [ ] Update the standards' Environment & Technologies document, which still
      says to pin runtimes with version managers.
- [x] Add the intelligence stub, so this repository gets its `AGENTS.md`.

---

## 🌿 The Workflows

This repository holds **triggers**. The logic lives in
[`tannergolden/standards`](https://github.com/tannergolden/standards), or for
`intelligence-sync.yml` in
[`tannergolden/intelligence`](https://github.com/tannergolden/intelligence),
and is pulled in by `uses:`, so a fix there reaches this repository without a
commit here. `verify-stubs.yml` and `scorecard.yml` are the two that run steps
of their own instead.

| Workflow                   | Gives you                                                            |
| :------------------------- | :------------------------------------------------------------------- |
| `checks.yml`               | The gates: lint/test/build, secret scan, CodeQL, workflow lint       |
| `semantic-pr.yml`          | The `pr` check: PR title, branch name, commit messages, DCO sign-off |
| `governance.yml`           | Onboarding, triage, stale sweep, slash commands                      |
| `release.yml`              | Draft notes, publish assets, registries, prune superseded releases   |
| `maintenance.yml`          | Prunes stale deployments; deletes draft releases on request          |
| `prune-runs.yml`           | Prunes workflow run history, with its logs and artifacts             |
| `lifecycle.yml`            | Claimed this repository once; tells you when a new major exists      |
| `dependabot-automerge.yml` | Approves and queues Dependabot's patch and minor updates             |
| `ci-failure-alert.yml`     | Opens an issue when a watched workflow fails, closes it on green     |
| `apply-standards.yml`      | Dispatch-only. The label taxonomy and branch protection              |
| `auto-format.yml`          | Formats what a push touched                                          |
| `preview-deploy.yml`       | Deploys pushes to a preview target, once one is configured           |
| `verify-stubs.yml`         | Proves every job's permission ceiling matches its called workflow    |
| `auto-index.yml`           | Redraws every folder log and index after a push, as a pull request   |
| `scorecard.yml`            | A weekly OpenSSF Scorecard score, filed under code scanning          |
| `template-sync.yml`        | Proposes the template's later fixes as one pull request, when run    |
| `intelligence-sync.yml`    | Proposes the shared agent rules as one pull request, every Monday    |
| `cut-release.yml`          | Cuts this repository's releases, once adopted                        |

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

---

## 📦 What's Inside

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                                       | Purpose                                                                                                                                |
| :------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------- |
| [`.devcontainer/`](.devcontainer/README.md) | The language-neutral development container this repository ships, and how to give it the toolchain your project needs.                 |
| [`.github/`](.github/)                      | -                                                                                                                                      |
| [`.vscode/`](.vscode/README.md)             | The VS Code settings and extension recommendations this repository shares, and why every other file in this folder stays out of git.   |
| [`assets/`](assets/README.md)               | Where this project keeps what presents it: four folders to start, a name ready for every other kind, and the rules every file follows. |
| [`benchmarks/`](benchmarks/README.md)       | The benchmark suites and recorded results that defend the performance budgets of this project.                                         |
| [`docs/`](docs/README.md)                   | Where this project keeps its own documents, and where the engineering standards it follows actually live.                              |
| [`packages/`](packages/README.md)           | Workspace packages, one folder each, for when a second consumer needs shared code.                                                     |
| [`src/`](src/README.md)                     | The application source, split into three layers whose dependencies point inward.                                                       |
| [`tests/`](tests/README.md)                 | The test suites, from isolated units to whole user journeys, and how CI comes to run them.                                             |
| [`.editorconfig`](.editorconfig)            | -                                                                                                                                      |
| [`.env.example`](.env.example)              | Environment variable template for this project.                                                                                        |
| [`.gitattributes`](.gitattributes)          | Git attributes - line endings, diffs, and what counts as binary                                                                        |
| [`.gitignore`](.gitignore)                  | &#x1F5C4;&#xFE0F; Universal Ignore Patterns                                                                                            |
| [`.markdownlint.json`](.markdownlint.json)  | Repository-wide markdownlint rules. Discovered by mechanism, which is why this lives at the root.                                      |
| [`AGENTS.md`](AGENTS.md)                    | How AI coding agents work in environment: the universal rules first, then this repository's own.                                       |
| [`LICENSE`](LICENSE)                        | MIT License                                                                                                                            |
| [`README.md`](README.md)                    | This file.                                                                                                                             |

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
