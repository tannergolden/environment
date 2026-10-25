#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Tests for the installer's refusals.

WHY THIS EXISTS. toolchain/install.sh promises that nothing unchecked is
installed: a download that does not match its pin, or does not arrive, stops
it before it has changed anything. Building the image proves the installer
works; these prove it refuses. Each runs the real script for a throwaway
user, with ENVIRONMENT_MIRROR pointing every download at a local folder, so
nothing is fetched from the network.

Run them:

    python3 -m unittest discover -s tests -p 'test_*.py'
"""

from __future__ import annotations

import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WANTED = re.compile(r'could not download (file://\S+),')


class Installer:
    """A copy of the toolchain, a mirror with nothing in it, and a home of its own."""

    def __init__(self) -> None:
        self.root = pathlib.Path(tempfile.mkdtemp(prefix='install-test-'))
        shutil.copytree(ROOT / 'toolchain', self.root / 'toolchain')
        self.mirror = self.root / 'mirror'
        self.home = self.root / 'home'
        self.mirror.mkdir()
        self.home.mkdir()

    def run(self, *args: str) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ, HOME=str(self.home), ENVIRONMENT_MIRROR=self.mirror.as_uri())
        env.pop('XDG_DATA_HOME', None)
        return subprocess.run(['sh', str(self.root / 'toolchain' / 'install.sh'), *args],
                              env=env, capture_output=True, text=True, check=False)

    def installed(self) -> list[str]:
        local = self.home / '.local'
        return sorted(str(p.relative_to(local)) for p in local.rglob('*')) if local.exists() else []

    def cleanup(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.installer = Installer()
        self.addCleanup(self.installer.cleanup)

    def test_stops_when_a_download_does_not_arrive(self) -> None:
        result = self.installer.run('--user')
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertRegex(result.stderr, WANTED)
        self.assertIn('so nothing was installed', result.stderr)
        self.assertEqual(self.installer.installed(), [])

    def test_refuses_a_download_that_does_not_match_its_pin(self) -> None:
        first = self.installer.run('--user')
        wanted = WANTED.search(first.stderr)
        self.assertIsNotNone(wanted, first.stderr)
        stand_in = pathlib.Path(wanted.group(1).removeprefix('file://'))
        stand_in.parent.mkdir(parents=True, exist_ok=True)
        stand_in.write_bytes(b'not the archive that was pinned\n')

        result = self.installer.run('--user')
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('is not the file pinned in versions', result.stderr)
        self.assertIn('so nothing was installed', result.stderr)
        self.assertEqual(self.installer.installed(), [])

    def test_refuses_a_tool_with_no_pin(self) -> None:
        versions = self.installer.root / 'toolchain' / 'versions'
        kept = [line for line in versions.read_text(encoding='utf-8').splitlines()
                if not line.startswith('NODE_VERSION=')]
        versions.write_text('\n'.join(kept) + '\n', encoding='utf-8')
        result = self.installer.run('--user')
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('NODE_VERSION is not pinned', result.stderr)
        self.assertEqual(self.installer.installed(), [])

    def test_rejects_an_option_it_does_not_know(self) -> None:
        for args in (('--system',), ('--user', '--user')):
            with self.subTest(args=args):
                result = self.installer.run(*args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(self.installer.installed(), [])


if __name__ == '__main__':
    unittest.main()
