# -*- coding: utf-8 -*-
"""Configuración de la API (única fuente de rutas y versión)."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
VERSION = "1.2.0"

MODEL_PATH = Path(os.getenv("MODEL_PATH", str(BASE_DIR / "artifacts" / "modelo.joblib")))
STATIC_DIR = Path(os.getenv("STATIC_DIR", str(BASE_DIR / "static")))
RESULTADOS_PATH = BASE_DIR / "data" / "resultados.json"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
