# -*- coding: utf-8 -*-
"""Entrena el modelo ganador y lo guarda en api/artifacts para el despliegue."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline

from entrenar import (
    SEMILLA,
    SEGMENTOS,
    TOPE_CLASE,
    preparar,
    vectorizador,
)

BASE = Path(__file__).resolve().parent
REPO = BASE.parent
RAW = BASE / "data" / "secop_muestra.csv"
OUT_ARTIFACTS = REPO / "api" / "artifacts"
OUT_DATA = REPO / "api" / "data"
OUT_ARTIFACTS.mkdir(parents=True, exist_ok=True)
OUT_DATA.mkdir(parents=True, exist_ok=True)


def main() -> None:
    if not RAW.exists():
        raise FileNotFoundError(f"Falta la muestra: {RAW}")

    crudo = pd.read_csv(RAW)
    datos = preparar(crudo)
    x = datos["texto"].to_numpy()
    y = datos["segmento"].to_numpy()
    x_tr, x_te, y_tr, y_te = train_test_split(
        x, y, test_size=0.2, random_state=SEMILLA, stratify=y,
    )

    modelo = Pipeline([
        ("tfidf", vectorizador()),
        ("modelo", LogisticRegression(
            C=4.0,
            class_weight="balanced",
            max_iter=400,
            solver="saga",
            random_state=SEMILLA,
        )),
    ])
    print("Ajustando regresión logística C=4…", flush=True)
    modelo.fit(x_tr, y_tr)

    # Muestra compacta para la búsqueda en la API (máx. 2500 textos).
    rng = np.random.default_rng(SEMILLA)
    n_idx = min(2500, len(x_tr))
    idx = rng.choice(len(x_tr), size=n_idx, replace=False)
    textos_busqueda = x_tr[idx]
    etiquetas_busqueda = y_tr[idx]
    matriz_busqueda = modelo.named_steps["tfidf"].transform(textos_busqueda)
    nn_space = NearestNeighbors(n_neighbors=5, metric="cosine")
    nn_space.fit(matriz_busqueda)

    artefactos = {
        "modelo": modelo,
        "nn": nn_space,
        "textos_busqueda": textos_busqueda,
        "etiquetas_busqueda": etiquetas_busqueda,
        "segmentos": SEGMENTOS,
        "metricas": {
            "modelo": "Regresión logística C=4",
            "n_train": int(len(x_tr)),
            "n_test": int(len(x_te)),
            "n_clases": int(len(np.unique(y))),
            "tope_clase": TOPE_CLASE,
        },
    }
    destino = OUT_ARTIFACTS / "modelo.joblib"
    joblib.dump(artefactos, destino, compress=3)
    meta = {
        "archivo": str(destino.name),
        "modelo": "Regresión logística C=4",
        "n_textos_busqueda": int(n_idx),
        "n_clases": int(len(np.unique(y))),
        "segmentos_usados": sorted(set(y.tolist())),
    }
    (OUT_ARTIFACTS / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Guardado:", destino, "tamaño_MB=", round(destino.stat().st_size / 1e6, 2), flush=True)


if __name__ == "__main__":
    main()
