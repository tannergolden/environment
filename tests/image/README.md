<!--
title: '🐳 IMAGE TESTS'
description: 'The tests that check a built image: every tool at its pinned version, Python, Node.js and git, the development user, and the repository validator and actionlint running inside it.'
type: index
-->

<div align="center">

# 🐳 IMAGE TESTS

<a name="top"></a>

**What a built image has to hold before anything publishes it.**

_Read from the pins, checked in the container._

</div>

---

## 💡 What This Folder Is For

The tests that need a built image, kept apart from the unit tests beside the
folder so `make test-unit` runs without Docker. `make test-image` builds the
image and runs them against it, with `ENVIRONMENT_IMAGE` naming it:

```bash
make test-image
ENVIRONMENT_IMAGE=environment:local python3 -m unittest discover -s tests/image -p 'test_*.py'
```

They check every check tool's version against
[`toolchain/versions`](../../toolchain/versions), `requirements.in` and
`package.json`, Python 3.12 importing the pinned PyYAML, Node.js, git 2.40 or
newer, the `vscode` user and its sudo, the label that makes a development
container work as that user, and that the repository validator and actionlint
run inside the image. Every container runs with no network. Without
`ENVIRONMENT_IMAGE` they fail, rather than pass having checked nothing.

---

## 📝 File Log

<!-- AUTO-INDEX:BEGIN dir=. style=log -->

| Entry                            | Purpose                                                        |
| :------------------------------- | :------------------------------------------------------------- |
| [`README.md`](README.md)         | This file.                                                     |
| [`test_image.py`](test_image.py) | Tests that a built image holds the toolchain its pins promise. |

<!-- AUTO-INDEX:END -->

🗂️ Machined Indexes redraws this log after every push to the default branch,
from what each file says about itself.

---

<div align="center">

**Built, then checked, then published.**

[↑ Back to Top](#top)

<br />

Built with ❤️ by the Engineering Team. Distributed under the terms in [LICENSE](/LICENSE).

</div>
