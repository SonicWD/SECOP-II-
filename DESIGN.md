# Sistema visual — SECOP II

Identidad **propia**, distinta del ODC (negro + verde institucional).  
Paleta viva inspirada en [3 Sided Cube](https://3sidedcube.com/): energía y contraste sobre blanco/negro.

## Color

| Token | Hex | Uso |
| --- | --- | --- |
| `--verde` | `#31EC56` malaquita | CTA secundaria, tabs activos, acentos |
| `--rosa` | `#EF036C` razzmatazz | Enlaces, foco, métricas |
| `--violeta` | `#EE72F8` heliotropo | Hover suave, chips de explicación |
| `--negro` / `--blanco` | `#0A0A0A` / `#FFFFFF` | Contraste base |

Fondos claros (`#FAFAFA`) con manchas radiales de color, sin el look “terminal oscuro” del ODC.

## Marca UDEC

- **Nav:** solo escudo limpio + “SECOP II” (sin repetir el wordmark).
- **Hero:** solo logo horizontal limpio (incluye escudo lineal + UDEC).
- **Pie:** escudo pequeño + créditos.
- Logos con fondo transparente (`*-clean` aplicados sobre los PNG).

## Tipografía y motion

- Source Serif 4 (títulos) · Source Sans 3 (cuerpo) · IBM Plex Mono (códigos).
- Entrada suave (`opacity` + `translateY`); hover en cards/pasos.
- Respeta `prefers-reduced-motion`.

## Accesibilidad

Skip link, `:focus-visible`, labels, `aria-live`, touch ≥ 44 px, `width`/`height` en imágenes.
