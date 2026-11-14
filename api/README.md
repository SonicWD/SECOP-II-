# API SECOP II

Arquitectura por capas (SOLID):

```
api/
├── main.py                 # uvicorn main:app
├── app/
│   ├── config.py           # rutas y versión
│   ├── domain/             # pipeline, componentes, ejemplos
│   ├── schemas/            # Pydantic (entrada)
│   ├── repositories/       # joblib + resultados.json
│   ├── services/           # clasificar, buscar, catálogo
│   └── routers/            # HTTP /api/*
├── artifacts/modelo.joblib
└── data/resultados.json
```

## Endpoints clave

| Ruta | Uso |
| --- | --- |
| `GET /api/health` | Estado del modelo |
| `GET /api/seleccion` | Modelo elegido, métricas, nº de modelos, herramientas |
| `GET /api/diseno` | Componentes, fuente, pipeline |
| `GET /api/meta` | Metadatos + selección |
| `POST /api/clasificar` | Segmento UNSPSC |
| `POST /api/buscar` | Vecinos por coseno |

## Respuestas de evaluación

- **Modelo:** Regresión logística C=4  
- **Modelos probados:** 7  
- **Criterio:** F1 macro medio en CV de 5 pliegues (train)  
- **Desempeño (prueba):** F1 macro ≈ 0,506 · Exactitud ≈ 0,561 · Recall@5 ≈ 0,698  
- **Herramientas:** pandas, scikit-learn (TF-IDF, CV, métricas, NearestNeighbors), joblib  
