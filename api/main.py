# -*- coding: utf-8 -*-
"""API del modelo SECOP II: clasificar, buscar, explicar y reportar."""

from __future__ import annotations

import json
import os
import re
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
RESULTADOS_PATH = BASE / "data" / "resultados.json"

app = FastAPI(
    title="SECOP II · Clasificación y búsqueda",
    description="Proyecto final PLN — Universidad de Cundinamarca",
    version="1.1.0",
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
_resultados = None
_feature_names = None

URL_RE = re.compile(r"https?://\S+")
SPACE_RE = re.compile(r"\s+")

EJEMPLOS = [
    {
        "id": "tic",
        "titulo": "Soporte de cómputo",
        "texto": (
            "Prestación de servicios profesionales de apoyo a la gestión para el "
            "mantenimiento preventivo y correctivo de equipos de cómputo e impresoras "
            "en las sedes de la entidad."
        ),
    },
    {
        "id": "salud",
        "titulo": "Insumos médicos",
        "texto": (
            "Suministro de medicamentos e insumos médico-quirúrgicos para la red "
            "hospitalaria del departamento, incluyendo dispositivos de diagnóstico "
            "y material de curación."
        ),
    },
    {
        "id": "obra",
        "titulo": "Obra civil",
        "texto": (
            "Contrato de obra para la construcción y adecuación de placas huella "
            "y mejoramiento de la vía terciaria en el municipio, con señalización "
            "y obras de drenaje."
        ),
    },
    {
        "id": "educacion",
        "titulo": "Capacitación",
        "texto": (
            "Prestación de servicios de capacitación y formación a funcionarios "
            "públicos en competencias digitales, pedagogía y gestión documental "
            "bajo modalidad presencial y virtual."
        ),
    },
    {
        "id": "aseo",
        "titulo": "Aseo y cafetería",
        "texto": (
            "Suministro de elementos de aseo, cafetería y papelería para las "
            "dependencias de la entidad, conforme a las fichas técnicas del "
            "almacén general."
        ),
    },
]

PIPELINE = [
    {"paso": 1, "nombre": "Consulta API SECOP II", "detalle": "SODA datos.gov.co, páginas de 8.000 filas"},
    {"paso": 2, "nombre": "Limpieza de texto", "detalle": "Une nombre+descripción, quita URL, mínimo 40 caracteres"},
    {"paso": 3, "nombre": "Etiqueta UNSPSC", "detalle": "Segmento = 2 dígitos del código; sin leakage al texto"},
    {"paso": 4, "nombre": "Recorte de muestra", "detalle": "Mín. 80 y tope 700 por clase; semilla 42"},
    {"paso": 5, "nombre": "Partición 80/20", "detalle": "Estratificada; la prueba no elige el modelo"},
    {"paso": 6, "nombre": "TF-IDF + CV", "detalle": "Uni/bigramas, 5 pliegues, criterio F1 macro"},
    {"paso": 7, "nombre": "Despliegue", "detalle": "Interfaz Next.js + API FastAPI en la nube"},
]

PROBLEMAS = [
    {
        "problema": "Desbalance extremo por tipo de contrato",
        "solucion": "Etiqueta = segmento UNSPSC; tope/mínimo por clase; class_weight=balanced; F1 macro",
    },
    {
        "problema": "Leakage del código de categoría",
        "solucion": "Solo nombre + descripción como entrada; el código es etiqueta",
    },
    {
        "problema": "Plantillas administrativas y URLs",
        "solucion": "Limpieza de URL, filtro <40 caracteres; se declara el límite de calidad",
    },
    {
        "problema": "Fecha vacía en el CSV",
        "solucion": "No se fija rango de fechas; se documenta en la propuesta",
    },
    {
        "problema": "Clases raras en la ventana",
        "solucion": "Excluir segmentos con menos de 80 procesos",
    },
    {
        "problema": "Optimizador en max_iter (C=4)",
        "solucion": "Se publica el F1 de esa parada; sigue siendo el mejor en CV",
    },
]

LINEA_CURSO = [
    {
        "rea": "REA1 · Procesamiento de texto",
        "aporte": "Normalización, TF-IDF, stopwords, clasificación y similitud en español",
    },
    {
        "rea": "REA1 · Embeddings",
        "aporte": "Representaciones densas y LSA; en este proyecto LSA+logística fue una variante comparada",
    },
    {
        "rea": "REA2 · YouTube (avances)",
        "aporte": "Pipeline reproducible, validación, métricas y despliegue consumible",
    },
    {
        "rea": "REA2 · Propuesta final SECOP",
        "aporte": "Problemática pública colombiana, UNSPSC, 7 modelos y búsqueda por coseno",
    },
]


def load():
    global _artefactos, _feature_names
    if _artefactos is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"No está el modelo: {MODEL_PATH}")
        _artefactos = joblib.load(MODEL_PATH)
        tfidf = _artefactos["modelo"].named_steps["tfidf"]
        _feature_names = np.array(tfidf.get_feature_names_out())
    return _artefactos


