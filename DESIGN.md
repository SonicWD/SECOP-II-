# Sistema visual — SECOP II (identidad propia)

Diseño **distinto** del ODC de grado (que usa lienzo negro + verde `#00d992`).  
Aquí la referencia es un tablero de **datos abiertos / contratación pública**: claro, papel, navy y cian.

## Color

| Variable | Valor | Uso |
| --- | --- | --- |
| `--lienzo` | `#eef2f6` | Fondo de página |
| `--superficie` | `#ffffff` | Paneles |
| `--navy` | `#152b45` | Títulos, nav brand |
| `--cian` | `#0e7490` | Acento, CTA, enlaces |
| `--cian-suave` | `rgb(14 116 144 / 0.1)` | Fondos de acento |
| `--ambar` | `#b45309` | Avisos |
| `--rojo` | `#b91c1c` | Errores |
| `--texto` | `#334155` | Cuerpo |
| `--apagado` | `#64748b` | Secundario |
| `--linea` | `#d0d7e2` | Bordes |

`color-scheme: light`. Sin sombras multicapa ni glow verde.

## Tipografía

- **Source Serif 4** — títulos (tono informe / academia).
- **Source Sans 3** — cuerpo y UI.
- **IBM Plex Mono** — códigos UNSPSC y métricas (`tabular-nums`).

## Forma

- Radio 10 px en paneles, 8 px en controles.
- Bordes 1 px slate; sin cards con sombra pesada.
- CTA sólido cian; secundarios outline navy.

## Marca institucional

Logos oficiales copiados del ODC (`odc-web-v2/public/logos/`):

- `udec-escudo.png` — nav, hero y pie
- `udec-horizontal.png` — hero (versión para fondo claro)
- `udec-horizontal-claro.png` — disponible si se usa fondo oscuro

## Accesibilidad (Vercel Web Interface Guidelines)

- Skip link a `#contenido`
- `:focus-visible` en controles
- Labels + `aria-invalid` / `aria-live`
- `prefers-reduced-motion`
- Áreas táctiles ≥ 44 px
- `touch-action: manipulation`
- Imágenes con `width`/`height`; escudo decorativo con `alt=""` + `aria-hidden`
