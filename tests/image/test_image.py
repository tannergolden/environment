#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
"""Tests that a built image holds the toolchain its pins promise.

WHY THIS EXISTS. The image is the one thing every repository's development
container and every check is meant to agree on, so each version it holds is
a promise: these keep it. They read every expected version from the pins
themselves, so changing a pin is the whole of changing a test, and they run
the account's own checks inside the image to prove a repository can.

They need Docker, and ENVIRONMENT_IMAGE naming the image to check; `make
test-image` builds one and sets it. Every container runs with no network, so
nothing here depends on what is reachable.

    make test-image
"""

from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
TOOLCHAIN = ROOT / 'toolchain'
IMAGE = os.environ.get('ENVIRONMENT_IMAGE', '')
FIRST_VERSION = re.compile(r'[0-9]+\.[0-9]+\.[0-9]+')


def pins() -> dict[str, str]:
    found: dict[str, str] = {}
    for line in (TOOLCHAIN / 'versions').read_text(encoding='utf-8').splitlines():
        if line and not line.startswith('#'):
            key, _, value = line.partition('=')
            found[key] = value
    for line in (TOOLCHAIN / 'requirements.in').read_text(encoding='utf-8').splitlines():
        if line and not line.startswith('#'):
            name, _, version = line.partition('==')
            found[name.lower()] = version
    found.update(json.loads((TOOLCHAIN / 'package.json').read_text(encoding='utf-8'))['dependencies'])
    return found


def run(*command: str, user: str = 'root', work: bool = False) -> subprocess.CompletedProcess[str]:
    args = ['docker', 'run', '--rm', '--network', 'none', '--user', user]
    if work:
        # The checkout belongs to whoever ran the tests, so git is told to
        # trust it rather than refuse a repository owned by someone else.
        args += ['--volume', f'{ROOT}:/work:ro', '--workdir', '/work',
                 '--env', 'GIT_CONFIG_COUNT=1', '--env', 'GIT_CONFIG_KEY_0=safe.directory',
                 '--env', 'GIT_CONFIG_VALUE_0=*']
    return subprocess.run([*args, IMAGE, *command], capture_output=True, text=True, check=False)


class ImageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not IMAGE:
            raise RuntimeError('set ENVIRONMENT_IMAGE to the image to check, or run make test-image')
        cls.pins = pins()

    def assertVersion(self, command: tuple[str, ...], expected: str, status: int = 0) -> None:
        result = run(*command)
        self.assertEqual(result.returncode, status, result.stderr)
        found = FIRST_VERSION.search(result.stdout + result.stderr)
        self.assertIsNotNone(found, result.stdout)
        self.assertEqual(found.group(0), expected)

    def test_each_check_tool_is_its_pinned_version(self) -> None:
        for command, pin in (
            (('actionlint', '-version'), 'ACTIONLINT_VERSION'),
            (('gitleaks', 'version'), 'GITLEAKS_VERSION'),
            (('lychee', '--version'), 'LYCHEE_VERSION'),
            (('shellcheck', '--version'), 'SHELLCHECK_VERSION'),
            (('typos', '--version'), 'TYPOS_VERSION'),
            (('ruff', '--version'), 'ruff'),
            (('pytest', '--version'), 'pytest'),
            (('zizmor', '--version'), 'zizmor'),
            (('prettier', '--version'), 'prettier'),
        ):
            with self.subTest(command=command[0]):
                self.assertVersion(command, self.pins[pin])
        # markdownlint-cli2 has no version flag: its help names the version,
        # and it exits 2 after printing it.
        self.assertVersion(('markdownlint-cli2', '--help'), self.pins['markdownlint-cli2'], status=2)

    def test_python_is_3_12_and_imports_the_pinned_pyyaml(self) -> None:
        result = run('python3', '-c', 'import sys, yaml; print(sys.version.split()[0], yaml.__version__)')
        self.assertEqual(result.returncode, 0, result.stderr)
        python, pyyaml = result.stdout.split()
        self.assertTrue(python.startswith('3.12.'), python)
        self.assertEqual(pyyaml, self.pins['pyyaml'])

    def test_pip_installs_for_the_user_without_a_flag(self) -> None:
        marker = 'import os, sysconfig; print(os.path.exists(os.path.join(sysconfig.get_path("stdlib"), "EXTERNALLY-MANAGED")))'
        result = run('python3', '-c', marker)
        self.assertEqual(result.stdout.strip(), 'False', 'pip install --user would be refused')
        self.assertEqual(run('python3', '-m', 'pip', '--version').returncode, 0)

    def test_node_is_its_pinned_version(self) -> None:
        result = run('node', '--version')
        self.assertEqual(result.stdout.strip(), 'v' + self.pins['NODE_VERSION'])
        self.assertEqual(run('npm', '--version').returncode, 0)

    def test_git_is_new_enough_for_the_standards(self) -> None:
        result = run('git', '--version')
        major, minor = (int(part) for part in FIRST_VERSION.search(result.stdout).group(0).split('.')[:2])
        self.assertGreaterEqual((major, minor), (2, 40))

    def test_the_development_user_has_uid_1000_and_sudo(self) -> None:
        result = run('sh', '-c', 'id -u && sudo -n true && echo sudo', user='vscode')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.split(), ['1000', 'sudo'])

    def test_a_development_container_works_as_that_user(self) -> None:
        label = subprocess.run(['docker', 'inspect', '--format', '{{ index .Config.Labels "devcontainer.metadata" }}', IMAGE],
                               capture_output=True, text=True, check=True).stdout
        self.assertEqual(json.loads(label), [{'remoteUser': 'vscode'}])

    def test_the_checks_run_here(self) -> None:
        for command in (('python3', '.github/scripts/validate-repository.py'), ('actionlint',)):
            with self.subTest(command=command[0]):
                result = run(*command, user='vscode', work=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
