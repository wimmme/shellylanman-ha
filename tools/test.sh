#!/bin/sh
# Runs the integration tests in Docker (Python 3.14), against the pinned Home
# Assistant version or another phcc version: sh tools-test.sh [0.13.368]
set -eu
cd "$(dirname "$0")/.."
PHCC="${1:-$(sed -n 's/^pytest-homeassistant-custom-component==//p' requirements_test.txt)}"
docker run --rm -e PYTHONDONTWRITEBYTECODE=1 -v "$PWD":/src -w /src -v slm-ha-pip:/root/.cache/pip python:3.14-slim \
  sh -c "pip install -q pytest-homeassistant-custom-component==$PHCC && python -m pytest -q -p no:cacheprovider"
