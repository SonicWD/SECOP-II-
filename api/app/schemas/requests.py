# -*- coding: utf-8 -*-
"""Contratos de entrada (Pydantic)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TextoIn(BaseModel):
    texto: str = Field(..., min_length=20, description="Nombre y descripción del proceso")
    top_k: int = Field(5, ge=1, le=10)
    explicar: bool = True


class BuscarIn(BaseModel):
    consulta: str = Field(..., min_length=20)
    k: int = Field(5, ge=1, le=5)


class LimpiezaIn(BaseModel):
    texto: str = Field(..., min_length=1)
