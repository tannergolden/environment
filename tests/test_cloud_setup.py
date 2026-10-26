#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Tests for the Claude Code cloud setup script.

WHY THIS EXISTS. setup/claude-cloud-setup.sh runs before every cloud
session starts, and a session is better started with its own tools than with
a failed setup. So it has to exit 0 whatever happens, run nothing it could
not check against its pin, and leave the script it is pasted into running. Each test
lays a release out in a folder, serves it through ENVIRONMENT_BASE, fills the
pins as `make cloud-setup` would, and runs the script with bash. The release's
installer is a stand-in that records how it was called.

Run them:

    python3 -m unittest discover -s tests -p 'test_*.py'
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SETUP = ROOT / 'setup' / 'claude-cloud-setup.sh'
VERSION = 'v9.9.9'
PINS = {
    'INSTALL_SHA256': 'install.sh',
    'VERSIONS_SHA256': 'versions',
    'REQUIREMENTS_SHA256': 'requirements.txt',
    'PACKAGE_SHA256': 'package.json',
    'LOCK_SHA256': 'package-lock.json',
}
STAND_IN = '#!/bin/sh\nprintf "%s" "$*" > "$MARKER"\n'


class Release:
    """A release laid out the way raw.githubusercontent.com serves one."""

    def __init__(self) -> None:
        self.root = pathlib.Path(tempfile.mkdtemp(prefix='cloud-setup-test-'))
        self.toolchain = self.root / 'base' / VERSION / 'toolchain'
        self.toolchain.mkdir(parents=True)
        self.marker = self.root / 'installer-ran'
        for name in PINS.values():
            self.write(name, STAND_IN if name == 'install.sh' else f'{name} as released\n')

    def write(self, name: str, text: str) -> None:
        (self.toolchain / name).write_text(text, encoding='utf-8')

    def pinned(self) -> str:
        """The setup script with its pins filled, as `make cloud-setup` prints it."""
        script = SETUP.read_text(encoding='utf-8').replace('@VERSION@', VERSION)
        for placeholder, name in PINS.items():
            digest = hashlib.sha256((self.toolchain / name).read_bytes()).hexdigest()
            script = script.replace(f'@{placeholder}@', digest)
        return script

    def run(self, script: str) -> subprocess.CompletedProcess[str]:
        path = self.root / 'setup.sh'
        path.write_text(script, encoding='utf-8')
        env = dict(os.environ, ENVIRONMENT_BASE=(self.root / 'base').as_uri(), MARKER=str(self.marker))
        return subprocess.run(['bash', str(path)], env=env, capture_output=True, text=True, check=False)

    def cleanup(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


class CloudSetupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.release = Release()
        self.addCleanup(self.release.cleanup)

    def test_runs_the_installer_for_the_user_when_every_pin_matches(self) -> None:
        result = self.release.run(self.release.pinned())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.release.marker.read_text(encoding='utf-8'), '--user')

    def test_runs_nothing_when_a_file_does_not_match_its_pin(self) -> None:
        script = self.release.pinned()
        self.release.write('versions', 'versions, changed after it was pinned\n')
        result = self.release.run(script)
        self.assertEqual(result.returncode, 0)
        self.assertIn('toolchain/versions for v9.9.9 does not match its pin, so nothing was installed', result.stderr)
        self.assertFalse(self.release.marker.exists())

    def test_runs_nothing_when_a_file_is_missing(self) -> None:
        script = self.release.pinned()
        (self.release.toolchain / 'package.json').unlink()
        result = self.release.run(script)
        self.assertEqual(result.returncode, 0)
        self.assertIn('could not download toolchain/package.json for v9.9.9', result.stderr)
        self.assertFalse(self.release.marker.exists())

    def test_the_copy_in_the_repository_installs_nothing(self) -> None:
        result = self.release.run(SETUP.read_text(encoding='utf-8'))
        self.assertEqual(result.returncode, 0)
        self.assertIn('no release is pinned here yet', result.stderr)
        self.assertFalse(self.release.marker.exists())

    def test_a_failing_installer_still_lets_the_session_start(self) -> None:
        self.release.write('install.sh', '#!/bin/sh\nexit 1\n')
        result = self.release.run(self.release.pinned())
        self.assertEqual(result.returncode, 0)
        self.assertIn('the installer reported a problem', result.stderr)

    def test_the_script_it_is_pasted_into_keeps_running(self) -> None:
        for script in (self.release.pinned(), SETUP.read_text(encoding='utf-8')):
            with self.subTest(pinned='@VERSION@' not in script):
                result = self.release.run(script + 'echo the next setup script ran\n')
                self.assertEqual(result.returncode, 0)
                self.assertIn('the next setup script ran', result.stdout)


if __name__ == '__main__':
    unittest.main()
