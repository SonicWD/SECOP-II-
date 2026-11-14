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
};

type PipelineData = {
  pipeline: { paso: number; nombre: string; detalle: string }[];
  problemas: { problema: string; solucion: string }[];
};

function fmt(n: number | null | undefined, d = 3) {
  if (n == null) return "—";
  return n.toFixed(d).replace(".", ",");
}

export function Secciones() {
  const [meta, setMeta] = useState<Meta | null>(null);
  const [res, setRes] = useState<Resultados | null>(null);
  const [pipe, setPipe] = useState<PipelineData | null>(null);

  useEffect(() => {
    Promise.all([
      fetch("/api/meta").then((r) => r.json()),
      fetch("/api/resultados").then((r) => r.json()),
      fetch("/api/pipeline").then((r) => r.json()),
    ])
      .then(([m, r, p]) => {
        setMeta(m);
        setRes(r);
        setPipe(p);
      })
      .catch(() => undefined);
  }, []);

  return (
    <>
      <section className="panel" id="problema" aria-labelledby="problema-titulo">
        <h2 id="problema-titulo">Problemática y solución</h2>
        <div className="dos">
          <div>
            <h3 className="subh">Problemática</h3>
            <p>
              SECOP II publica millones de procesos en texto libre. Quien busca un bien o
              servicio rara vez conoce el código UNSPSC. La búsqueda por palabras sueltas
              mezcla obras, suministros y servicios que comparten los mismos verbos.
            </p>
          </div>
          <div>
            <h3 className="subh">Solución</h3>
            <p>
              Clasificar el segmento UNSPSC desde el nombre y la descripción, medir con F1
              macro, y recuperar vecinos por distancia de coseno sobre el mismo TF-IDF. El
              código no entra como variable (sin leakage).
            </p>
          </div>
        </div>
      </section>

      <section className="panel" id="fuente" aria-labelledby="fuente-titulo">
        <h2 id="fuente-titulo">Fuente de información</h2>
        <p>
          <a
            href={meta?.fuente || "https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt"}
            target="_blank"
            rel="noreferrer"
          >
            SECOP II – Procesos de Contratación
          </a>{" "}
          (datos.gov.co, p6dx-8zbt). API SODA pública, sin token.
        </p>
        {meta?.muestra ? (
          <dl className="meta grid-4" style={{ marginTop: "1rem" }}>
            <div>
              <dt>Descargadas</dt>
              <dd>{meta.muestra.filas_descargadas?.toLocaleString("es-CO") ?? "—"}</dd>
            </div>
            <div>
              <dt>Modeladas</dt>
              <dd>{meta.muestra.filas_modelo?.toLocaleString("es-CO") ?? "—"}</dd>
            </div>
            <div>
              <dt>Clases</dt>
              <dd>{meta.muestra.n_clases ?? "—"}</dd>
            </div>
            <div>
              <dt>Vocabulario</dt>
              <dd>{meta.muestra.vocabulario?.toLocaleString("es-CO") ?? "—"}</dd>
            </div>
          </dl>
        ) : null}
      </section>

      <section className="panel" id="pipeline" aria-labelledby="pipeline-titulo">
        <h2 id="pipeline-titulo">Pipeline</h2>
        <div className="pipeline">
          {(pipe?.pipeline || []).map((p) => (
            <div className="paso" key={p.paso} title={p.detalle}>
              <span>{String(p.paso).padStart(2, "0")}</span>
              <strong>{p.nombre}</strong>
            </div>
          ))}
        </div>
        <p className="hint" style={{ marginTop: "1rem" }}>
          {meta?.criterio || "El F1 macro de validación cruzada decide el modelo; la prueba solo informa."}
        </p>
      </section>

      <section className="panel" id="resultados" aria-labelledby="resultados-titulo">
        <h2 id="resultados-titulo">Resultados obtenidos</h2>
        {meta?.metricas_referencia ? (
          <dl className="meta grid-4" style={{ marginBottom: "1.25rem" }}>
            <div>
              <dt>F1 macro prueba</dt>
              <dd>{fmt(meta.metricas_referencia.f1_macro_prueba)}</dd>
            </div>
            <div>
              <dt>Exactitud</dt>
              <dd>{fmt(meta.metricas_referencia.exactitud_prueba)}</dd>
            </div>
            <div>
              <dt>Recall@5</dt>
              <dd>{fmt(meta.metricas_referencia.recall_at_5)}</dd>
            </div>
            <div>
              <dt>MRR@5</dt>
              <dd>{fmt(meta.metricas_referencia.mrr_at_5)}</dd>
            </div>
          </dl>
        ) : null}
        {res?.modelos?.length ? (
          <div className="tabla-wrap">
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
          <div>
            <h3 className="subh">Mejores F1 por segmento</h3>
            <ul className="lista">
              {(res?.por_clase_mejores || []).map((c) => (
                <li key={c.segmento}>
                  <strong>{c.segmento}</strong> {c.nombre} · F1 {fmt(c.f1)}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="subh">Peores F1 por segmento</h3>
            <ul className="lista">
              {(res?.por_clase_peores || []).map((c) => (
                <li key={c.segmento}>
                  <strong>{c.segmento}</strong> {c.nombre} · F1 {fmt(c.f1)}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="panel" id="problemas" aria-labelledby="problemas-titulo">
        <h2 id="problemas-titulo">Problemas y soluciones</h2>
        <div className="cards">
          {(pipe?.problemas || []).map((p) => (
            <article className="card" key={p.problema}>
              <h3 className="subh">{p.problema}</h3>
              <p>{p.solucion}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="panel" id="curso" aria-labelledby="curso-titulo">
        <h2 id="curso-titulo">Línea de la asignatura</h2>
        <p className="lead">
          El proyecto final reutiliza lo visto en los REA anteriores: limpieza y TF-IDF,
          embeddings/LSA, pipeline reproducible y métricas honestas.
        </p>
        <div className="cards">
          {(meta?.linea_curso || []).map((l) => (
            <article className="card" key={l.rea}>
              <h3 className="subh">{l.rea}</h3>
              <p>{l.aporte}</p>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}
