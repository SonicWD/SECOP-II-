"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "motion/react";

type Ejemplo = { id: string; titulo: string; texto: string };
type Ranking = { codigo: string; nombre: string; probabilidad: number | null };
type Termino = { termino: string; tfidf: number; aporte: number };
type Vecino = {
  rango: number;
  segmento: string;
  nombre: string;
  similitud: number;
  extracto: string;
};

export function Consola() {
  const [tab, setTab] = useState<"clasificar" | "buscar" | "limpiar">("clasificar");
  const [texto, setTexto] = useState("");
  const [ejemplos, setEjemplos] = useState<Ejemplo[]>([]);
  const [touched, setTouched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pred, setPred] = useState<{
    segmento: string;
    nombre: string;
    ranking: Ranking[];
    terminos_clave: Termino[];
  } | null>(null);
  const [vecinos, setVecinos] = useState<Vecino[] | null>(null);
  const [limpieza, setLimpieza] = useState<{
    limpio: string;
    caracteres: number;
    tokens_aprox: number;
    urls_retiradas: number;
    apto_modelo: boolean;
  } | null>(null);

  useEffect(() => {
    fetch("/api/ejemplos")
      .then((r) => r.json())
      .then((d) => {
        setEjemplos(d.ejemplos || []);
        if (d.ejemplos?.[0]) setTexto(d.ejemplos[0].texto);
      })
      .catch(() => {
        const fallback =
          "Prestación de servicios profesionales de apoyo a la gestión para el mantenimiento preventivo y correctivo de equipos de cómputo e impresoras en las sedes de la entidad.";
        setTexto(fallback);
      });
  }, []);

  const corto = texto.trim().length > 0 && texto.trim().length < 20;
  const invalido = touched && corto;

  async function clasificar() {
    setTouched(true);
    setError(null);
    setVecinos(null);
    setLimpieza(null);
    if (texto.trim().length < 20) {
      setError("Escribe al menos 20 caracteres del objeto contractual.");
      queueMicrotask(() => document.getElementById("objeto")?.focus());
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/clasificar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto: texto.trim(), top_k: 5, explicar: true }),
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(typeof detail.detail === "string" ? detail.detail : "No se pudo clasificar.");
      }
      setPred(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error de red con la API.");
      setPred(null);
    } finally {
      setLoading(false);
    }
  }

  async function buscar() {
    setTouched(true);
    setError(null);
    setPred(null);
    setLimpieza(null);
    if (texto.trim().length < 20) {
      setError("Escribe al menos 20 caracteres para buscar.");
      queueMicrotask(() => document.getElementById("objeto")?.focus());
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/buscar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ consulta: texto.trim(), k: 5 }),
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(typeof detail.detail === "string" ? detail.detail : "No se pudo buscar.");
      }
      const data = await res.json();
      setVecinos(data.vecinos);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error de red con la API.");
      setVecinos(null);
    } finally {
      setLoading(false);
    }
  }

  async function limpiar() {
    setTouched(true);
    setError(null);
    setPred(null);
    setVecinos(null);
    setLoading(true);
    try {
      const res = await fetch("/api/limpiar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto }),
      });
      if (!res.ok) throw new Error("No se pudo limpiar el texto.");
      setLimpieza(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Error de red.");
      setLimpieza(null);
    } finally {
      setLoading(false);
    }
  }

  function run() {
    if (tab === "clasificar") return clasificar();
    if (tab === "buscar") return buscar();
    return limpiar();
  }

  return (
    <section className="panel panel-demo" id="demo" aria-labelledby="consola-titulo">
      <div className="demo-cabecera">
        <h2 id="consola-titulo">Probar el modelo</h2>
        <p className="lead">
          Clasificación UNSPSC, búsqueda por coseno y limpieza de texto — misma lógica de la
          propuesta.
        </p>
      </div>

      {ejemplos.length > 0 ? (
        <div className="chips" role="list" aria-label="Ejemplos">
          {ejemplos.map((ej) => (
            <button
              key={ej.id}
              type="button"
              className="chip"
              role="listitem"
              onClick={() => {
                setTexto(ej.texto);
                setTouched(false);
                setError(null);
              }}
            >
              {ej.titulo}
            </button>
          ))}
        </div>
      ) : null}

      <div className="tabs" role="tablist" aria-label="Modo">
        {(
          [
            ["clasificar", "Clasificar"],
            ["buscar", "Buscar"],
            ["limpiar", "Limpiar texto"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            className="tab"
            role="tab"
            aria-selected={tab === id}
            onClick={() => setTab(id)}
          >
            {label}
          </button>
        ))}
      </div>

      <label htmlFor="objeto">Texto del proceso</label>
      <textarea
        id="objeto"
        name="objeto"
        value={texto}
        onChange={(e) => setTexto(e.target.value)}
        onBlur={() => setTouched(true)}
        required
        minLength={20}
        autoComplete="off"
        spellCheck={true}
        aria-invalid={invalido || undefined}
        aria-describedby={invalido ? "objeto-error" : "objeto-hint"}
        placeholder="Ej.: suministro de medicamentos para la red hospitalaria…"
      />
      <p id="objeto-hint" className="hint">
        Mínimo 20 caracteres. El código UNSPSC no se escribe: el modelo lo predice.
      </p>
      {invalido ? (
        <p id="objeto-error" className="error" role="alert">
          Aún faltan caracteres para una descripción usable.
        </p>
      ) : null}

      <div className="acciones">
        <button type="button" className="btn" disabled={loading} onClick={() => void run()}>
          {loading
            ? "Procesando…"
            : tab === "clasificar"
              ? "Clasificar segmento"
              : tab === "buscar"
                ? "Buscar similares"
                : "Ver limpieza"}
        </button>
      </div>

      {error ? (
        <p className="error" role="alert">
          {error}
        </p>
      ) : null}

      <AnimatePresence mode="wait">
        {pred ? (
          <motion.div
            key="pred"
            className="resultado"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            <div className="badge" aria-live="polite">
              <span>{pred.segmento}</span>
              <span>{pred.nombre}</span>
            </div>
            <table className="tabla">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Segmento</th>
                  <th>Prob.</th>
                </tr>
              </thead>
              <tbody>
                {pred.ranking.map((r) => (
                  <tr key={r.codigo}>
                    <td>{r.codigo}</td>
                    <td>{r.nombre}</td>
                    <td>{r.probabilidad == null ? "—" : `${(r.probabilidad * 100).toFixed(1)}%`}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {pred.terminos_clave?.length ? (
              <>
                <h3 className="subh">Términos que empujan la clase (TF-IDF × coeficiente)</h3>
                <div className="chips">
                  {pred.terminos_clave.map((t) => (
                    <span key={t.termino} className="chip chip-static" title={`aporte ${t.aporte}`}>
                      {t.termino} · {t.aporte.toFixed(3)}
                    </span>
                  ))}
                </div>
              </>
            ) : null}
          </motion.div>
        ) : null}

        {vecinos ? (
          <motion.div
            key="vec"
            className="resultado"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            {vecinos.map((v) => (
              <article key={v.rango} className="vecino">
                <strong>
                  {v.rango}. {v.segmento} — {v.nombre} · sim {v.similitud.toFixed(3)}
                </strong>
                <p>{v.extracto}…</p>
              </article>
            ))}
          </motion.div>
        ) : null}

        {limpieza ? (
          <motion.div
            key="lim"
            className="resultado"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            <dl className="meta grid-4">
              <div>
                <dt>Caracteres</dt>
                <dd>{limpieza.caracteres}</dd>
              </div>
              <div>
                <dt>Tokens ≈</dt>
                <dd>{limpieza.tokens_aprox}</dd>
              </div>
              <div>
                <dt>URLs quitadas</dt>
                <dd>{limpieza.urls_retiradas}</dd>
              </div>
              <div>
                <dt>Apto modelo</dt>
                <dd>{limpieza.apto_modelo ? "Sí" : "No"}</dd>
              </div>
            </dl>
            <p className="hint">Texto limpio</p>
            <p className="vecino">{limpieza.limpio}</p>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </section>
  );
}
