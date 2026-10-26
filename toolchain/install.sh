#!/bin/sh
# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
#
# Installs the toolchain: every tool the standards' checks run, at the
# versions pinned in the files beside this one.
#
# WHY ONE SCRIPT FOR TWO MACHINES. The image runs it once, as it is built,
# and a Claude Code cloud session runs the same file from a release, through
# setup/claude-cloud-setup.sh. One set of steps and one set of pins, so a tool
# cannot be one version in the container and another in the session.
#
# NOTHING UNCHECKED IS INSTALLED, AND A FAILED DOWNLOAD CHANGES NOTHING.
# Everything is fetched into a scratch folder and checked there first: each
# archive against its SHA-256 in `versions`, each wheel against its hash in
# requirements.txt, and each npm package against its integrity hash in
# package-lock.json. pip resolves nothing of its own and builds nothing from
# source, and npm ci runs no install scripts. Only then is anything
# installed, so a mismatch, or a host that cannot be reached, stops the
# install before it has changed anything. What can still fail after that is
# local, such as a full disk: the installer says so, puts back any command
# it had moved aside, and a second run finishes the job.
#
#     sh install.sh           system-wide, as root: what the image runs
#     sh install.sh --user    for this user, under ~/.local: what a cloud
#                             session runs
#
# System-wide, Node.js goes into /usr/local, the tools' own files into
# /opt/environment, and every command into /usr/local/bin. For a user, the
# files go into ~/.local/share/environment and the commands into
# ~/.local/bin, which a cloud session puts ahead of its own copies; a machine
# that already has Node.js of the pinned major or newer keeps its own.
#
# It needs curl, tar, xz, sha256sum or shasum, and Python 3.12 or newer with
# pip, able to install for the user when it runs with --user.
#
# ENVIRONMENT_MIRROR serves every archive from elsewhere: each
# https://host/path is fetched from $ENVIRONMENT_MIRROR/host/path instead. A
# network that cannot reach the public hosts points it at a mirror, and the
# tests at a folder of stand-ins; pip and npm keep their own index settings.
# The pins still decide what is installed.

set -eu

here=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)

say() {
  printf 'install.sh: %s\n' "$*" >&2
}

fail() {
  say "$*"
  exit 1
}

mode=system
case ${1:-} in
  '') ;;
  --user) mode=user ;;
  *)
    say "unknown option '$1': pass --user, or nothing to install system-wide"
    exit 2
    ;;
