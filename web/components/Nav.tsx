"use client";

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
    <nav className="nav" aria-label="Secciones">
      <a className="nav-brand" href="#top">
        SECOP II
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
