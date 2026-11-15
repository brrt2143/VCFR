#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$(readlink -f -- "$0")")"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip install -e .
if [ ! -e config.json ]; then cp config.example.json config.json; fi
mkdir -p models
printf 'Preparado. Inicia con .venv/bin/vcfr o ./vcfr/iniciar.sh.\n'
printf 'Para Calibre, define VCFR_COMMAND=%s/.venv/bin/vcfr en su entorno.\n' "$PWD"
