import Image from "next/image";
import { Consola } from "@/components/Consola";
import { Nav } from "@/components/Nav";
import { Secciones } from "@/components/Secciones";

export default function Home() {
  return (
    <>
      <a className="skip" href="#contenido">
        Saltar al contenido
      </a>
      <Nav />
      <main className="shell" id="top">
        <header className="hero">
          <div className="hero-copy">
            <Image
              className="hero-logo"
              src="/logos/udec-horizontal.png"
              alt="Universidad de Cundinamarca"
              width={240}
              height={112}
              priority
            />
            <p className="eyebrow">PLN · Proyecto final · Extensión Fusagasugá</p>
            <h1>Clasifica y busca procesos de SECOP II</h1>
            <p>
              Interfaz y API en la nube: predice el segmento UNSPSC desde el texto público
              y recupera contratos parecidos con TF-IDF y distancia de coseno.
            </p>
            <div className="hero-cta">
              <a className="btn" href="#demo">
                Probar el modelo
              </a>
              <a className="btn btn-ghost" href="#resultados">
                Ver resultados
              </a>
            </div>
          </div>
          <aside className="hero-stats" aria-label="Métricas del modelo">
            <div className="stat">
              <span className="stat-val">0,506</span>
              <span className="stat-label">F1 macro</span>
            </div>
            <div className="stat">
              <span className="stat-val">0,561</span>
              <span className="stat-label">Exactitud</span>
            </div>
            <div className="stat">
              <span className="stat-val">0,698</span>
              <span className="stat-label">Recall@5</span>
            </div>
            <div className="stat">
              <span className="stat-val">7</span>
              <span className="stat-label">Modelos</span>
            </div>
          </aside>
        </header>

        <div id="contenido" className="contenido">
          <Consola />
          <div className="stack">
            <Secciones />
          </div>
        </div>

        <footer className="pie">
          <div className="pie-marca">
            <Image
              src="/logos/udec-escudo.png"
              alt=""
              width={36}
              height={54}
              aria-hidden
            />
            <p>
              Wilson Alfonso Díaz Capador · Especialización en Inteligencia Artificial ·
              Universidad de Cundinamarca
            </p>
          </div>
          <p className="pie-links">
            <a href="https://github.com/SonicWD/SECOP-II-" rel="noreferrer" target="_blank">
              GitHub
            </a>
            {" · "}
            <a href="/api/health">API</a>
            {" · "}
            <a href="/docs" target="_blank" rel="noreferrer">
              OpenAPI
            </a>
          </p>
        </footer>
      </main>
    </>
  );
}
