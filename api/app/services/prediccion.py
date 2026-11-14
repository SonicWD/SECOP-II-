# -*- coding: utf-8 -*-
"""Servicios de clasificación, explicación y búsqueda (lógica de negocio)."""

from __future__ import annotations

from typing import Any

import numpy as np
from fastapi import HTTPException

from app.repositories.artefactos import ArtefactoRepository, repo
from app.services.texto import limpiar_texto


def nombre_segmento(codigo: str, segmentos: dict) -> str:
    return segmentos.get(str(codigo), f"Segmento {codigo}")


def explicar_prediccion(
    modelo,
    texto: str,
    clase: str,
    feature_names: np.ndarray | None,
    top_n: int = 8,
) -> list[dict]:
    """Aporte TF-IDF × coeficientes de la clase predicha."""
    tfidf = modelo.named_steps["tfidf"]
    clf = modelo.named_steps["modelo"]
    names = feature_names
    if names is None:
        names = np.array(tfidf.get_feature_names_out())
    vec = tfidf.transform([texto])
    clases = list(clf.classes_)
    if clase not in clases or not hasattr(clf, "coef_"):
        return []
    idx_c = clases.index(clase)
    coef = clf.coef_[idx_c]
    row = vec.tocsr()
    indices, data = row.indices, row.data
    if len(indices) == 0:
        return []
    aportes = coef[indices] * data
    order = np.argsort(aportes)[::-1][:top_n]
    return [
        {
            "termino": str(names[indices[j]]),
            "tfidf": round(float(data[j]), 4),
            "aporte": round(float(aportes[j]), 4),
        }
        for j in order
    ]


class ClasificadorService:
    def __init__(self, repository: ArtefactoRepository = repo) -> None:
        self._repo = repository

    def clasificar(self, texto: str, top_k: int = 5, explicar: bool = True) -> dict[str, Any]:
        limpio = limpiar_texto(texto)
        if len(limpio) < 20:
            raise HTTPException(400, "Escribe al menos 20 caracteres útiles tras limpiar URLs.")
        art = self._repo.cargar_modelo()
        modelo = art["modelo"]
        segmentos = art["segmentos"]
        pred = str(modelo.predict([limpio])[0])
        clf = modelo.named_steps["modelo"]
        ranking: list[dict] = []
        if hasattr(clf, "predict_proba"):
            probs = modelo.predict_proba([limpio])[0]
            clases = modelo.classes_
            orden = np.argsort(probs)[::-1][:top_k]
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
        terminos = (
            explicar_prediccion(modelo, limpio, pred, self._repo.feature_names)
            if explicar
            else []
        )
        return {
            "segmento": pred,
            "nombre": nombre_segmento(pred, segmentos),
            "ranking": ranking,
            "terminos_clave": terminos,
            "texto_usado": limpio,
        }


class BusquedaService:
    def __init__(self, repository: ArtefactoRepository = repo) -> None:
        self._repo = repository

    def buscar(self, consulta: str, k: int = 5) -> dict[str, Any]:
        limpia = limpiar_texto(consulta)
        if len(limpia) < 20:
            raise HTTPException(400, "Escribe al menos 20 caracteres.")
        art = self._repo.cargar_modelo()
        modelo = art["modelo"]
        nn = art["nn"]
        textos = art["textos_busqueda"]
        etiquetas = art["etiquetas_busqueda"]
        segmentos = art["segmentos"]
        vec = modelo.named_steps["tfidf"].transform([limpia])
        dist, idx = nn.kneighbors(vec, n_neighbors=int(k))
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
        return {"vecinos": vecinos, "consulta_usada": limpia}


class CatalogoService:
    """Arma respuestas de meta, resultados, diseño y preguntas del curso."""

    def __init__(self, repository: ArtefactoRepository = repo) -> None:
        self._repo = repository

    def ganador(self) -> dict[str, Any] | None:
        res = self._repo.cargar_resultados()
        return next(
            (
                r
                for r in res.get("resultados", [])
                if r.get("modelo") == res.get("modelo_seleccionado")
            ),
            None,
        )

    def seleccion_modelo(self) -> dict[str, Any]:
        """Respuestas explícitas a las preguntas de evaluación."""
        from app.domain.catalogo import HERRAMIENTAS_SELECCION

        res = self._repo.cargar_resultados()
        g = self.ganador()
        busq = res.get("busqueda", {})
        return {
            "modelo_seleccionado": res.get(
                "modelo_seleccionado", "Regresión logística C=4"
            ),
            "modelos_probados": res.get("modelos_probados", 7),
            "criterio": res.get(
                "criterio",
                "F1 macro medio de validación cruzada de cinco pliegues sobre el entrenamiento",
            ),
            "desempeno": {
                "f1_macro_cv": g["f1_macro_cv"] if g else 0.4879,
                "f1_macro_prueba": g["f1_macro_prueba"] if g else 0.5056,
                "exactitud_prueba": g["exactitud_prueba"] if g else 0.5609,
                "recall_at_5": busq.get("recall_at_5", 0.6975),
                "mrr_at_5": busq.get("mrr_at_5", 0.5289),
            },
            "metricas_usadas": [
                "F1 macro (CV 5 pliegues) — criterio de selección del modelo",
                "F1 macro (prueba) — informe final, no decide",
                "Exactitud (prueba)",
                "Recall@5 y MRR@5 — calidad de la búsqueda por coseno",
            ],
            "herramientas": HERRAMIENTAS_SELECCION,
            "modelos_comparados": [r.get("modelo") for r in res.get("resultados", [])],
        }

    def meta(self) -> dict[str, Any]:
        from app.domain.catalogo import LINEA_CURSO

        art = self._repo.cargar_modelo()
        res = self._repo.cargar_resultados()
        m = art.get("metricas", {})
        g = self.ganador()
        seleccion = self.seleccion_modelo()
        return {
            "proyecto": "SECOP II — Clasificación y búsqueda de procesos",
            "autor": "Wilson Alfonso Díaz Capador",
            "universidad": "Universidad de Cundinamarca",
            "curso": "Procesamiento de Lenguaje Natural · REA 2",
            "fuente": res.get(
                "fuente",
                "https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt",
            ),
            "modelo": m.get("modelo", seleccion["modelo_seleccionado"]),
            "criterio": seleccion["criterio"],
            "metricas_referencia": {
                "f1_macro_prueba": seleccion["desempeno"]["f1_macro_prueba"],
                "f1_macro_cv": seleccion["desempeno"]["f1_macro_cv"],
                "exactitud_prueba": seleccion["desempeno"]["exactitud_prueba"],
                "recall_at_5": seleccion["desempeno"]["recall_at_5"],
                "mrr_at_5": seleccion["desempeno"]["mrr_at_5"],
            },
            "seleccion_modelo": seleccion,
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