def load_resultados():
    global _resultados
    if _resultados is None:
        if RESULTADOS_PATH.exists():
            _resultados = json.loads(RESULTADOS_PATH.read_text(encoding="utf-8"))
        else:
            _resultados = {}
    return _resultados


@app.on_event("startup")
def startup():
    load()
    load_resultados()


class TextoIn(BaseModel):
    texto: str = Field(..., min_length=20, description="Nombre y descripción del proceso")
    top_k: int = Field(5, ge=1, le=10)
    explicar: bool = True


class BuscarIn(BaseModel):
    consulta: str = Field(..., min_length=20)
    k: int = Field(5, ge=1, le=5)


class LimpiezaIn(BaseModel):
    texto: str = Field(..., min_length=1)


def nombre_segmento(codigo: str, segmentos: dict) -> str:
    return segmentos.get(str(codigo), f"Segmento {codigo}")


def limpiar_texto(texto: str) -> str:
    t = URL_RE.sub(" ", texto)
    t = SPACE_RE.sub(" ", t).strip()
    return t


def explicar_prediccion(modelo, texto: str, clase: str, top_n: int = 8) -> list[dict]:
    """Aporte de términos TF-IDF × coeficientes de la clase predicha (lab TF-IDF/clasificación)."""
    global _feature_names
    tfidf = modelo.named_steps["tfidf"]
    clf = modelo.named_steps["modelo"]
    if _feature_names is None:
        _feature_names = np.array(tfidf.get_feature_names_out())
    vec = tfidf.transform([texto])
    clases = list(clf.classes_)
    if clase not in clases or not hasattr(clf, "coef_"):
        return []
    idx_c = clases.index(clase)
    coef = clf.coef_[idx_c]
    row = vec.tocsr()
    indices = row.indices
    data = row.data
    if len(indices) == 0:
        return []
    aportes = coef[indices] * data
    order = np.argsort(aportes)[::-1][:top_n]
    out = []
    for j in order:
        term = str(_feature_names[indices[j]])
        out.append({
            "termino": term,
            "tfidf": round(float(data[j]), 4),
            "aporte": round(float(aportes[j]), 4),
        })
    return out


@app.get("/api/health")
def health():
    art = load()
    return {
        "ok": True,
        "version": "1.1.0",
        "modelo": art.get("metricas", {}).get("modelo", "Regresión logística C=4"),
        "n_clases": art.get("metricas", {}).get("n_clases"),
    }


@app.get("/api/meta")
def meta():
    art = load()
    res = load_resultados()
    m = art.get("metricas", {})
    ganador = next(
        (r for r in res.get("resultados", []) if r.get("modelo") == res.get("modelo_seleccionado")),
        None,
    )
    return {
        "proyecto": "SECOP II — Clasificación y búsqueda de procesos",
        "autor": "Wilson Alfonso Díaz Capador",
        "universidad": "Universidad de Cundinamarca",
        "curso": "Procesamiento de Lenguaje Natural · REA 2",
        "fuente": res.get(
            "fuente",
            "https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt",
        ),
        "modelo": m.get("modelo", res.get("modelo_seleccionado", "Regresión logística C=4")),
        "criterio": res.get("criterio"),
        "metricas_referencia": {
            "f1_macro_prueba": ganador["f1_macro_prueba"] if ganador else 0.5056,
            "f1_macro_cv": ganador["f1_macro_cv"] if ganador else 0.4879,
            "exactitud_prueba": ganador["exactitud_prueba"] if ganador else 0.5609,
            "recall_at_5": res.get("busqueda", {}).get("recall_at_5", 0.6975),
            "mrr_at_5": res.get("busqueda", {}).get("mrr_at_5", 0.5289),
        },
        "muestra": {
            "filas_descargadas": res.get("filas_descargadas"),
            "filas_modelo": res.get("filas_modelo"),
            "n_train": m.get("n_train") or res.get("n_train"),
            "n_test": m.get("n_test") or res.get("n_test"),
            "n_clases": m.get("n_clases") or res.get("n_clases"),
            "vocabulario": res.get("vocabulario"),
            "departamentos": res.get("departamentos"),
            "min_clase": res.get("min_clase"),
            "tope_clase": res.get("tope_clase"),
            "semilla": res.get("semilla", 42),
        },
        "linea_curso": LINEA_CURSO,
        "repo": "https://github.com/SonicWD/SECOP-II-",
    }


