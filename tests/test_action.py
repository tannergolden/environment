#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Tests that the toolchain action installs this release's pins, or fails.

WHY THIS EXISTS. Other repositories' checks call
.github/actions/toolchain at a tag, and GitHub runs it from this
repository's source archive at that tag. It is only worth calling while it
runs this repository's own installer from that archive, puts what it
installed ahead of the runner's tools, and fails the job when the installer
fails. These hold it to that without a runner; 🚦 Checks' toolchain job runs
it on one.

Run them:

    python3 -m unittest discover -s tests -p 'test_*.py'
"""

from __future__ import annotations

import io
import pathlib
import re
import subprocess
import tarfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ACTION = ROOT / '.github' / 'actions' / 'toolchain'


class ToolchainActionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.action = (ACTION / 'action.yml').read_text(encoding='utf-8')

    def test_it_runs_the_installer_from_its_own_archive_for_the_user(self) -> None:
        self.assertRegex(self.action, r'(?m)^\s+using: composite$')
        installer = re.search(r'(?m)^\s+INSTALLER: \$\{\{ github\.action_path \}\}/(\S+)$', self.action)
        self.assertIsNotNone(installer)
        self.assertEqual((ACTION / installer.group(1)).resolve(), ROOT / 'toolchain' / 'install.sh')
        self.assertRegex(self.action, r'(?m)^\s+run: sh "\$INSTALLER" --user$')

    def test_it_puts_the_tools_ahead_of_the_runners(self) -> None:
        self.assertRegex(self.action, r'(?m)^\s+echo "\$HOME/\.local/bin" >> "\$GITHUB_PATH"$')

    def test_a_failure_fails_the_job(self) -> None:
        self.assertNotIn('continue-on-error', self.action)
        self.assertNotRegex(self.action, r'\|\|\s*(true|:|exit 0)')

    def test_the_source_archive_carries_the_action_and_the_installer(self) -> None:
        # GitHub builds the archive it fetches an action from with
        # `git archive`, which leaves out whatever .gitattributes marks
        # export-ignore, a whole folder at a time. This archives what is
        # staged the same way, and looks for every file the action needs.
        tree = subprocess.run(['git', 'write-tree'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
        archive = subprocess.run(['git', 'archive', '--format=tar', tree], cwd=ROOT, capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            names = set(tar.getnames())
        for path in ('.github/actions/toolchain/action.yml', 'toolchain/install.sh', 'toolchain/versions',
                     'toolchain/requirements.txt', 'toolchain/package.json', 'toolchain/package-lock.json'):
            with self.subTest(path=path):
                self.assertIn(path, names)

    def test_checks_run_it_on_a_runner(self) -> None:
        checks = (ROOT / '.github' / 'workflows' / 'checks.yml').read_text(encoding='utf-8')
        job = checks[checks.index('\n  toolchain:\n'):]
        self.assertIn('uses: ./.github/actions/toolchain', job)
        self.assertIn('ENVIRONMENT_IMAGE: host', job)


if __name__ == '__main__':
    unittest.main()
