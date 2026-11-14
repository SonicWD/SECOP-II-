# -*- coding: utf-8 -*-
"""Rutas HTTP de la API (capa de presentación)."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import VERSION
from app.domain.catalogo import (
    COMPONENTES,
    EJEMPLOS,
    LINEA_CURSO,
    PIPELINE,
    PROBLEMAS,
)
from app.repositories.artefactos import repo
from app.schemas.requests import BuscarIn, LimpiezaIn, TextoIn
from app.services.prediccion import BusquedaService, CatalogoService, ClasificadorService
from app.services.texto import resumen_limpieza

router = APIRouter(prefix="/api")

_clasificar = ClasificadorService()
_buscar = BusquedaService()
_catalogo = CatalogoService()


@router.get("/health")
def health():
    art = repo.cargar_modelo()
    return {
        "ok": True,
        "version": VERSION,
        "modelo": art.get("metricas", {}).get("modelo", "Regresión logística C=4"),
        "n_clases": art.get("metricas", {}).get("n_clases"),
    }


@router.get("/meta")
def meta():
    return _catalogo.meta()


@router.get("/seleccion")
def seleccion():
    """Preguntas de evaluación: modelo, métricas, cantidad y herramientas."""
    return _catalogo.seleccion_modelo()


@router.get("/diseno")
def diseno():
    """Diseño esquemático, fuente y pipeline."""
    res = repo.cargar_resultados()
    return {
        "componentes": COMPONENTES,
        "fuente": {
            "nombre": "SECOP II – Procesos de Contratación",
            "url": res.get(
                "fuente",
                "https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt",
            ),
            "dataset_id": res.get("dataset_id", "p6dx-8zbt"),
            "acceso": "API SODA pública, sin token",
            "campos_texto": ["nombre_del_procedimiento", "descripcion_del_procedimiento"],
            "etiqueta": "segmento UNSPSC (2 dígitos del código principal)",
        },
        "pipeline": PIPELINE,
        "problemas": PROBLEMAS,
    }


@router.get("/resultados")
def resultados():
    res = repo.cargar_resultados()
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
        "seleccion": _catalogo.seleccion_modelo(),
    }


@router.get("/ejemplos")
def ejemplos():
    return {"ejemplos": EJEMPLOS}


@router.get("/segmentos")
def segmentos():
    art = repo.cargar_modelo()
    segs = art["segmentos"]
    usados = sorted(set(str(x) for x in art["etiquetas_busqueda"]))
    return {
        "total_catalogo": len(segs),
        "en_modelo": [
            {"codigo": c, "nombre": segs.get(c, f"Segmento {c}")} for c in usados
        ],
    }


@router.get("/pipeline")
def pipeline():
    return {
        "pipeline": PIPELINE,
        "problemas": PROBLEMAS,
        "linea_curso": LINEA_CURSO,
        "componentes": COMPONENTES,
        "seleccion": _catalogo.seleccion_modelo(),
    }


@router.post("/limpiar")
def limpiar(body: LimpiezaIn):
    return resumen_limpieza(body.texto)


@router.post("/clasificar")
def clasificar(body: TextoIn):
    return _clasificar.clasificar(body.texto, body.top_k, body.explicar)


@router.post("/buscar")
def buscar(body: BuscarIn):
    return _buscar.buscar(body.consulta, body.k)