@app.get("/api/resultados")
def resultados():
    res = load_resultados()
    if not res:
        raise HTTPException(404, "No hay resultados.json")
    return {
        "modelo_seleccionado": res.get("modelo_seleccionado"),
        "criterio": res.get("criterio"),
        "modelos": res.get("resultados", []),
        "por_clase_mejores": res.get("por_clase_mejores", []),
        "por_clase_peores": res.get("por_clase_peores", []),
        "busqueda": res.get("busqueda", {}),
        "modelos_probados": res.get("modelos_probados"),
    }


@app.get("/api/ejemplos")
def ejemplos():
    return {"ejemplos": EJEMPLOS}


@app.get("/api/segmentos")
def segmentos():
    art = load()
    segs = art["segmentos"]
    usados = sorted(set(str(x) for x in art["etiquetas_busqueda"]))
    return {
        "total_catalogo": len(segs),
        "en_modelo": [
            {"codigo": c, "nombre": segs.get(c, f"Segmento {c}")}
            for c in usados
        ],
    }


@app.get("/api/pipeline")
def pipeline():
    return {"pipeline": PIPELINE, "problemas": PROBLEMAS, "linea_curso": LINEA_CURSO}


@app.post("/api/limpiar")
def limpiar(body: LimpiezaIn):
    """Vista de preprocesamiento (REA1 procesamiento de texto)."""
    original = body.texto
    limpio = limpiar_texto(original)
    tokens = re.findall(r"(?u)\b[a-záéíóúüñ]{3,}\b", limpio.lower())
    return {
        "original": original,
        "limpio": limpio,
        "caracteres": len(limpio),
        "tokens_aprox": len(tokens),
        "urls_retiradas": len(URL_RE.findall(original)),
        "apto_modelo": len(limpio) >= 20,
    }


@app.post("/api/clasificar")
def clasificar(body: TextoIn):
    texto = limpiar_texto(body.texto)
    if len(texto) < 20:
        raise HTTPException(400, "Escribe al menos 20 caracteres útiles tras limpiar URLs.")
    art = load()
    modelo = art["modelo"]
    segmentos = art["segmentos"]
    pred = str(modelo.predict([texto])[0])
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
            "codigo": pred,
            "nombre": nombre_segmento(pred, segmentos),
            "probabilidad": None,
        }]
    explicacion = explicar_prediccion(modelo, texto, pred) if body.explicar else []
    return {
        "segmento": pred,
        "nombre": nombre_segmento(pred, segmentos),
        "ranking": ranking,
        "terminos_clave": explicacion,
        "texto_usado": texto,
    }


@app.post("/api/buscar")
def buscar(body: BuscarIn):
    consulta = limpiar_texto(body.consulta)
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
    return {"vecinos": vecinos, "consulta_usada": consulta}


# Interfaz estática (build de Next) en el mismo origen que la API.
if STATIC_DIR.exists():
    assets = STATIC_DIR / "_next"
    if assets.exists():
        app.mount("/_next", StaticFiles(directory=assets), name="next_assets")

    logos = STATIC_DIR / "logos"
    if logos.exists():
        app.mount("/logos", StaticFiles(directory=logos), name="logos")

    @app.get("/")
    def index():
        index_file = STATIC_DIR / "index.html"
        if not index_file.exists():
            raise HTTPException(404, "Falta el build de la interfaz (static/index.html).")
        return FileResponse(index_file)

    @app.get("/{nombre_archivo}")
    def estatico_raiz(nombre_archivo: str):
        """favicon, robots, etc. del export de Next (no pisa /api/*)."""
        if nombre_archivo.startswith("api"):
            raise HTTPException(404)
        candidato = STATIC_DIR / nombre_archivo
        if candidato.is_file():
            return FileResponse(candidato)
        raise HTTPException(404)
