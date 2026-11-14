# SECOP II — Clasificación y búsqueda

Proyecto final de **Procesamiento de Lenguaje Natural**  
Wilson Alfonso Díaz Capador · Universidad de Cundinamarca

Clasifica el segmento UNSPSC de un proceso de contratación a partir del nombre y la descripción, y recupera procesos similares (TF-IDF + distancia de coseno). Interfaz Next.js + API FastAPI con el modelo en joblib.

## Estructura

```
proyecto/
├── web/          # Interfaz Next.js (look ODC / awesome-design-md)
├── api/          # FastAPI + artifacts/modelo.joblib
├── DESIGN.md     # Sistema visual
└── README.md
```

## Requisitos

- Node.js 20+
- Python 3.11+ (probado con 3.14)
- Dependencias del modelo: `scikit-learn==1.8.0`

## Arranque local

### 1. API

```bash
cd api
python -m pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Prueba: http://127.0.0.1:8000/api/health

### 2. Interfaz

```bash
cd web
npm install
npm run dev
```

Abre http://localhost:3000  
Las rutas `/api/*` se reescriben hacia la API (`API_URL`, por defecto `http://127.0.0.1:8000`).

## Endpoints

| Método | Ruta | Uso |
| --- | --- | --- |
| GET | `/api/health` | Estado del modelo |
| GET | `/api/meta` | Metadatos y métricas de referencia |
| POST | `/api/clasificar` | `{ "texto": "..." }` → segmento UNSPSC |
| POST | `/api/buscar` | `{ "consulta": "..." }` → top-5 vecinos |

## Resultados de referencia

- Modelo: regresión logística C=4  
- F1 macro prueba: **0,506** · Exactitud: **0,561** · Recall@5: **0,698**  
- Fuente: [SECOP II – Procesos de Contratación](https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt) (p6dx-8zbt)

## Despliegue en la nube

El `Dockerfile` construye la UI (Next export) y la sirve desde FastAPI en el **mismo origen** (`/` + `/api/*`).

1. Repo: https://github.com/SonicWD/SECOP-II-
2. **Render**: conectar el repo; usa `render.yaml` (Docker, health `/api/health`).
3. **Hugging Face Spaces**: Space tipo Docker apuntando a este Dockerfile.
4. Local unificado (después de `STATIC_EXPORT=1 npm run build` y copiar `web/out` → `api/static`):

```bash
cd api
uvicorn main:app --port 8000
# UI+API en http://127.0.0.1:8000
```

## Licencia de uso académico

Entrega de curso. Datos públicos de datos.gov.co.
