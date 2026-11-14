# -*- coding: utf-8 -*-
"""Repositorio de artefactos: modelo joblib y resultados de la corrida."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np

from app.config import MODEL_PATH, RESULTADOS_PATH


class ArtefactoRepository:
    """Carga perezosa y cacheada (una sola responsabilidad: I/O de artefactos)."""

    def __init__(
        self,
        model_path: Path = MODEL_PATH,
        resultados_path: Path = RESULTADOS_PATH,
    ) -> None:
        self._model_path = model_path
        self._resultados_path = resultados_path
        self._artefactos: dict[str, Any] | None = None
        self._resultados: dict[str, Any] | None = None
        self._feature_names: np.ndarray | None = None

    def cargar_modelo(self) -> dict[str, Any]:
        if self._artefactos is None:
            if not self._model_path.exists():
                raise FileNotFoundError(f"No está el modelo: {self._model_path}")
            self._artefactos = joblib.load(self._model_path)
            tfidf = self._artefactos["modelo"].named_steps["tfidf"]
            self._feature_names = np.array(tfidf.get_feature_names_out())
        return self._artefactos

    def cargar_resultados(self) -> dict[str, Any]:
        if self._resultados is None:
            if self._resultados_path.exists():
                self._resultados = json.loads(
                    self._resultados_path.read_text(encoding="utf-8")
                )
            else:
                self._resultados = {}
        return self._resultados

    @property
    def feature_names(self) -> np.ndarray | None:
        if self._feature_names is None and self._artefactos is not None:
            tfidf = self._artefactos["modelo"].named_steps["tfidf"]
            self._feature_names = np.array(tfidf.get_feature_names_out())
        return self._feature_names


# Instancia compartida (inyección simple sin framework DI)
repo = ArtefactoRepository()
