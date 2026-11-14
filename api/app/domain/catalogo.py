# -*- coding: utf-8 -*-
"""Contenido estático del proyecto: diseño, fuente, pipeline y ejemplos."""

from __future__ import annotations

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

# Diseño esquemático de componentes (UI ↔ API ↔ modelo ↔ datos)
COMPONENTES = [
    {
        "id": "ui",
        "nombre": "Interfaz Next.js",
        "rol": "Captura el texto del proceso y muestra segmento, ranking y vecinos",
    },
    {
        "id": "api",
        "nombre": "API FastAPI",
        "rol": "Expone /api/clasificar, /api/buscar, /api/health y metadatos",
    },
    {
        "id": "preproceso",
        "nombre": "Limpieza de texto",
        "rol": "Quita URL, normaliza espacios y valida longitud mínima",
    },
    {
        "id": "tfidf",
        "nombre": "Vectorizador TF-IDF",
        "rol": "Uni/bigramas en español (≤20 mil términos) dentro del pipeline sklearn",
    },
    {
        "id": "clasificador",
        "nombre": "Clasificador",
        "rol": "Regresión logística C=4 con class_weight=balanced → segmento UNSPSC",
    },
    {
        "id": "busqueda",
        "nombre": "Índice de vecinos",
        "rol": "NearestNeighbors sobre TF-IDF; distancia de coseno → top-k similares",
    },
    {
        "id": "fuente",
        "nombre": "SECOP II (datos.gov.co)",
        "rol": "API SODA p6dx-8zbt: nombre + descripción como texto; código como etiqueta",
    },
]

PIPELINE = [
    {"paso": 1, "nombre": "Consulta API SECOP II", "detalle": "SODA datos.gov.co, páginas de 8.000 filas"},
    {"paso": 2, "nombre": "Limpieza de texto", "detalle": "Une nombre+descripción, quita URL, mínimo 40 caracteres"},
    {"paso": 3, "nombre": "Etiqueta UNSPSC", "detalle": "Segmento = 2 dígitos del código; sin leakage al texto"},
    {"paso": 4, "nombre": "Recorte de muestra", "detalle": "Mín. 80 y tope 700 por clase; semilla 42"},
    {"paso": 5, "nombre": "Partición 80/20", "detalle": "Estratificada; la prueba no elige el modelo"},
    {"paso": 6, "nombre": "TF-IDF + CV", "detalle": "Uni/bigramas, 5 pliegues, criterio F1 macro"},
    {"paso": 7, "nombre": "Despliegue", "detalle": "Interfaz Next.js + API FastAPI en Render"},
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

HERRAMIENTAS_SELECCION = [
    "pandas — descarga y preparación de la muestra SECOP II",
    "scikit-learn — TfidfVectorizer, Pipeline, StratifiedKFold, cross_val_score",
    "scikit-learn.metrics — f1_score (macro), accuracy_score",
    "scikit-learn.neighbors — NearestNeighbors (métrica coseno) para Recall@5 y MRR@5",
    "joblib — persistencia del pipeline ganador (modelo.joblib)",
    "Criterio de selección: F1 macro medio en validación cruzada de 5 pliegues (solo train)",
]
