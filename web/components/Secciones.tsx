"use client";

import { useEffect, useState } from "react";

type Meta = {
  proyecto: string;
  autor: string;
  metricas_referencia: Record<string, number>;
  muestra: Record<string, number | null>;
  linea_curso: { rea: string; aporte: string }[];
  criterio?: string;
  fuente?: string;
  seleccion_modelo?: Seleccion;
};

type Seleccion = {
  modelo_seleccionado: string;
  modelos_probados: number;
  criterio: string;
  desempeno: Record<string, number>;
  metricas_usadas: string[];
  herramientas: string[];
  modelos_comparados: string[];
};

type Resultados = {
  modelo_seleccionado: string;
  modelos: {
    modelo: string;
    f1_macro_cv: number;
    f1_macro_prueba: number;
    exactitud_prueba: number;
  }[];
  por_clase_mejores: { segmento: string; nombre: string; f1: number; soporte: number }[];
  por_clase_peores: { segmento: string; nombre: string; f1: number; soporte: number }[];
  busqueda: { recall_at_5: number; mrr_at_5: number; consultas: number };
  modelos_probados?: number;
};

type PipelineData = {
  pipeline: { paso: number; nombre: string; detalle: string }[];
  problemas: { problema: string; solucion: string }[];
  componentes?: { id: string; nombre: string; rol: string }[];
  seleccion?: Seleccion;
};

type Diseno = {
  componentes: { id: string; nombre: string; rol: string }[];
  fuente: { nombre: string; url: string; acceso: string; etiqueta: string };
};

const TINTAS = ["tile-vino", "tile-ambar", "tile-miel", "tile-piedra"] as const;

function fmt(n: number | null | undefined, d = 3) {
  if (n == null) return "—";
  return n.toFixed(d).replace(".", ",");
}

