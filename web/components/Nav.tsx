"use client";

import Image from "next/image";

const LINKS = [
  { href: "#demo", label: "Demo" },
  { href: "#problema", label: "Problema" },
  { href: "#fuente", label: "Fuente" },
  { href: "#pipeline", label: "Pipeline" },
  { href: "#resultados", label: "Resultados" },
  { href: "#problemas", label: "Problemas" },
  { href: "#curso", label: "Curso" },
];

export function Nav() {
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
      <div className="nav-links">
        {LINKS.map((l) => (
          <a key={l.href} href={l.href}>
            {l.label}
          </a>
        ))}
      </div>
    </nav>
  );
}
