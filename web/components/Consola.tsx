"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";

const EJEMPLO =
  "Prestación de servicios profesionales de apoyo a la gestión para el mantenimiento preventivo y correctivo de equipos de cómputo e impresoras en las sedes de la entidad.";

type Ranking = { codigo: string; nombre: string; probabilidad: number | null };
type Vecino = {
  rango: number;
  segmento: string;
  nombre: string;
  similitud: number;
  extracto: string;
};

export function Consola() {
  const [tab, setTab] = useState<"clasificar" | "buscar">("clasificar");
  const [texto, setTexto] = useState(EJEMPLO);
  const [touched, setTouched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pred, setPred] = useState<{ segmento: string; nombre: string; ranking: Ranking[] } | null>(null);
  const [vecinos, setVecinos] = useState<Vecino[] | null>(null);

  const corto = texto.trim().length > 0 && texto.trim().length < 20;
  const invalido = touched && corto;

  async function clasificar() {
    setTouched(true);
    setError(null);
    setVecinos(null);
    if (texto.trim().length < 20) {
      setError("Escribe al menos 20 caracteres del objeto contractual.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/clasificar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto: texto.trim(), top_k: 5 }),
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        throw new Error(detail.detail || "No se pudo clasificar.");
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
    if (texto.trim().length < 20) {
      setError("Escribe al menos 20 caracteres para buscar.");
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
        throw new Error(detail.detail || "No se pudo buscar.");
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

  return (
    <section className="panel" aria-labelledby="consola-titulo">
      <h2 id="consola-titulo" style={{ fontSize: "1.25rem", marginBottom: "0.75rem" }}>
        Probar el modelo
      </h2>
      <div className="tabs" role="tablist" aria-label="Modo">
        <button
          type="button"
          className="tab"
          role="tab"
          aria-selected={tab === "clasificar"}
          onClick={() => setTab("clasificar")}
        >
          Clasificar
        </button>
        <button
          type="button"
          className="tab"
          role="tab"
          aria-selected={tab === "buscar"}
          onClick={() => setTab("buscar")}
        >
          Buscar
        </button>
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
        aria-invalid={invalido || undefined}
        aria-describedby={invalido ? "objeto-error" : "objeto-hint"}
        placeholder="Nombre y descripción del proceso de contratación…"
      />
      <p id="objeto-hint" className="hint" style={{ marginTop: "0.5rem" }}>
        Mínimo 20 caracteres. El código UNSPSC no se escribe aquí: el modelo lo predice.
      </p>
      {invalido ? (
        <p id="objeto-error" className="error" role="alert">
          Aún faltan caracteres para una descripción usable.
        </p>
      ) : null}

      <div className="acciones">
        <button
          type="button"
          className="btn"
          disabled={loading}
          onClick={() => (tab === "clasificar" ? clasificar() : buscar())}
        >
          {loading ? "Procesando…" : tab === "clasificar" ? "Clasificar segmento" : "Buscar similares"}
        </button>
        <button
          type="button"
          className="btn btn-ghost"
          onClick={() => {
            setTexto(EJEMPLO);
            setTouched(false);
            setError(null);
          }}
        >
          Restaurar ejemplo
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
      </AnimatePresence>
    </section>
  );
}
