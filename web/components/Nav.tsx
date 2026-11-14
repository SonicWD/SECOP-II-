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
          width={28}
          height={42}
          aria-hidden
        />
        <span className="nav-brand-text">
          <span className="nav-sigla">SECOP II</span>
          <span className="nav-inst">Universidad de Cundinamarca</span>
        </span>
        <span className="solo-lector">Ir al inicio · Universidad de Cundinamarca</span>
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
