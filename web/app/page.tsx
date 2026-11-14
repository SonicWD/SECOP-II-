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
          <div>
            <div className="hero-marcas">
              <Image
                className="hero-logo"
                src="/logos/udec-horizontal.png"
                alt="Universidad de Cundinamarca"
                width={220}
                height={103}
                priority
              />
              <Image
                className="hero-escudo"
                src="/logos/udec-escudo.png"
                alt=""
                width={56}
                height={84}
                aria-hidden
              />
            </div>
            <p className="eyebrow">PLN · Proyecto final · Extensión Fusagasugá</p>
            <h1>SECOP II — Clasificación y búsqueda</h1>
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

        <div id="contenido">
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
              width={32}
              height={48}
              aria-hidden
            />
            <p>
              Wilson Alfonso Díaz Capador · Especialización en Inteligencia Artificial ·
              Universidad de Cundinamarca
            </p>
          </div>
          <p>
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
          </p>
        </footer>
      </main>
    </>
  );
}
