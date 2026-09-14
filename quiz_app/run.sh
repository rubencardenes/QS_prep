#!/usr/bin/env bash
# Lanza la app creando el entorno virtual la primera vez.
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x .venv/bin/python ]; then
  echo "Creando entorno virtual…"
  if command -v uv >/dev/null 2>&1; then
    uv venv .venv
  else
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
  fi
fi

# Actualiza también entornos existentes cuando cambian las dependencias.
if command -v uv >/dev/null 2>&1; then
  uv pip install --python .venv/bin/python -r requirements.txt
else
  .venv/bin/pip install -r requirements.txt
fi

exec .venv/bin/python main.py "$@"
