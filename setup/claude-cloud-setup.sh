#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Tanner Golden
# SPDX-License-Identifier: MIT
#
# Installs the environment's toolchain into a Claude Code cloud session.
#
# WHY THIS EXISTS. A cloud session starts from its own image, not this one,
# and takes a setup script instead. This one downloads one release's
# installer and pins, checks each file against its SHA-256 before anything
# runs, and installs the tools for the session's user, into ~/.local/bin,
# ahead of the copies the session's image carries. Every check tool is then
# the version the image holds; the session keeps its own Python and, when it
# has one, its own Node.js.
#
# Copy it with its pins filled in: `make cloud-setup VERSION=vX.Y.Z` in this
# repository prints it ready to paste, into the cloud environment's settings
# under Setup script. The copy here keeps placeholders, and installs nothing.
#
# IT NEVER FAILS THE SESSION. A setup script that exits non-zero stops the
# session from starting, so every failure prints a notice instead, and the
# session starts with the tools its own image has.
#
# It runs in a subshell and never exits the script it is pasted into, so it
# can share the field with another setup script. Paste it above one that
# ends by exiting, as the intelligence hub's does.

(
  VERSION='@VERSION@'
  INSTALL_SHA256='@INSTALL_SHA256@'
  VERSIONS_SHA256='@VERSIONS_SHA256@'
  REQUIREMENTS_SHA256='@REQUIREMENTS_SHA256@'
  PACKAGE_SHA256='@PACKAGE_SHA256@'
  LOCK_SHA256='@LOCK_SHA256@'
  BASE="${ENVIRONMENT_BASE:-https://raw.githubusercontent.com/tannergolden/environment}"

  notice() {
    printf 'environment: %s\n' "$*" >&2
  }

  sha256() {
    if command -v sha256sum >/dev/null 2>&1; then
      sha256sum "$1" | cut -d ' ' -f 1
    else
      shasum -a 256 "$1" | cut -d ' ' -f 1
    fi
  }

  main() {
    case "$VERSION" in
      @*)
        notice 'no release is pinned here yet; run make cloud-setup VERSION=vX.Y.Z in tannergolden/environment'
        return 0
        ;;
    esac
    for tool in curl python3; do
      command -v "$tool" >/dev/null 2>&1 \
        || { notice "$tool is not installed, so the toolchain was not installed"; return 0; }
    done
    dir="$(mktemp -d)" || { notice 'could not make a scratch folder'; return 0; }
    trap 'rm -rf "$dir"' EXIT
    mkdir "$dir/toolchain"
    for entry in "install.sh $INSTALL_SHA256" "versions $VERSIONS_SHA256" \
      "requirements.txt $REQUIREMENTS_SHA256" "package.json $PACKAGE_SHA256" \
      "package-lock.json $LOCK_SHA256"; do
      file="${entry%% *}"
      pin="${entry#* }"
      curl -fsSL --retry 2 --max-time 30 "$BASE/$VERSION/toolchain/$file" -o "$dir/toolchain/$file" \
        || { notice "could not download toolchain/$file for $VERSION, so nothing was installed"; return 0; }
      [ "$(sha256 "$dir/toolchain/$file")" = "$pin" ] \
        || { notice "toolchain/$file for $VERSION does not match its pin, so nothing was installed"; return 0; }
    done
    sh "$dir/toolchain/install.sh" --user \
      || notice 'the installer reported a problem, so the session keeps some of its own tools; see above'
  }

  main
) || true
