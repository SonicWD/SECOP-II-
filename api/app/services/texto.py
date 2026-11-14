# -*- coding: utf-8 -*-
"""Servicio de preprocesamiento de texto."""

from __future__ import annotations

import re

URL_RE = re.compile(r"https?://\S+")
SPACE_RE = re.compile(r"\s+")
TOKEN_RE = re.compile(r"(?u)\b[a-záéíóúüñ]{3,}\b")


def limpiar_texto(texto: str) -> str:
    t = URL_RE.sub(" ", texto)
    return SPACE_RE.sub(" ", t).strip()


def resumen_limpieza(original: str) -> dict:
    limpio = limpiar_texto(original)
    tokens = TOKEN_RE.findall(limpio.lower())
    return {
        "original": original,
        "limpio": limpio,
        "caracteres": len(limpio),
        "tokens_aprox": len(tokens),
        "urls_retiradas": len(URL_RE.findall(original)),
        "apto_modelo": len(limpio) >= 20,
    }
