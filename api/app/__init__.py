# -*- coding: utf-8 -*-
"""Fábrica de la aplicación FastAPI."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import CORS_ORIGINS, STATIC_DIR, VERSION
from app.repositories.artefactos import repo
from app.routers.api import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="SECOP II · Clasificación y búsqueda",
        description=(
            "Proyecto final PLN — Universidad de Cundinamarca. "
            "Arquitectura por capas: routers → services → repositories."
        ),
        version=VERSION,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    @app.on_event("startup")
    def startup() -> None:
        repo.cargar_modelo()
        repo.cargar_resultados()

    _montar_estaticos(app)
    return app


def _montar_estaticos(app: FastAPI) -> None:
    if not STATIC_DIR.exists():
        return

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
        if nombre_archivo.startswith("api"):
            raise HTTPException(404)
        candidato = STATIC_DIR / nombre_archivo
        if candidato.is_file():
            return FileResponse(candidato)
        raise HTTPException(404)