export function Secciones() {
  const [meta, setMeta] = useState<Meta | null>(null);
  const [res, setRes] = useState<Resultados | null>(null);
  const [pipe, setPipe] = useState<PipelineData | null>(null);
  const [diseno, setDiseno] = useState<Diseno | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/meta").then((r) => r.json()),
      fetch("/api/resultados").then((r) => r.json()),
      fetch("/api/pipeline").then((r) => r.json()),
      fetch("/api/diseno").then((r) => r.json()),
    ])
      .then(([m, r, p, d]) => {
        setMeta(m);
        setRes(r);
        setPipe(p);
        setDiseno(d);
      })
      .catch(() => undefined);
  }, []);

  const seleccion = meta?.seleccion_modelo || pipe?.seleccion;

  return (
    <>
      <section className="panel panel-vino" id="problema" aria-labelledby="problema-titulo">
        <h2 id="problema-titulo">Problemática y solución</h2>
        <div className="dos">
          <article className="tile tile-vino">
            <h3 className="tile-label">Problemática</h3>
            <p>
              SECOP II publica millones de procesos en texto libre. Quien busca un bien o
              servicio rara vez conoce el código UNSPSC. La búsqueda por palabras sueltas
              mezcla obras, suministros y servicios que comparten los mismos verbos.
            </p>
          </article>
          <article className="tile tile-ambar">
            <h3 className="tile-label">Solución</h3>
            <p>
              Clasificar el segmento UNSPSC desde el nombre y la descripción, medir con F1
              macro, y recuperar vecinos por distancia de coseno sobre el mismo TF-IDF. El
              código no entra como variable (sin leakage).
            </p>
          </article>
        </div>
      </section>

      <section className="panel panel-miel" id="fuente" aria-labelledby="fuente-titulo">
        <h2 id="fuente-titulo">Fuente de información</h2>
        <p>
          <a
            href={
              diseno?.fuente?.url ||
              meta?.fuente ||
              "https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt"
            }
            target="_blank"
            rel="noreferrer"
          >
            {diseno?.fuente?.nombre || "SECOP II – Procesos de Contratación"}
          </a>{" "}
          (datos.gov.co, p6dx-8zbt). {diseno?.fuente?.acceso || "API SODA pública, sin token."}
        </p>
        {meta?.muestra ? (
          <div className="metric-grid">
            {[
              ["Descargadas", meta.muestra.filas_descargadas?.toLocaleString("es-CO")],
              ["Modeladas", meta.muestra.filas_modelo?.toLocaleString("es-CO")],
              ["Clases", String(meta.muestra.n_clases ?? "—")],
              ["Vocabulario", meta.muestra.vocabulario?.toLocaleString("es-CO")],
            ].map(([lab, val], i) => (
              <div key={lab} className={`metric-chip ${TINTAS[i % TINTAS.length]}`}>
                <span className="metric-chip-lab">{lab}</span>
                <span className="metric-chip-val">{val ?? "—"}</span>
              </div>
            ))}
          </div>
        ) : null}
      </section>

      <section className="panel panel-ambar" id="diseno" aria-labelledby="diseno-titulo">
        <h2 id="diseno-titulo">Diseño esquemático de componentes</h2>
        <div className="cards">
          {(diseno?.componentes || pipe?.componentes || []).map((c, i) => (
            <article className={`card ${TINTAS[i % TINTAS.length]}`} key={c.id}>
              <h3 className="tile-label">{c.nombre}</h3>
              <p>{c.rol}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="panel panel-ambar" id="pipeline" aria-labelledby="pipeline-titulo">
        <h2 id="pipeline-titulo">Pipeline</h2>
        <div className="pipeline">
          {(pipe?.pipeline || []).map((p, i) => (
            <div
              className={`paso paso-color-${(i % 3) + 1}`}
              key={p.paso}
              title={p.detalle}
            >
              <span>{String(p.paso).padStart(2, "0")}</span>
              <strong>{p.nombre}</strong>
            </div>
          ))}
        </div>
        <p className="hint" style={{ marginTop: "1rem" }}>
          {meta?.criterio ||
            "El F1 macro de validación cruzada decide el modelo; la prueba solo informa."}
        </p>
      </section>

      <section className="panel panel-vino" id="resultados" aria-labelledby="resultados-titulo">
        <h2 id="resultados-titulo">Resultados obtenidos</h2>
        {seleccion ? (
          <div className="dos" style={{ marginBottom: "1.1rem" }}>
            <article className="tile tile-vino">
              <h3 className="tile-label">Modelo seleccionado</h3>
              <p>
                <strong>{seleccion.modelo_seleccionado}</strong>
                <br />
                Se probaron <strong>{seleccion.modelos_probados}</strong> modelos.
                <br />
                Criterio: {seleccion.criterio}
              </p>
            </article>
            <article className="tile tile-ambar">
              <h3 className="tile-label">Desempeño</h3>
              <ul className="lista">
                <li>
                  <strong>F1 CV</strong> {fmt(seleccion.desempeno.f1_macro_cv)}
                </li>
                <li>
                  <strong>F1 prueba</strong> {fmt(seleccion.desempeno.f1_macro_prueba)}
                </li>
                <li>
                  <strong>Exactitud</strong> {fmt(seleccion.desempeno.exactitud_prueba)}
                </li>
                <li>
                  <strong>Recall@5</strong> {fmt(seleccion.desempeno.recall_at_5)}
                </li>
              </ul>
            </article>
          </div>
        ) : null}
        {seleccion?.herramientas?.length ? (
          <div style={{ marginBottom: "1.1rem" }}>
            <p className="subh">Herramientas para elegir el modelo</p>
            <ul className="lista">
              {seleccion.herramientas.map((h) => (
                <li key={h}>{h}</li>
              ))}
            </ul>
          </div>
        ) : null}
        {meta?.metricas_referencia ? (
          <div className="metric-grid">
            {[
              ["F1 macro prueba", fmt(meta.metricas_referencia.f1_macro_prueba)],
              ["Exactitud", fmt(meta.metricas_referencia.exactitud_prueba)],
              ["Recall@5", fmt(meta.metricas_referencia.recall_at_5)],
              ["MRR@5", fmt(meta.metricas_referencia.mrr_at_5)],
            ].map(([lab, val], i) => (
              <div key={lab} className={`metric-chip ${TINTAS[i % TINTAS.length]}`}>
                <span className="metric-chip-lab">{lab}</span>
                <span className="metric-chip-val">{val}</span>
              </div>
            ))}
          </div>
        ) : null}
        {res?.modelos?.length ? (
          <div className="tabla-wrap" style={{ marginTop: "1.1rem" }}>
            <table className="tabla">
              <thead>
                <tr>
                  <th>Modelo</th>
                  <th>F1 CV</th>
                  <th>F1 prueba</th>
                  <th>Exactitud</th>
                </tr>
              </thead>
              <tbody>
                {res.modelos.map((m) => (
                  <tr
                    key={m.modelo}
                    className={m.modelo === res.modelo_seleccionado ? "fila-win" : undefined}
                  >
                    <td>{m.modelo}</td>
                    <td>{fmt(m.f1_macro_cv)}</td>
                    <td>{fmt(m.f1_macro_prueba)}</td>
                    <td>{fmt(m.exactitud_prueba)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
        <div className="dos" style={{ marginTop: "1.25rem" }}>
          <article className="tile tile-ambar">
            <h3 className="tile-label">Mejores F1</h3>
            <ul className="lista">
              {(res?.por_clase_mejores || []).map((c) => (
                <li key={c.segmento}>
                  <strong>{c.segmento}</strong> {c.nombre} · F1 {fmt(c.f1)}
                </li>
              ))}
            </ul>
          </article>
          <article className="tile tile-vino">
            <h3 className="tile-label">Peores F1</h3>
            <ul className="lista">
              {(res?.por_clase_peores || []).map((c) => (
                <li key={c.segmento}>
                  <strong>{c.segmento}</strong> {c.nombre} · F1 {fmt(c.f1)}
                </li>
              ))}
            </ul>
          </article>
        </div>
      </section>

      <section className="panel panel-miel" id="problemas" aria-labelledby="problemas-titulo">
        <h2 id="problemas-titulo">Problemas y soluciones</h2>
        <div className="cards">
          {(pipe?.problemas || []).map((p, i) => (
            <article className={`card ${TINTAS[i % 3]}`} key={p.problema}>
              <h3 className="tile-label">{p.problema}</h3>
              <p>{p.solucion}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="panel panel-ambar" id="curso" aria-labelledby="curso-titulo">
        <h2 id="curso-titulo">Línea de la asignatura</h2>
        <p className="lead">
          El proyecto final reutiliza lo visto en los REA anteriores: limpieza y TF-IDF,
          embeddings/LSA, pipeline reproducible y métricas honestas.
        </p>
        <div className="cards">
          {(meta?.linea_curso || []).map((l, i) => (
            <article className={`card ${TINTAS[i % TINTAS.length]}`} key={l.rea}>
              <h3 className="tile-label">{l.rea}</h3>
              <p>{l.aporte}</p>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}
