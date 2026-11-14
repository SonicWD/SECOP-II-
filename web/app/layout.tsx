import type { Metadata, Viewport } from "next";
import { IBM_Plex_Mono, Libre_Baskerville, Poppins } from "next/font/google";
import "./globals.css";

const display = Libre_Baskerville({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--fuente-display",
  display: "swap",
});

const sans = Poppins({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--fuente-texto",
  display: "swap",
});

const mono = IBM_Plex_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--fuente-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SECOP II · Clasificación y búsqueda",
  description:
    "Proyecto final de PLN: clasifica segmentos UNSPSC y busca procesos similares a partir del texto público.",
};

export const viewport: Viewport = {
  themeColor: "#faf7f5",
  colorScheme: "light",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={`${display.variable} ${sans.variable} ${mono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
