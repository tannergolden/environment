#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Tests for the cloud setup printer.

WHY THIS EXISTS. The script `print-cloud-setup.py` prints is pasted into
every Claude Code cloud environment, and a session installs only what its
pins name. A pin taken from the wrong file, or from the working tree rather
than the tag, would make every session refuse the release, or install one
nobody tagged.

Every test builds a throwaway repository with a tagged release, runs the real
script as a subprocess, and asserts on what it prints. One then runs what it
printed against the release, as a session would, so the printer and the setup
script are held to the same pairing of pin and file.

Run it:

    python3 .github/scripts/test_print_cloud_setup.py
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
SCRIPT = HERE / 'print-cloud-setup.py'
SETUP = HERE.parents[1] / 'setup' / 'claude-cloud-setup.sh'
FILES = ('install.sh', 'versions', 'requirements.txt', 'package.json', 'package-lock.json')
STAND_IN = '#!/bin/sh\nprintf "%s" "$*" > "$MARKER"\n'


class Release:
    """A throwaway repository holding the printer, the setup script and a toolchain."""

    def __init__(self) -> None:
        self.root = pathlib.Path(tempfile.mkdtemp(prefix='cloud-setup-test-'))
        self.git('init', '-q', '.')
        self.git('config', 'user.name', 'Test')
        self.git('config', 'user.email', 'test@example.invalid')
        self.git('config', 'commit.gpgsign', 'false')
        self.git('config', 'tag.gpgsign', 'false')
        self.write('.github/scripts/print-cloud-setup.py', SCRIPT.read_text(encoding='utf-8'))
        self.write('setup/claude-cloud-setup.sh', SETUP.read_text(encoding='utf-8'))
        for name in FILES:
            self.write(f'toolchain/{name}', f'{name} as released\n')

    def git(self, *args: str) -> None:
        subprocess.run(['git', *args], cwd=self.root, check=True, capture_output=True)

    def write(self, rel: str, text: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')

    def tag(self, version: str) -> None:
        self.git('add', '-A')
        self.git('commit', '-q', '-m', 'release')
        self.git('tag', version)

    def run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, '.github/scripts/print-cloud-setup.py', *args],
                              cwd=self.root, capture_output=True, text=True, check=False)

    def serve(self, version: str) -> pathlib.Path:
        """The tag's toolchain, laid out as raw.githubusercontent.com serves it."""
        base = self.root / 'served'
        folder = base / version / 'toolchain'
        folder.mkdir(parents=True)
        for name in FILES:
            shown = subprocess.run(['git', 'show', f'refs/tags/{version}:toolchain/{name}'], cwd=self.root,
                                   check=True, capture_output=True)
            (folder / name).write_bytes(shown.stdout)
        return base

    def cleanup(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


class PrintCloudSetupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.release = Release()
        self.addCleanup(self.release.cleanup)

    def test_pins_every_file_to_the_tag(self) -> None:
        self.release.tag('v1.2.3')
        result = self.release.run('v1.2.3')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("VERSION='v1.2.3'", result.stdout)
        for name in FILES:
            self.assertIn(sha256(f'{name} as released\n'), result.stdout, name)
        self.assertNotRegex(result.stdout, r'@[A-Z0-9_]+@')

    def test_the_printed_script_installs_the_release_it_names(self) -> None:
        self.release.write('toolchain/install.sh', STAND_IN)
        self.release.tag('v1.2.3')
        printed = self.release.run('v1.2.3')
        self.assertEqual(printed.returncode, 0, printed.stderr)
        pasted = self.release.root / 'pasted.sh'
        pasted.write_text(printed.stdout, encoding='utf-8')
        marker = self.release.root / 'installer-ran'
        env = dict(os.environ, ENVIRONMENT_BASE=self.release.serve('v1.2.3').as_uri(), MARKER=str(marker))
        result = subprocess.run(['bash', str(pasted)], env=env, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(marker.exists(), result.stderr)
        self.assertEqual(marker.read_text(encoding='utf-8'), '--user')

    def test_refuses_a_setup_script_with_a_pin_it_cannot_fill(self) -> None:
        setup = SETUP.read_text(encoding='utf-8') + "EXTRA='@EXTRA_SHA256@'\n"
        self.release.write('setup/claude-cloud-setup.sh', setup)
        self.release.tag('v1.2.3')
        result = self.release.run('v1.2.3')
        self.assertEqual(result.returncode, 1)
        self.assertIn('@EXTRA_SHA256@', result.stderr)
        self.assertEqual(result.stdout, '')

    def test_reads_the_tag_not_the_working_tree(self) -> None:
        self.release.tag('v1.2.3')
        self.release.write('toolchain/install.sh', 'edited after the release\n')
        result = self.release.run('v1.2.3')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(sha256('install.sh as released\n'), result.stdout)
        self.assertNotIn(sha256('edited after the release\n'), result.stdout)

    def test_refuses_a_tag_that_is_not_here(self) -> None:
        self.release.tag('v1.2.3')
        result = self.release.run('v9.9.9')
        self.assertEqual(result.returncode, 1)
        self.assertIn('there is no tag v9.9.9', result.stderr)
        self.assertEqual(result.stdout, '')

    def test_refuses_a_release_missing_a_file(self) -> None:
        (self.release.root / 'toolchain' / 'package-lock.json').unlink()
        self.release.tag('v1.2.3')
        result = self.release.run('v1.2.3')
        self.assertEqual(result.returncode, 1)
        self.assertIn('toolchain/package-lock.json is not in v1.2.3', result.stderr)
        self.assertEqual(result.stdout, '')

    def test_refuses_anything_but_a_version(self) -> None:
        for args in ((), ('1.2.3',), ('v1.2',), ('v1.2.3', 'v1.2.4')):
            with self.subTest(args=args):
                result = self.release.run(*args)
                self.assertEqual(result.returncode, 2)
                self.assertIn('usage:', result.stderr)


if __name__ == '__main__':
    unittest.main()
