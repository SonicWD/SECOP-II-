import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--fuente-texto",
  display: "swap",
});

const mono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--fuente-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SECOP II · Clasificación y búsqueda",
  description:
    "Proyecto final de PLN: clasifica segmentos UNSPSC y busca procesos similares a partir del texto público.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className={`${inter.variable} ${mono.variable}`}>
      <body>{children}</body>
    </html>
  );
}
