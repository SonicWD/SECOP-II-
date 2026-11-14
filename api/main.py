# -*- coding: utf-8 -*-
"""Punto de entrada: uvicorn main:app (Docker / Render / local)."""

from __future__ import annotations

from app import create_app

app = create_app()
