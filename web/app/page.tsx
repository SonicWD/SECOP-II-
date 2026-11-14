import { Consola } from "@/components/Consola";

export default function Home() {
  return (
    <main className="shell">
      <header className="hero">
        <div>
          <p className="eyebrow">PLN · Proyecto final · UCundinamarca</p>
          <h1>SECOP II — Clasificación y búsqueda</h1>
          <p>
            Asigna el segmento UNSPSC a partir del texto público del proceso y recupera
            contratos parecidos. Modelo: regresión logística C=4 sobre TF-IDF.
          </p>
        </div>
        <dl className="meta">
          <div>
            <dt>F1 macro (prueba)</dt>
            <dd>0,506</dd>
          </div>
          <div>
            <dt>Exactitud</dt>
            <dd>0,561</dd>
          </div>
          <div>
            <dt>Recall@5</dt>
            <dd>0,698</dd>
          </div>
          <div>
            <dt>Fuente</dt>
            <dd>datos.gov.co · p6dx-8zbt</dd>
          </div>
        </dl>
      </header>

      <section aria-labelledby="pipeline-titulo">
        <h2 id="pipeline-titulo" className="eyebrow" style={{ color: "var(--apagado)" }}>
          Pipeline
        </h2>
        <div className="pipeline">
          {[
            ["01", "API SECOP"],
            ["02", "Limpieza"],
            ["03", "UNSPSC"],
            ["04", "TF-IDF"],
            ["05", "CV 5 folds"],
            ["06", "Logística"],
            ["07", "UI / API"],
          ].map(([n, t]) => (
            <div className="paso" key={n}>
              <span>{n}</span>
              <strong>{t}</strong>
            </div>
          ))}
        </div>
      </section>

      <div style={{ marginBlockStart: "2rem" }}>
        <Consola />
      </div>

      <footer className="pie">
        Wilson Alfonso Díaz Capador · Especialización en Inteligencia Artificial ·{" "}
        <a href="https://github.com/SonicWD/SECOP-II-" rel="noreferrer" target="_blank">
          GitHub
        </a>
        {" · "}
        <a href="/api/health" rel="noreferrer">
          API health
        </a>
      </footer>
    </main>
  );
}
