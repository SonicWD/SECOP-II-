"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

const LINKS = [
  { id: "demo", label: "Demo" },
  { id: "problema", label: "Problema" },
  { id: "fuente", label: "Fuente" },
  { id: "pipeline", label: "Pipeline" },
  { id: "resultados", label: "Resultados" },
  { id: "problemas", label: "Problemas" },
  { id: "curso", label: "Curso" },
] as const;

type SeccionId = (typeof LINKS)[number]["id"];

function esSeccion(id: string): id is SeccionId {
  return LINKS.some((l) => l.id === id);
}

export function Nav() {
  const [activa, setActiva] = useState<SeccionId>("demo");

  useEffect(() => {
    const ids = LINKS.map((l) => l.id);
    const nodos = ids
      .map((id) => document.getElementById(id))
      .filter((el): el is HTMLElement => Boolean(el));

    if (!nodos.length) return;

    const visto = new Map<SeccionId, number>();

    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (esSeccion(entry.target.id)) {
            visto.set(entry.target.id, entry.intersectionRatio);
          }
        }
        let mejor: SeccionId = ids[0];
        let ratio = -1;
        for (const id of ids) {
          const r = visto.get(id) ?? 0;
          if (r > ratio) {
            ratio = r;
            mejor = id;
          }
        }
        // Si casi nada está visible, usar la más cercana al tope del viewport.
        if (ratio < 0.08) {
          const ancla = window.scrollY + 120;
          let cercana: SeccionId = ids[0];
          let dist = Number.POSITIVE_INFINITY;
          for (const el of nodos) {
            if (!esSeccion(el.id)) continue;
            const d = Math.abs(el.offsetTop - ancla);
            if (d < dist) {
              dist = d;
              cercana = el.id;
            }
          }
          setActiva(cercana);
          return;
        }
        setActiva(mejor);
      },
      {
        root: null,
        // Compensa el header sticky
        rootMargin: "-20% 0px -55% 0px",
        threshold: [0, 0.1, 0.25, 0.5, 0.75, 1],
      },
    );

    for (const el of nodos) observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <nav className="nav" aria-label="Secciones del proyecto">
      <a className="nav-brand" href="#top">
        <Image
          className="nav-escudo"
          src="/logos/udec-escudo.png"
          alt=""
          width={30}
          height={45}
          aria-hidden
        />
        <span className="nav-sigla">SECOP II</span>
        <span className="solo-lector">Inicio · Universidad de Cundinamarca</span>
      </a>
      <div className="nav-links" role="list">
        {LINKS.map((l) => {
          const selected = activa === l.id;
          return (
            <a
              key={l.id}
              href={`#${l.id}`}
              role="listitem"
              className={selected ? "nav-link is-active" : "nav-link"}
              aria-current={selected ? "location" : undefined}
              onClick={() => setActiva(l.id)}
            >
              {l.label}
            </a>
          );
        })}
      </div>
    </nav>
  );
}
