#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Print the Claude Code cloud setup script, pinned to one release.

WHY THIS EXISTS. setup/claude-cloud-setup.sh keeps placeholders where a
release's version and the SHA-256 of each file it downloads belong, so the
copy in the repository can never install something nobody pinned. This fills
them in from the release's tag, from the very files a session downloads, and
prints the script ready to paste into the cloud environment's settings.

    python3 .github/scripts/print-cloud-setup.py v1.0.0

`make cloud-setup VERSION=v1.0.0` runs the same. The tag has to be here, so
fetch it first (`git fetch --tags`). Nothing is written.
"""

from __future__ import annotations

import hashlib
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = 'setup/claude-cloud-setup.sh'

# Each placeholder, and the file at the tag whose SHA-256 fills it.
PINS = {
    'INSTALL_SHA256': 'toolchain/install.sh',
    'VERSIONS_SHA256': 'toolchain/versions',
    'REQUIREMENTS_SHA256': 'toolchain/requirements.txt',
    'PACKAGE_SHA256': 'toolchain/package.json',
    'LOCK_SHA256': 'toolchain/package-lock.json',
}

VERSION = re.compile(r'^v[0-9]+\.[0-9]+\.[0-9]+$')
PLACEHOLDER = re.compile(r'@[A-Z0-9_]+@')


class Missing(Exception):
    """A file the setup script needs is not in the release."""


def at_tag(version: str, path: str) -> bytes:
    """The file as the tag holds it, which is what a session downloads."""
    result = subprocess.run(['git', 'show', f'refs/tags/{version}:{path}'], cwd=ROOT,
                            capture_output=True, check=False)
    if result.returncode != 0:
        raise Missing(f'{path} is not in {version}')
    return result.stdout


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not VERSION.match(argv[1]):
        print('usage: print-cloud-setup.py vX.Y.Z, or make cloud-setup VERSION=vX.Y.Z', file=sys.stderr)
        return 2
    version = argv[1]
    known = subprocess.run(['git', 'rev-parse', '-q', '--verify', f'refs/tags/{version}'], cwd=ROOT,
                           capture_output=True, check=False)
    if known.returncode != 0:
        print(f'print-cloud-setup: there is no tag {version} here; fetch it with git fetch --tags, '
              'or cut the release first', file=sys.stderr)
        return 1
    try:
        script = at_tag(version, SCRIPT).decode('utf-8').replace('@VERSION@', version)
        for placeholder, path in PINS.items():
            script = script.replace(f'@{placeholder}@', hashlib.sha256(at_tag(version, path)).hexdigest())
    except Missing as exc:
        print(f'print-cloud-setup: {exc}, so the setup script could not be pinned to it', file=sys.stderr)
        return 1
    left = sorted(set(PLACEHOLDER.findall(script)))
    if left:
        print(f'print-cloud-setup: {SCRIPT} in {version} has placeholders this does not fill: '
              f'{", ".join(left)}', file=sys.stderr)
        return 1
    sys.stdout.write(script)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
