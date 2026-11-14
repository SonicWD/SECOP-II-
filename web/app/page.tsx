import { Consola } from "@/components/Consola";
import { Nav } from "@/components/Nav";
import { Secciones } from "@/components/Secciones";

export default function Home() {
  return (
    <>
      <Nav />
      <main className="shell" id="top">
        <header className="hero">
          <div>
            <p className="eyebrow">PLN · Proyecto final · UCundinamarca</p>
            <h1>SECOP II — Clasificación y búsqueda</h1>
            <p>
              Modelo en la nube con interfaz y API: asigna el segmento UNSPSC desde el
              texto público y recupera procesos parecidos. Integra TF-IDF, validación
              cruzada y búsqueda por coseno trabajados en la asignatura.
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
              <dt>Modelos comparados</dt>
              <dd>7</dd>
            </div>
          </dl>
        </header>

        <Consola />

        <div className="stack">
          <Secciones />
        </div>

        <footer className="pie">
          Wilson Alfonso Díaz Capador · Especialización en Inteligencia Artificial ·{" "}
          <a href="https://github.com/SonicWD/SECOP-II-" rel="noreferrer" target="_blank">
            GitHub
          </a>
          {" · "}
          <a href="/api/health">API</a>
          {" · "}
          <a href="/api/meta">Meta</a>
          {" · "}
          <a href="/docs" target="_blank" rel="noreferrer">
            OpenAPI
          </a>
        </footer>
      </main>
    </>
  );
}
