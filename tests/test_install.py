#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Tests for the installer's refusals.

WHY THIS EXISTS. toolchain/install.sh promises that nothing unchecked is
installed: a download that does not match its pin, or does not arrive, stops
it before it has changed anything. Building the image proves the installer
works; these prove it refuses. Each runs the real script for a throwaway
user, with ENVIRONMENT_MIRROR pointing every archive at a local folder and,
where a test gets as far as pip, pip at an empty one, so nothing is fetched
from the network.

Run them:

    python3 -m unittest discover -s tests -p 'test_*.py'
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
WANTED = re.compile(r'could not download (file://\S+),')
# Each tool, by the word its download URL carries.
TOOLS = ('ACTIONLINT', 'GITLEAKS', 'LYCHEE', 'SHELLCHECK', 'TYPOS', 'NODE')


class Installer:
    """A copy of the toolchain, a mirror with nothing in it, and a home of its own."""

    def __init__(self) -> None:
        self.root = pathlib.Path(tempfile.mkdtemp(prefix='install-test-'))
        shutil.copytree(ROOT / 'toolchain', self.root / 'toolchain')
        self.mirror = self.root / 'mirror'
        self.home = self.root / 'home'
        self.mirror.mkdir()
        self.home.mkdir()

    def run(self, *args: str, cwd: pathlib.Path | None = None,
            **extra: str) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ, HOME=str(self.home), ENVIRONMENT_MIRROR=self.mirror.as_uri(), **extra)
        env.pop('XDG_DATA_HOME', None)
        return subprocess.run(['sh', str(self.root / 'toolchain' / 'install.sh'), *args],
                              cwd=cwd, env=env, capture_output=True, text=True, check=False)

    def serve_every_archive(self, wrong: str = '', *args: str,
                            **extra: str) -> tuple[list[str], subprocess.CompletedProcess[str]]:
        """Serves each archive the installer asks for, pinned to match, but `wrong`'s, and runs it once more."""
        versions = self.root / 'toolchain' / 'versions'
        fetched: list[str] = []
        for _ in range(len(TOOLS) + 1):
            result = self.run(*(args or ('--user',)), **extra)
            wanted = WANTED.search(result.stderr)
            if not wanted:
                break
            stand_in = pathlib.Path(wanted.group(1).removeprefix('file://'))
            tool = next(name for name in TOOLS if name.lower() in str(stand_in.relative_to(self.mirror)))
            stand_in.parent.mkdir(parents=True, exist_ok=True)
            stand_in.write_bytes(f'a stand-in for {tool}\n'.encode())
            fetched.append(tool)
            if tool != wrong:
                digest = hashlib.sha256(stand_in.read_bytes()).hexdigest()
                text = re.sub(rf'(?m)^({tool}_SHA256_(?:AMD64|ARM64))=.*$', rf'\g<1>={digest}',
                              versions.read_text(encoding='utf-8'))
                versions.write_text(text, encoding='utf-8')
        return fetched, result

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

    def test_checks_every_download_before_it_installs_any(self) -> None:
        # Every download arrives, and each matches its pin but the last one,
        # typos', so the refusal comes once the others are fetched and checked.
        fetched, result = self.installer.serve_every_archive(wrong='TYPOS')
        self.assertEqual(fetched[-1:], ['TYPOS'], fetched)
        self.assertLessEqual({'ACTIONLINT', 'GITLEAKS', 'LYCHEE', 'SHELLCHECK'}, set(fetched))
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertRegex(result.stderr, r'crate-ci/typos/\S+ is not the file pinned in versions')
        self.assertIn('so nothing was installed', result.stderr)
        self.assertEqual(self.installer.installed(), [])

    def test_installs_nothing_when_a_wheel_cannot_be_fetched(self) -> None:
        # Every archive matches its pin, and pip's index is an empty folder:
        # the wheels are fetched before anything is installed, so a session's
        # own pytest and ruff are still there when PyPI cannot be reached.
        empty = self.installer.root / 'empty-index'
        empty.mkdir()
        fetched, result = self.installer.serve_every_archive(
            PIP_INDEX_URL=empty.as_uri(), PIP_CONFIG_FILE=os.devnull)
        self.assertLessEqual({'ACTIONLINT', 'GITLEAKS', 'LYCHEE', 'SHELLCHECK', 'TYPOS'}, set(fetched))
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('pip could not download every wheel', result.stderr)
        self.assertIn('so nothing was installed', result.stderr)
        self.assertEqual(self.installer.installed(), [])

    def test_fetches_only_the_parts_it_is_asked_for(self) -> None:
        # The binaries alone: Node.js is never asked for, and the run stops at
        # typos' mismatch, before pip or npm would fetch anything.
        fetched, result = self.installer.serve_every_archive('TYPOS', '--user', '--only', 'binaries')
        self.assertEqual(fetched, ['ACTIONLINT', 'GITLEAKS', 'LYCHEE', 'SHELLCHECK', 'TYPOS'])
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('so nothing was installed', result.stderr)
        self.assertEqual(self.installer.installed(), [])

    def test_the_python_tools_alone_fetch_no_archive(self) -> None:
        empty = self.installer.root / 'empty-index'
        empty.mkdir()
        result = self.installer.run('--user', '--only', 'python', PIP_INDEX_URL=empty.as_uri(),
                                    PIP_CONFIG_FILE=os.devnull)
        self.assertNotRegex(result.stderr, WANTED)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertRegex(result.stderr, r'pip could not download every wheel requirements\.txt pins for Python 3\.\d+')
        self.assertEqual(self.installer.installed(), [])

    def test_runs_the_real_pip_wherever_it_is_started(self) -> None:
        # Python looks in the folder it is started from before anywhere else,
        # so a folder called pip there would run in place of pip and decide
        # what is installed. This one leaves a mark if it ever runs.
        start = self.installer.root / 'start'
        marker = self.installer.root / 'hijacked'
        (start / 'pip').mkdir(parents=True)
        (start / 'pip' / '__init__.py').write_text('', encoding='utf-8')
        (start / 'pip' / '__main__.py').write_text(
            f'import pathlib, sys\npathlib.Path({str(marker)!r}).write_text(" ".join(sys.argv[1:]))\n',
            encoding='utf-8')
        empty = self.installer.root / 'empty-index'
        empty.mkdir()
        result = self.installer.run('--user', '--only', 'python', cwd=start, PIP_INDEX_URL=empty.as_uri(),
                                    PIP_CONFIG_FILE=os.devnull)
        self.assertFalse(marker.exists(), 'a pip folder where the installer was started ran in place of pip')
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn('pip could not download every wheel', result.stderr)
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
        for args in (('--system',), ('--user', '--user'), ('--user', '--only'), ('--user', '--only', 'go'),
                     ('--user', '--only', ''), ('--user', '--only', 'binaries', '--only', 'node')):
            with self.subTest(args=args):
                result = self.installer.run(*args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(self.installer.installed(), [])


if __name__ == '__main__':
    unittest.main()
