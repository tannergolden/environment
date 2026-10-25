#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Tests that the toolchain's pins are complete and agree with each other.

WHY THIS EXISTS. Four files pin the toolchain: `versions`, the two locks
compiled from `requirements.in` and `package.json`, and the Dockerfile's
base. A pin that is missing, malformed or out of step with its source fails
only when an image is built, on one architecture, perhaps in the middle of a
release. These fail it on the pull request instead, without building
anything.

Run them:

    python3 -m unittest discover -s tests -p 'test_*.py'
"""

from __future__ import annotations

import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOLCHAIN = ROOT / 'toolchain'
TOOLS = ('NODE', 'ACTIONLINT', 'GITLEAKS', 'LYCHEE', 'SHELLCHECK', 'TYPOS')
VERSION = re.compile(r'^[0-9]+\.[0-9]+\.[0-9]+$')
SHA256 = re.compile(r'^[0-9a-f]{64}$')


def read_versions() -> dict[str, str]:
    pins: dict[str, str] = {}
    for line in (TOOLCHAIN / 'versions').read_text(encoding='utf-8').splitlines():
        if line and not line.startswith('#'):
            key, _, value = line.partition('=')
            pins[key] = value
    return pins


def normalise(name: str) -> str:
    return re.sub(r'[-_.]+', '-', name).lower()


class VersionsTests(unittest.TestCase):
    def test_every_tool_has_a_version_and_a_sum_per_architecture(self) -> None:
        pins = read_versions()
        for tool in TOOLS:
            with self.subTest(tool=tool):
                self.assertRegex(pins.get(f'{tool}_VERSION', ''), VERSION)
                amd64, arm64 = pins.get(f'{tool}_SHA256_AMD64', ''), pins.get(f'{tool}_SHA256_ARM64', '')
                self.assertRegex(amd64, SHA256)
                self.assertRegex(arm64, SHA256)
                self.assertNotEqual(amd64, arm64, 'one archive cannot serve both architectures')

    def test_nothing_else_is_pinned(self) -> None:
        expected = {f'{tool}_{field}' for tool in TOOLS for field in ('VERSION', 'SHA256_AMD64', 'SHA256_ARM64')}
        self.assertEqual(set(read_versions()), expected)

    def test_the_installer_downloads_every_tool(self) -> None:
        installer = (TOOLCHAIN / 'install.sh').read_text(encoding='utf-8')
        for tool in TOOLS:
            with self.subTest(tool=tool):
                self.assertRegex(installer, rf'(?m)^\s*(?:\|\|\s+)?fetch {tool.lower()} "https://')


class PythonPinsTests(unittest.TestCase):
    def setUp(self) -> None:
        source = (TOOLCHAIN / 'requirements.in').read_text(encoding='utf-8')
        self.pins = dict(line.split('==') for line in source.splitlines() if line and not line.startswith('#'))
        self.lock = (TOOLCHAIN / 'requirements.txt').read_text(encoding='utf-8')

    def test_each_tool_is_pinned_exactly(self) -> None:
        self.assertTrue(self.pins)
        for name, version in self.pins.items():
            with self.subTest(name=name):
                self.assertRegex(version, VERSION)

    def test_the_lock_holds_each_pin(self) -> None:
        locked = {normalise(n): v for n, v in re.findall(r'(?m)^([A-Za-z0-9_.-]+)==(\S+)', self.lock)}
        for name, version in self.pins.items():
            with self.subTest(name=name):
                self.assertEqual(locked.get(normalise(name)), version)

    def test_every_locked_package_is_hashed(self) -> None:
        for block in re.split(r'(?m)^(?=[A-Za-z0-9])', self.lock):
            if '==' in block:
                with self.subTest(package=block.split('==')[0]):
                    self.assertIn('--hash=sha256:', block)


class NodePinsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.package = json.loads((TOOLCHAIN / 'package.json').read_text(encoding='utf-8'))
        self.lock = json.loads((TOOLCHAIN / 'package-lock.json').read_text(encoding='utf-8'))

    def test_each_tool_is_pinned_exactly(self) -> None:
        self.assertTrue(self.package['dependencies'])
        for name, version in self.package['dependencies'].items():
            with self.subTest(name=name):
                self.assertRegex(version, VERSION)

    def test_the_lock_agrees_with_the_pins(self) -> None:
        packages = self.lock['packages']
        self.assertEqual(packages['']['dependencies'], self.package['dependencies'])
        for name, version in self.package['dependencies'].items():
            with self.subTest(name=name):
                self.assertEqual(packages[f'node_modules/{name}']['version'], version)

    def test_every_locked_package_is_checked_and_runs_no_install_script(self) -> None:
        for path, entry in self.lock['packages'].items():
            if path:
                with self.subTest(package=path):
                    self.assertTrue(entry.get('integrity', '').startswith('sha512-'))
                    self.assertFalse(entry.get('hasInstallScript', False))


class DockerfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.dockerfile = (ROOT / 'Dockerfile').read_text(encoding='utf-8')

    def test_the_base_is_pinned_by_digest(self) -> None:
        bases = re.findall(r'(?m)^FROM\s+(\S+)', self.dockerfile)
        self.assertEqual(len(bases), 1)
        self.assertRegex(bases[0], r'^ubuntu:24\.04@sha256:[0-9a-f]{64}$')

    def test_the_development_container_works_as_the_user_the_image_makes(self) -> None:
        label = re.search(r'devcontainer\.metadata="((?:[^"\\]|\\.)*)"', self.dockerfile)
        self.assertIsNotNone(label)
        metadata = json.loads(label.group(1).replace('\\"', '"'))
        self.assertEqual(metadata, [{'remoteUser': 'vscode'}])
        self.assertRegex(self.dockerfile, r'useradd [^\n]*--uid 1000 [^\n]* vscode\b')

    def test_the_build_runs_the_installer(self) -> None:
        self.assertIn('sh /tmp/toolchain/install.sh', self.dockerfile)
        self.assertNotRegex(self.dockerfile, r'(?m)^(?:COPY|ADD)\b', 'the toolchain is mounted, not copied in')


if __name__ == '__main__':
    unittest.main()
