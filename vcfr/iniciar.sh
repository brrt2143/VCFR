#!/usr/bin/env bash
set -euo pipefail
root="$(dirname -- "$(readlink -f -- "$0")")/.."
cd "$root"
exec .venv/bin/python -m vcfr.app "$@"
