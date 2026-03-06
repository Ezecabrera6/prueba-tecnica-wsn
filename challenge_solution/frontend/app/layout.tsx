import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Cotizador de Recetas",
  description: "Cotizador de recetas con precios en ARS y USD"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