esac
[ $# -le 1 ] || { say 'pass one option at most'; exit 2; }

if [ "$mode" = system ]; then
  data=/opt/environment
  bin=/usr/local/bin
  node_root=/usr/local
  pip_scope=''
else
  # A relative XDG_DATA_HOME is to be ignored, as the XDG specification says.
  case ${XDG_DATA_HOME:-} in
    /*) data=$XDG_DATA_HOME/environment ;;
    *) data=$HOME/.local/share/environment ;;
  esac
  bin=$HOME/.local/bin
  node_root=$data/node
  pip_scope=--user
fi

# A value from `versions`, read as data: the file is never run as shell.
pin() {
  value=$(sed -n "s/^$1=//p" "$here/versions" | head -n 1)
  [ -n "$value" ] || fail "$1 is not pinned in $here/versions"
  printf '%s\n' "$value"
}

sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | cut -d ' ' -f 1
  else
    shasum -a 256 "$1" | cut -d ' ' -f 1
  fi
}

for tool in curl tar xz python3; do
  command -v "$tool" >/dev/null 2>&1 || fail "$tool is not installed, so nothing was"
done
python3 -m pip --version >/dev/null 2>&1 || fail 'pip is not installed for python3, so nothing was'

[ "$(uname -s)" = Linux ] || fail "the toolchain is built for Linux, not $(uname -s)"
case $(uname -m) in
  x86_64 | amd64) arch=AMD64 node_arch=x64 gnu_arch=x86_64 go_arch=amd64 leaks_arch=x64 ;;
  aarch64 | arm64) arch=ARM64 node_arch=arm64 gnu_arch=aarch64 go_arch=arm64 leaks_arch=arm64 ;;
  *) fail "$(uname -m) is not an architecture the toolchain is built for: amd64 or arm64" ;;
esac

work=$(mktemp -d)
stage=checking
# Clears the scratch folder however the installer ends, and says how far a
# stopped or failed run got.
finish() {
  status=$?
  rm -rf "$work"
  [ "$status" -ne 0 ] || return 0
  if [ "$stage" = installing ]; then
    say "stopped partway through installing into $bin, so some tools there may be new and some as they were; run it again to finish"
  elif [ "$status" -ge 128 ]; then
    say 'stopped before it installed anything, so nothing was'
  fi
}
trap finish EXIT
trap 'exit 143' TERM
trap 'exit 130' INT

fetch() {
  name=$1 url=$2
  sum=$(pin "$(printf '%s' "$name" | tr '[:lower:]' '[:upper:]')_SHA256_$arch")
  case $url in
    https://*) [ -z "${ENVIRONMENT_MIRROR:-}" ] || url="${ENVIRONMENT_MIRROR%/}/${url#https://}" ;;
  esac
  curl -fsSL --retry 3 --connect-timeout 20 --max-time 300 -o "$work/$name.archive" "$url" \
    || fail "could not download $url, so nothing was installed"
  actual=$(sha256 "$work/$name.archive")
  [ "$actual" = "$sum" ] \
    || fail "$url is not the file pinned in versions (SHA-256 $actual, pinned $sum), so nothing was installed"
}

# --- Download and check everything first ------------------------------------

# A machine's own Node.js is kept only at the pinned major or newer, since
# markdownlint-cli2 needs Node.js 22, and never the one a previous run
# linked into $bin, which is the toolchain's own.
node_version=$(pin NODE_VERSION)
machine_node=$(command -v node 2>/dev/null || true)
keep_node=no
if [ "$mode" = user ] && [ -n "$machine_node" ] && [ "$machine_node" != "$bin/node" ] \
  && [ "$(node -p 'process.versions.node.split(".")[0]' 2>/dev/null || echo 0)" -ge "${node_version%%.*}" ]; then
  keep_node=yes
fi

v=$node_version
[ "$keep_node" = yes ] \
  || fetch node "https://nodejs.org/dist/v$v/node-v$v-linux-$node_arch.tar.xz"
v=$(pin ACTIONLINT_VERSION)
fetch actionlint "https://github.com/rhysd/actionlint/releases/download/v$v/actionlint_${v}_linux_$go_arch.tar.gz"
v=$(pin GITLEAKS_VERSION)
fetch gitleaks "https://github.com/gitleaks/gitleaks/releases/download/v$v/gitleaks_${v}_linux_$leaks_arch.tar.gz"
v=$(pin LYCHEE_VERSION)
fetch lychee "https://github.com/lycheeverse/lychee/releases/download/lychee-v$v/lychee-$gnu_arch-unknown-linux-musl.tar.gz"
v=$(pin SHELLCHECK_VERSION)
fetch shellcheck "https://github.com/koalaman/shellcheck/releases/download/v$v/shellcheck-v$v.linux.$gnu_arch.tar.xz"
v=$(pin TYPOS_VERSION)
fetch typos "https://github.com/crate-ci/typos/releases/download/v$v/typos-v$v-$gnu_arch-unknown-linux-musl.tar.gz"

# The wheels, each checked against its hash as it arrives.
python3 -m pip download --quiet --no-cache-dir --disable-pip-version-check \
  --require-hashes --no-deps --only-binary=:all: --dest "$work/wheels" --requirement "$here/requirements.txt" \
  || fail 'pip could not download every wheel requirements.txt pins, each matching its hash, so nothing was installed'

# The npm packages, each checked against its integrity hash, installed into
# the scratch folder by the Node.js that will run them. npm starts through
# `env node`, so the Node.js just checked comes first.
if [ "$keep_node" = yes ]; then
  npm=npm
else
  mkdir "$work/node"
  tar -xJf "$work/node.archive" -C "$work/node" --strip-components=1 --no-same-owner
  PATH="$work/node/bin:$PATH"
  export PATH
  npm="$work/node/bin/npm"
fi
mkdir "$work/npm"
cp "$here/package.json" "$here/package-lock.json" "$work/npm/"
# The download cache and npm's own temporary files go with the scratch
# folder, rather than staying in the image or in the user's home.
(cd "$work/npm" && TMPDIR="$work" "$npm" ci --omit=dev --ignore-scripts --no-audit --no-fund --no-update-notifier \
  --loglevel=error --cache "$work/npm-cache") \
  || fail 'npm could not install every package package-lock.json pins, each matching its hash, so nothing was installed'

# Last, whether this Python can take them. The lock is compiled for Python
# 3.12 and newer: on an older one, pytest would install without the backports
# it needs there.
python3 -c 'import sys; sys.exit(sys.version_info < (3, 12))' \
  || fail "python3 is $(python3 -c 'import platform; print(platform.python_version())'), and the toolchain needs 3.12 or newer, so nothing was installed"
if [ "$mode" = user ]; then
  python3 -c 'import site, sys; sys.exit(not site.ENABLE_USER_SITE)' \
    || fail 'python3 cannot install for this user, as inside a virtual environment, so nothing was installed'
fi

# --- Install -----------------------------------------------------------------

say "every download matched its pin; installing into $bin"
stage=installing
mkdir -p "$data/licenses" "$bin"

# A command is replaced, never written through: a link left by another
# installer, such as `uv tool` or pipx, points into that installer's own
# files, and copying over it would rewrite them.
replace() {
  rm -f "$bin/$1"
}

if [ "$keep_node" = yes ]; then
  say "keeping this machine's Node.js $(node --version)"
else
  # For a user, the folder is the toolchain's own: a previous version goes
  # first, so two never mix.
  [ "$mode" = system ] || rm -rf "$node_root"
  mkdir -p "$node_root"
  tar -xJf "$work/node.archive" -C "$node_root" --strip-components=1 --no-same-owner
  if [ "$mode" = user ]; then
    for command in node npm npx; do
      replace "$command"
      ln -s "$node_root/bin/$command" "$bin/$command"
    done
  fi
fi

for name in actionlint gitleaks lychee shellcheck typos; do
  mkdir "$work/$name"
  tar -xf "$work/$name.archive" -C "$work/$name" --no-same-owner
  # The executable of that name: an archive can carry a completion file
  # called the same.
  found=$(find "$work/$name" -type f -name "$name" -perm -100 | head -n 1)
  [ -n "$found" ] || fail "the $name archive holds no $name"
  replace "$name"
  cp "$found" "$bin/$name"
  chmod 0755 "$bin/$name"
  mkdir -p "$data/licenses/$name"
  find "$work/$name" -type f \( -iname 'LICEN[CS]E*' -o -iname 'COPYING*' \) -exec cp {} "$data/licenses/$name/" \;
done

# Ubuntu marks its Python as managed by apt (PEP 668). --break-system-packages
# lets pip install beside it, which is the point here: these pins are what
# `python3` imports and runs, so `python3 -m pytest` and the repository
# validator's `import yaml` get exactly them. The wheels come from the scratch
# folder, already checked, so nothing is fetched now, and --force-reinstall
# writes every command again, even for a package already in place. Both
# places this runs, an image build and a cloud session, run it as root on
# purpose, so pip is told not to warn about that. A link another installer
# left is moved aside first, and put back if pip fails.
for command in pytest py.test pygmentize ruff zizmor; do
  [ ! -L "$bin/$command" ] || mv "$bin/$command" "$work/moved-$command"
done
# shellcheck disable=SC2086 # deliberately unquoted: empty system-wide, --user for a user
if ! PIP_ROOT_USER_ACTION=ignore python3 -m pip install $pip_scope --break-system-packages --quiet --no-cache-dir \
  --disable-pip-version-check --no-warn-script-location --no-index --find-links "$work/wheels" \
  --force-reinstall --require-hashes --no-deps --only-binary=:all: --requirement "$here/requirements.txt"; then
  for moved in "$work"/moved-*; do
    [ ! -L "$moved" ] || mv "$moved" "$bin/${moved#"$work"/moved-}"
  done
  fail 'pip could not install the wheels it had checked; the commands it had moved aside are back'
fi

# The new npm store is put together beside the old one, then swapped in, so
# a failed copy leaves the old one working.
rm -rf "$data/npm.new" "$data/npm.old"
mkdir -p "$data/npm.new"
cp "$here/package.json" "$here/package-lock.json" "$data/npm.new/"
mv "$work/npm/node_modules" "$data/npm.new/node_modules"
[ ! -d "$data/npm" ] || mv "$data/npm" "$data/npm.old"
mv "$data/npm.new" "$data/npm"
rm -rf "$data/npm.old"
for command in markdownlint-cli2 prettier; do
  replace "$command"
  ln -s "$data/npm/node_modules/.bin/$command" "$bin/$command"
done

cp "$here/versions" "$here/requirements.txt" "$here/package-lock.json" "$data/"
say "installed the toolchain into $bin"
