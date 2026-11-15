# -*- coding: utf-8 -*-
"""Clasificación del objeto contractual en SECOP II.

Muestra pública de Procesos de Contratación (datos.gov.co, p6dx-8zbt).
La etiqueta es el segmento UNSPSC (dos primeros dígitos del código de categoría).
El texto es el nombre y la descripción. El código no entra como variable.
La elección del modelo usa el F1 macro de validación cruzada; la prueba queda aparte.
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.decomposition import TruncatedSVD
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.naive_bayes import ComplementNB, MultinomialNB
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

BASE = Path(__file__).resolve().parent
RAW = BASE / "data" / "secop_muestra.csv"
OUT = BASE / "resultados.json"

SEGMENTOS = {
    "10": "Material vivo vegetal y animal",
    "11": "Material mineral y textil",
    "12": "Químicos y gases",
    "13": "Resinas, cauchos y espumas",
    "14": "Papel y productos de papel",
    "15": "Combustibles y lubricantes",
    "20": "Maquinaria de minería",
    "21": "Maquinaria agrícola",
    "22": "Maquinaria de construcción",
    "23": "Maquinaria industrial",
    "24": "Manejo de materiales",
    "25": "Vehículos comerciales",
    "26": "Componentes de transmisión",
    "27": "Herramientas y maquinaria general",
    "30": "Componentes estructurales",
    "31": "Componentes de manufactura",
    "32": "Componentes electrónicos",
    "39": "Sistemas eléctricos e iluminación",
    "40": "Climatización y distribución de fluidos",
    "41": "Equipo de laboratorio",
    "42": "Equipo médico",
    "43": "Tecnologías de la información",
    "44": "Oficina y papelería",
    "45": "Impresión y fotografía",
    "46": "Seguridad y orden público",
    "47": "Limpieza y aseo",
    "48": "Servicio de alimentos",
    "49": "Deporte y recreación",
    "50": "Alimentos y bebidas",
    "51": "Medicamentos y productos farmacéuticos",
    "52": "Electrodomésticos y electrónicos de consumo",
    "53": "Ropa y cuidado personal",
    "54": "Relojería y joyería",
    "55": "Publicaciones",
    "56": "Muebles y mobiliario",
    "60": "Instrumentos musicales, juegos y artes",
    "70": "Servicios de agricultura, pesca y silvicultura",
    "71": "Minería y perforación",
    "72": "Edificación y construcción",
    "73": "Producción industrial",
    "76": "Limpieza industrial",
    "77": "Servicios ambientales",
    "78": "Transporte, almacenamiento y correo",
    "80": "Servicios de gestión y administrativos",
    "81": "Ingeniería, investigación y tecnología",
    "82": "Servicios editoriales y de diseño",
    "83": "Servicios públicos y saneamiento",
    "84": "Servicios financieros y de seguros",
    "85": "Servicios de salud",
    "86": "Servicios educativos y de capacitación",
    "90": "Viajes, alimentación y entretenimiento",
    "91": "Servicios personales y domésticos",
    "92": "Defensa nacional y orden público",
    "93": "Política y asuntos cívicos",
    "94": "Organizaciones y clubes",
    "95": "Terrenos, edificios y estructuras",
}

STOP = {
    "a", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con", "contra",
    "cual", "cuando", "de", "del", "desde", "donde", "durante", "e", "el", "ella",
    "ellas", "ellos", "en", "entre", "era", "es", "esa", "esas", "ese", "eso", "esos",
    "esta", "estas", "este", "esto", "estos", "ha", "han", "hasta", "la", "las", "le",
    "les", "lo", "los", "mas", "más", "me", "mi", "mis", "mucho", "muy", "no", "nos",
    "o", "para", "pero", "por", "que", "se", "ser", "si", "sin", "sobre", "su", "sus",
    "te", "un", "una", "uno", "y", "ya", "the", "of", "and",
}

UA = {"User-Agent": "Mozilla/5.0 (compatible; ucundinamarca-pln/1.0)"}
PAGINAS = 4
POR_PAGINA = 8000
MIN_CLASE = 80
TOPE_CLASE = 700
SEMILLA = 42


def _get(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def universo() -> list[dict]:
    url = "https://www.datos.gov.co/resource/p6dx-8zbt.json?" + urllib.parse.urlencode({
        "$select": "tipo_de_contrato, count(*) as n",
        "$group": "tipo_de_contrato",
        "$order": "n DESC",
        "$limit": 40,
    })
    return json.loads(_get(url))


def fechas_de_la_ventana() -> tuple[str | None, str | None]:
    def una(offset: int) -> str | None:
        url = "https://www.datos.gov.co/resource/p6dx-8zbt.json?" + urllib.parse.urlencode({
            "$select": "fecha_de_publicacion_del",
            "$where": (
                "descripci_n_del_procedimiento IS NOT NULL "
                "AND codigo_principal_de_categoria IS NOT NULL"
            ),
            "$order": "fecha_de_publicacion_del DESC",
            "$limit": 1,
            "$offset": offset,
        })
        filas = json.loads(_get(url))
        if not filas:
            return None
        return str(filas[0].get("fecha_de_publicacion_del", ""))[:10] or None

    try:
        reciente = una(0)
        antigua = una(PAGINAS * POR_PAGINA - 1)
        return antigua, reciente
    except Exception as exc:
        print("fechas no disponibles", exc, flush=True)
        return None, None


def descargar() -> pd.DataFrame:
    if RAW.exists() and RAW.stat().st_size > 1000:
        return pd.read_csv(RAW)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    frames = []
    campos = ",".join([
        "nombre_del_procedimiento",
        "descripci_n_del_procedimiento",
        "codigo_principal_de_categoria",
        "tipo_de_contrato",
        "modalidad_de_contratacion",
        "fecha_de_publicacion_del",
        "departamento_entidad",
        "ciudad_entidad",
    ])
    where = (
        "descripci_n_del_procedimiento IS NOT NULL "
        "AND codigo_principal_de_categoria IS NOT NULL"
    )
    for i in range(PAGINAS):
        url = "https://www.datos.gov.co/resource/p6dx-8zbt.csv?" + urllib.parse.urlencode({
            "$select": campos,
            "$where": where,
            "$order": "fecha_de_publicacion_del DESC",
            "$limit": POR_PAGINA,
            "$offset": i * POR_PAGINA,
        })
        print(f"descarga pagina {i + 1}/{PAGINAS}", flush=True)
        frames.append(pd.read_csv(url, encoding="utf-8"))
        time.sleep(0.4)
    df = pd.concat(frames, ignore_index=True)
    df.to_csv(RAW, index=False)
    return df


def segmento(codigo: str) -> str | None:
    # El valor llega como V1.80111600: el 1 es la versión y el código es el bloque de 8 dígitos.
    hallados = re.findall(r"\d{8}", str(codigo))
    if not hallados:
        return None
    return hallados[-1][:2]


def preparar(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["texto"] = (
        out["nombre_del_procedimiento"].fillna("").astype(str)
        + " "
        + out["descripci_n_del_procedimiento"].fillna("").astype(str)
    )
    out["texto"] = out["texto"].str.replace(r"https?://\S+", " ", regex=True)
    out["texto"] = out["texto"].str.replace(r"\s+", " ", regex=True).str.strip()
    out["segmento"] = out["codigo_principal_de_categoria"].map(segmento)
    out = out[out["segmento"].notna() & (out["texto"].str.len() >= 40)]
    conteo = out["segmento"].value_counts()
    validos = conteo[conteo >= MIN_CLASE].index
    out = out[out["segmento"].isin(validos)]
    partes = []
    rng = np.random.default_rng(SEMILLA)
    for codigo, grupo in out.groupby("segmento"):
        if len(grupo) > TOPE_CLASE:
            idx = rng.choice(grupo.index.to_numpy(), size=TOPE_CLASE, replace=False)
            grupo = grupo.loc[idx]
        partes.append(grupo)
        _ = codigo
    return pd.concat(partes, ignore_index=True)


def vectorizador() -> TfidfVectorizer:
    return TfidfVectorizer(
        lowercase=True,
        stop_words=list(STOP),
        token_pattern=r"(?u)\b[a-záéíóúüñ]{3,}\b",
        ngram_range=(1, 2),
        min_df=3,
        max_df=0.95,
        max_features=20000,
        sublinear_tf=True,
    )


def candidatos() -> dict[str, Pipeline]:
    def tubo(modelo) -> Pipeline:
        return Pipeline([("tfidf", vectorizador()), ("modelo", modelo)])

    return {
        "Base (clase mayoritaria)": Pipeline([
            ("tfidf", vectorizador()),
            ("modelo", DummyClassifier(strategy="most_frequent")),
        ]),
        "Naive Bayes multinomial": tubo(MultinomialNB(alpha=0.1)),
        "Naive Bayes complementario": tubo(ComplementNB(alpha=0.1)),
        "Regresión logística C=1": tubo(LogisticRegression(
            C=1.0, class_weight="balanced", max_iter=400, solver="saga", random_state=SEMILLA,
        )),
        "Regresión logística C=4": tubo(LogisticRegression(
            C=4.0, class_weight="balanced", max_iter=400, solver="saga", random_state=SEMILLA,
        )),
        "SVM lineal": tubo(LinearSVC(
            C=1.0, class_weight="balanced", dual="auto", random_state=SEMILLA,
        )),
        "LSA 100 + logística": Pipeline([
            ("tfidf", vectorizador()),
            ("svd", TruncatedSVD(n_components=100, random_state=SEMILLA)),
            ("modelo", LogisticRegression(
                C=1.0, class_weight="balanced", max_iter=400, solver="lbfgs", random_state=SEMILLA,
            )),
        ]),
    }


def redondear(x: float, n: int = 4) -> float:
    return round(float(x), n)


def buscar(vector, x_train, y_train, x_test, y_test, n_consultas: int = 400) -> dict:
    matriz_tr = vector.transform(x_train)
    matriz_te = vector.transform(x_test)
    nn = NearestNeighbors(n_neighbors=5, metric="cosine")
    nn.fit(matriz_tr)
    rng = np.random.default_rng(SEMILLA)
    n = min(n_consultas, len(x_test))
    idx = rng.choice(len(x_test), size=n, replace=False)
    distancias, vecinos = nn.kneighbors(matriz_te[idx])
    aciertos = 0
    reciproco = 0.0
    for i, fila in enumerate(vecinos):
        etiqueta = y_test[idx[i]]
        hallados = [y_train[j] for j in fila]
        if etiqueta in hallados:
            aciertos += 1
            reciproco += 1.0 / (hallados.index(etiqueta) + 1)
    _ = distancias
    return {
        "consultas": int(n),
        "recall_at_5": redondear(aciertos / n),
        "mrr_at_5": redondear(reciproco / n),
    }


def main() -> None:
    t0 = time.time()
    print("universo", flush=True)
    tipos = universo()
    print("descarga", flush=True)
    crudo = descargar()
    print("filas crudas", len(crudo), flush=True)
    datos = preparar(crudo)
    print("filas modelo", len(datos), "clases", datos["segmento"].nunique(), flush=True)

    x = datos["texto"].to_numpy()
    y = datos["segmento"].to_numpy()
    x_tr, x_te, y_tr, y_te = train_test_split(
        x, y, test_size=0.2, random_state=SEMILLA, stratify=y,
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMILLA)
    modelos = candidatos()
    filas = []
    ajustados = {}
    for nombre, tubo in modelos.items():
        print("cv", nombre, flush=True)
        puntajes = cross_val_score(tubo, x_tr, y_tr, cv=cv, scoring="f1_macro", n_jobs=-1)
        modelo = clone(tubo)
        modelo.fit(x_tr, y_tr)
        pred = modelo.predict(x_te)
        fila = {
            "modelo": nombre,
            "f1_macro_cv": redondear(puntajes.mean()),
            "f1_macro_cv_std": redondear(puntajes.std()),
            "f1_macro_prueba": redondear(f1_score(y_te, pred, average="macro")),
            "f1_ponderado_prueba": redondear(f1_score(y_te, pred, average="weighted")),
            "exactitud_prueba": redondear(accuracy_score(y_te, pred)),
        }
        print(fila, flush=True)
        filas.append(fila)
        ajustados[nombre] = (modelo, pred)

    filas.sort(key=lambda r: r["f1_macro_cv"], reverse=True)
    ganador = filas[0]["modelo"]
    modelo, pred = ajustados[ganador]
    reporte = classification_report(y_te, pred, output_dict=True, zero_division=0)
    por_clase = []
    for codigo, info in reporte.items():
        if codigo in {"accuracy", "macro avg", "weighted avg"}:
            continue
        por_clase.append({
            "segmento": codigo,
            "nombre": SEGMENTOS.get(codigo, f"Segmento {codigo}"),
            "precision": redondear(info["precision"]),
            "recall": redondear(info["recall"]),
            "f1": redondear(info["f1-score"]),
            "soporte": int(info["support"]),
        })
    por_clase.sort(key=lambda r: r["f1"])

    vector = modelo.named_steps["tfidf"]
    busqueda = buscar(vector, x_tr, y_tr, x_te, y_te)
    fechas = pd.to_datetime(datos["fecha_de_publicacion_del"], errors="coerce")
    fecha_min = str(fechas.min().date()) if fechas.notna().any() else None
    fecha_max = str(fechas.max().date()) if fechas.notna().any() else None
    if fecha_min is None:
        print("fechas por API", flush=True)
        fecha_min, fecha_max = fechas_de_la_ventana()
    conteo = (
        datos["segmento"].value_counts()
        .rename_axis("segmento").reset_index(name="n")
    )
    conteo["nombre"] = conteo["segmento"].map(lambda c: SEGMENTOS.get(c, f"Segmento {c}"))

    resultado = {
        "fuente": "https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt",
        "dataset_id": "p6dx-8zbt",
        "universo_por_tipo": tipos,
        "filas_descargadas": int(len(crudo)),
        "filas_modelo": int(len(datos)),
        "n_train": int(len(x_tr)),
        "n_test": int(len(x_te)),
        "n_clases": int(datos["segmento"].nunique()),
        "vocabulario": int(len(vector.vocabulary_)),
        "fecha_min": fecha_min,
        "fecha_max": fecha_max,
        "texto_mediana_caracteres": int(datos["texto"].str.len().median()),
        "departamentos": int(datos["departamento_entidad"].nunique()),
        "clases": conteo.to_dict(orient="records"),
        "modelos_probados": len(filas),
        "criterio": "F1 macro medio de validación cruzada de cinco pliegues sobre el entrenamiento",
        "modelo_seleccionado": ganador,
        "resultados": filas,
        "por_clase_peores": por_clase[:5],
        "por_clase_mejores": list(reversed(por_clase[-5:])),
        "busqueda": busqueda,
        "segundos": redondear(time.time() - t0, 1),
        "semilla": SEMILLA,
        "min_clase": MIN_CLASE,
        "tope_clase": TOPE_CLASE,
    }
    OUT.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print("LISTO", ganador, "en", resultado["segundos"], "s", flush=True)
    print(OUT)


if __name__ == "__main__":
    main()
