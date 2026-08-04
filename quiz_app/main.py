#!/usr/bin/env python3
"""Punto de entrada de la app de preparación de entrevistas."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from quizprep.ui import run  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(run())
