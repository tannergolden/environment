# --- 🐳 The Environment's Commands ---
#
# The commands CI runs, so a contributor runs the same ones: 🚦 Checks calls
# `make lint` and `make test`, and 🏷️ Cut Release calls them again on the
# commit it is about to tag. `make help` lists every target.
#
# `make test` builds the image and checks it, so it needs Docker. Behind a
# proxy that inspects TLS, hand the build its CA bundle:
#
#     make test BUILD_FLAGS='--secret id=ca-bundle,src=/path/to/ca-bundle.crt'

PYTHON ?= python3
IMAGE ?= environment:local
BUILD_FLAGS ?=
VERSION ?=

.PHONY: help lint test test-unit test-image build lock cloud-setup

help: ## List every target
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | sed -E 's/:.*## /|/' | awk -F '|' '{ printf "  %-12s %s\n", $$1, $$2 }'

lint: ## The repository validator, and shellcheck on both scripts
	$(PYTHON) .github/scripts/validate-repository.py
	shellcheck --shell=sh toolchain/install.sh
	shellcheck setup/claude-cloud-setup.sh

test: test-unit test-image ## Everything CI tests: the scripts, then the image

test-unit: ## The tests that need no Docker
	$(PYTHON) -m unittest discover -s .github/scripts -p 'test_*.py'
	$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

test-image: build ## Build the image, then check every tool it holds
	ENVIRONMENT_IMAGE=$(IMAGE) $(PYTHON) -m unittest discover -s tests/image -p 'test_*.py'

build: ## Build the image for this machine's architecture
	docker build $(BUILD_FLAGS) --tag $(IMAGE) .

lock: ## Recompile both locks from their pins, after changing one (needs uv and npm)
	uv pip compile toolchain/requirements.in --universal --python-version 3.12 --generate-hashes \
		--quiet --custom-compile-command 'make lock' --output-file toolchain/requirements.txt
	cd toolchain && npm install --package-lock-only --ignore-scripts --no-audit --no-fund

cloud-setup: ## Print the Claude cloud setup script, pinned to VERSION
	@$(PYTHON) .github/scripts/print-cloud-setup.py $(VERSION)
