# --- 🐳 The Environment ---
#
# The machine every repository is worked on in: Ubuntu 24.04 pinned by
# digest, git, Python 3.12, Node.js 22, and the tools the standards' checks
# run, each at the exact version toolchain/ pins. 🏷️ Cut Release publishes it
# as ghcr.io/tannergolden/environment, for linux/amd64 and linux/arm64.
#
# A repository's development container names it, and nothing else:
#
#     { "image": "ghcr.io/tannergolden/environment:1" }
#
# WHAT IS EXACT AND WHAT IS NOT. The base is pinned by digest, and every tool
# the checks run by version and checksum, in toolchain/. The packages added
# from Ubuntu's archive below are its current ones when the image is built,
# and the base's own move with its digest, which Dependabot proposes. The
# tests hold the versions that matter there: Python 3.12, git 2.40 or newer.
#
# Behind a proxy that inspects TLS, pass its CA bundle as the `ca-bundle`
# secret. The downloads trust it and no layer of the image keeps it:
#
#     docker build --secret id=ca-bundle,src=/path/to/ca-bundle.crt .

FROM ubuntu:24.04@sha256:68ee22004a9109b44973313b02ff7b1de250f1de0f5ecb628d73f579aaff33ac

ARG DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Ubuntu's own packages, signed by its archive. The EXTERNALLY-MANAGED marker
# goes because this Python is the environment's own: a development
# container's `pip install --user` would otherwise be refused.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl git less make openssh-client procps \
      python3 python3-pip python3-venv sudo xz-utils \
 && rm -rf /var/lib/apt/lists/* \
 && rm -f /usr/lib/python3*/EXTERNALLY-MANAGED

# The user a development container works as, with sudo, at the uid a
# Codespace's files belong to. Ubuntu's own `ubuntu` user holds it first.
RUN userdel --remove ubuntu \
 && useradd --create-home --uid 1000 --user-group --shell /bin/bash vscode \
 && echo 'vscode ALL=(root) NOPASSWD:ALL' > /etc/sudoers.d/vscode \
 && chmod 0440 /etc/sudoers.d/vscode

# Every tool the checks run, by the same script a cloud session runs.
RUN --mount=type=bind,source=toolchain,target=/tmp/toolchain \
    --mount=type=secret,id=ca-bundle,required=false \
    if [ -s /run/secrets/ca-bundle ]; then \
      export CURL_CA_BUNDLE=/run/secrets/ca-bundle PIP_CERT=/run/secrets/ca-bundle \
        NODE_EXTRA_CA_CERTS=/run/secrets/ca-bundle npm_config_cafile=/run/secrets/ca-bundle; \
    fi \
 && sh /tmp/toolchain/install.sh

# The publish job adds the source, revision, version and creation labels. The
# metadata label tells a development container to work as `vscode`, so a
# repository's devcontainer.json needs only the image. There is no licences
# label: the image redistributes software under many licences, GPL ones among
# them, and the README says where each is.
LABEL org.opencontainers.image.title="environment" \
      org.opencontainers.image.description="The development environment for tannergolden repositories: Ubuntu 24.04, git, Python 3.12, Node.js 22 and the standards' check tools, pinned." \
      devcontainer.metadata="[{\"remoteUser\":\"vscode\"}]"
