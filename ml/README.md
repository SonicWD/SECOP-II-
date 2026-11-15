# Laboratorio ML — SECOP II

Aquí está el **entrenamiento y la comparación de modelos**. La API en `../api` solo **sirve** el modelo ya elegido.

## Archivos

| Archivo | Rol |
| --- | --- |
| `entrenar.py` | Descarga SODA, limpia, prueba **7 modelos**, elige por F1 macro CV, escribe `resultados.json` |
| `exportar_modelo.py` | Reentrena logística C=4 y guarda `../api/artifacts/modelo.joblib` |
| `resultados.json` | Métricas de la corrida (lo consume la API/UI) |
| `data/secop_muestra.csv` | Muestra descargada de datos.gov.co |

## Cómo correr

Desde esta carpeta (`ml/`):

```bash
python entrenar.py          # descarga (si hace falta) + compara 7 modelos
python exportar_modelo.py   # exporta el ganador al joblib de la API
```

Requisitos: `pandas`, `scikit-learn==1.8.0`, `joblib`, `numpy`.

## Qué explicar en el video

1. `descargar()` / `preparar()` en `entrenar.py`
2. `candidatos()` — los 7 pipelines
3. `main()` — CV → selección → prueba → búsqueda coseno
4. `exportar_modelo.py` — joblib para producción
5. `../api/app/` — ejecución en la nube (ya no entrena)
