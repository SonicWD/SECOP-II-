# -*- coding: utf-8 -*-
"""API del modelo SECOP II: clasificar y buscar."""

from __future__ import annotations

import os
from pathlib import Path

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parent
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(BASE / "artifacts" / "modelo.joblib")))
STATIC_DIR = Path(os.getenv("STATIC_DIR", str(BASE / "static")))

app = FastAPI(
    title="SECOP II · Clasificación y búsqueda",
    description="Proyecto final PLN — Universidad de Cundinamarca",
    version="1.0.0",
)

origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_artefactos = None


def load():
    global _artefactos
    if _artefactos is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"No está el modelo: {MODEL_PATH}")
        _artefactos = joblib.load(MODEL_PATH)
    return _artefactos


@app.on_event("startup")
def startup():
    load()


class TextoIn(BaseModel):
    texto: str = Field(..., min_length=20, description="Nombre y descripción del proceso")
    top_k: int = Field(5, ge=1, le=10)


class BuscarIn(BaseModel):
    consulta: str = Field(..., min_length=20)
    k: int = Field(5, ge=1, le=5)


def nombre_segmento(codigo: str, segmentos: dict) -> str:
    return segmentos.get(str(codigo), f"Segmento {codigo}")


@app.get("/api/health")
def health():
    art = load()
    return {
        "ok": True,
        "modelo": art.get("metricas", {}).get("modelo", "Regresión logística C=4"),
        "n_clases": art.get("metricas", {}).get("n_clases"),
    }


@app.get("/api/meta")
def meta():
    art = load()
    m = art.get("metricas", {})
    return {
        "proyecto": "SECOP II — Clasificación y búsqueda de procesos",
        "autor": "Wilson Alfonso Díaz Capador",
        "universidad": "Universidad de Cundinamarca",
        "fuente": "https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt",
        "modelo": m.get("modelo", "Regresión logística C=4"),
        "metricas_referencia": {
            "f1_macro_prueba": 0.5056,
            "exactitud_prueba": 0.5609,
            "recall_at_5": 0.6975,
        },
        **{k: m.get(k) for k in ("n_train", "n_test", "n_clases")},
    }


@app.post("/api/clasificar")
def clasificar(body: TextoIn):
    texto = body.texto.strip()
    if len(texto) < 20:
        raise HTTPException(400, "Escribe al menos 20 caracteres.")
    art = load()
    modelo = art["modelo"]
    segmentos = art["segmentos"]
    pred = modelo.predict([texto])[0]
    clf = modelo.named_steps["modelo"]
    ranking = []
    if hasattr(clf, "predict_proba"):
        probs = modelo.predict_proba([texto])[0]
        clases = modelo.classes_
        orden = np.argsort(probs)[::-1][: body.top_k]
        ranking = [
            {
                "codigo": str(clases[i]),
                "nombre": nombre_segmento(str(clases[i]), segmentos),
                "probabilidad": round(float(probs[i]), 4),
            }
            for i in orden
        ]
    else:
        ranking = [{
            "codigo": str(pred),
            "nombre": nombre_segmento(str(pred), segmentos),
            "probabilidad": None,
        }]
    return {
        "segmento": str(pred),
        "nombre": nombre_segmento(str(pred), segmentos),
        "ranking": ranking,
    }


@app.post("/api/buscar")
def buscar(body: BuscarIn):
    consulta = body.consulta.strip()
    if len(consulta) < 20:
        raise HTTPException(400, "Escribe al menos 20 caracteres.")
    art = load()
    modelo = art["modelo"]
    nn = art["nn"]
    textos = art["textos_busqueda"]
    etiquetas = art["etiquetas_busqueda"]
    segmentos = art["segmentos"]
    vec = modelo.named_steps["tfidf"].transform([consulta])
    dist, idx = nn.kneighbors(vec, n_neighbors=int(body.k))
    vecinos = []
    for rango, (i, d) in enumerate(zip(idx[0], dist[0]), start=1):
        seg = str(etiquetas[i])
        vecinos.append({
            "rango": rango,
            "segmento": seg,
            "nombre": nombre_segmento(seg, segmentos),
            "similitud": round(1.0 - float(d), 4),
            "extracto": str(textos[i])[:320],
        })
    return {"vecinos": vecinos}


# Interfaz estática (build de Next) en el mismo origen que la API.
if STATIC_DIR.exists():
    assets = STATIC_DIR / "_next"
    if assets.exists():
        app.mount("/_next", StaticFiles(directory=assets), name="next_assets")

    @app.get("/")
    def index():
        index_file = STATIC_DIR / "index.html"
        if not index_file.exists():
            raise HTTPException(404, "Falta el build de la interfaz (static/index.html).")
        return FileResponse(index_file)
