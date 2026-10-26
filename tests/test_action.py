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
import os
import pathlib
import re
import subprocess
import tarfile
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
ACTION = ROOT / '.github' / 'actions' / 'toolchain'
WORKFLOWS = ROOT / '.github' / 'workflows'


def job(workflow: str, name: str) -> str:
    """The text of one job in a workflow, from its id to the next job's."""
    text = (WORKFLOWS / workflow).read_text(encoding='utf-8')
    start = text.index(f'\n  {name}:\n')
    following = re.search(r'(?m)^  [a-z0-9-]+:$', text[start + 2:])
    return text[start:start + 2 + following.start()] if following else text[start:]


class ToolchainActionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.action = (ACTION / 'action.yml').read_text(encoding='utf-8')

    def test_it_runs_the_installer_from_its_own_archive_for_the_user(self) -> None:
        self.assertRegex(self.action, r'(?m)^\s+using: composite$')
        installer = re.search(r'(?m)^\s+run: sh "\$GITHUB_ACTION_PATH/([^"]+)" --user --only "\$TOOLS"$', self.action)
        self.assertIsNotNone(installer)
        self.assertEqual((ACTION / installer.group(1)).resolve(), ROOT / 'toolchain' / 'install.sh')

    def test_it_finds_the_installer_inside_a_container_too(self) -> None:
        # In a job with `container:`, github.action_path names the folder on
        # the runner, which the container cannot see; the variable is
        # translated for it.
        self.assertNotRegex(self.action, r'\$\{\{\s*github\.action_path')

    def test_it_installs_everything_unless_told_what(self) -> None:
        self.assertRegex(self.action, r'(?m)^  tools:\n(?:    .*\n)*?    default: all$')
        self.assertRegex(self.action, r'(?m)^\s+TOOLS: \$\{\{ inputs\.tools \}\}$')

    def test_it_puts_the_tools_ahead_of_the_runners(self) -> None:
        self.assertRegex(self.action, r'(?m)^\s+echo "\$HOME/\.local/bin" >> "\$GITHUB_PATH"$')

    def test_a_failure_fails_the_job(self) -> None:
        self.assertNotIn('continue-on-error', self.action)
        self.assertNotRegex(self.action, r'\|\|\s*(true|:|exit 0)')
        self.assertNotRegex(self.action, r'(?m)^\s+if:', 'a step that can be skipped is one a job can pass without')

    def test_the_source_archive_carries_the_action_and_the_installer(self) -> None:
        # GitHub builds the archive it fetches an action from with
        # `git archive`, which leaves out whatever .gitattributes marks
        # export-ignore, a whole folder at a time. This archives the working
        # tree the same way, through an index of its own so the repository's
        # is left alone, and looks for every file the action needs.
        with tempfile.TemporaryDirectory() as scratch:
            env = dict(os.environ, GIT_INDEX_FILE=os.path.join(scratch, 'index'))
            subprocess.run(['git', 'add', '--all'], cwd=ROOT, env=env, capture_output=True, check=True)
            tree = subprocess.run(['git', 'write-tree'], cwd=ROOT, env=env, capture_output=True, text=True,
                                  check=True).stdout.strip()
        archive = subprocess.run(['git', 'archive', '--format=tar', tree], cwd=ROOT, capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            names = set(tar.getnames())
        for path in ('.github/actions/toolchain/action.yml', 'toolchain/install.sh', 'toolchain/versions',
                     'toolchain/requirements.txt', 'toolchain/package.json', 'toolchain/package-lock.json'):
            with self.subTest(path=path):
                self.assertIn(path, names)

    def test_checks_run_it_on_a_runner(self) -> None:
        toolchain = job('checks.yml', 'toolchain')
        self.assertIn('uses: ./.github/actions/toolchain', toolchain)
        self.assertIn('ENVIRONMENT_IMAGE: host', toolchain)

    def test_a_release_runs_it_on_both_architectures_before_it_tags(self) -> None:
        for name, runner in (('verify', 'ubuntu-latest'), ('verify-arm64', 'ubuntu-24.04-arm')):
            with self.subTest(job=name):
                verify = job('cut-release.yml', name)
                self.assertIn(f'runs-on: {runner}', verify)
                self.assertIn('uses: ./.github/actions/toolchain', verify)
                self.assertIn('ENVIRONMENT_IMAGE: host', verify)
        release = job('cut-release.yml', 'release')
        self.assertRegex(release, r'needs: \[verify, verify-arm64\]')
        files = re.search(r'required-files: >-\n((?:\s{8}.*\n)+)', release)
        self.assertIsNotNone(files)
        self.assertIn('.github/actions/toolchain/action.yml', files.group(1).split())


if __name__ == '__main__':
    unittest.main()
