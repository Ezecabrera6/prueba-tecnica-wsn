"use client";

import { FormEvent, useEffect, useState } from "react";

type QuoteItem = {
  ingredient_name: string;
  required_grams: number;
  purchased_grams: number;
  total_ars: number;
};

type Quote = {
  recipe_name: string;
  quote_date: string;
  ars_per_usd: number;
  total_ars: number;
  total_usd: number;
  items: QuoteItem[];
};

const fmtARS = (n: number) => new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" }).format(n);
const fmtUSD = (n: number) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" }).format(n);
const todayISO = new Date().toISOString().slice(0, 10);
const minISO = new Date(Date.now() - 30 * 86400000).toISOString().slice(0, 10);

export default function Page() {
  const [recipes, setRecipes] = useState<string[]>([]);
  const [date, setDate] = useState(new Date(Date.now() - 86400000).toISOString().slice(0, 10));
  const [recipe, setRecipe] = useState("");
  const [quote, setQuote] = useState<Quote | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/recipes")
      .then((r) => r.json())
      .then((d) => {
        const list = d.recipes ?? [];
        setRecipes(list);
        if (list[0]) setRecipe(list[0]);
      })
      .catch(() => setError("No se pudo cargar recetas."));
  }, []);

  async function quoteRecipe(e?: FormEvent) {
    e?.preventDefault();
    if (!recipe) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/quote", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ recipe_name: recipe, quote_date: date })
      });
      const payload = await res.json();
      if (!res.ok) throw new Error(payload.detail || "Error al cotizar.");
      setQuote(payload as Quote);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error de carga.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <header className="top card">
        <div>
          <h1>Cotizador de Recetas</h1>
          <p>Seleccioná receta y fecha (ultimos 30 dias) para calcular ARS y USD.</p>
        </div>
        <div className="pill">{quote ? `1 USD = ${quote.ars_per_usd.toFixed(2)} ARS` : "-"}</div>
      </header>

      <form className="controls card" onSubmit={quoteRecipe}>
        <select value={recipe} onChange={(e) => { setRecipe(e.target.value); setError(""); }}>
          {recipes.map((r) => (
            <option key={r} value={r}>{r}</option>
          ))}
        </select>
        <input
          type="date"
          value={date}
          min={minISO}
          max={todayISO}
          onChange={(e) => { setDate(e.target.value); setError(""); }}
        />
        <button type="submit" disabled={loading || !recipe}>
          {loading ? "Cotizando..." : "Cotizar"}
        </button>
      </form>

      {error ? <p className="error">{error}</p> : null}

      <section className="card">
        <h2>{quote?.recipe_name ?? "Resultado"}</h2>
        <table>
          <thead><tr><th>Ingrediente</th><th>Req(g)</th><th>Compra(g)</th><th>Subtotal ARS</th><th>Subtotal USD</th></tr></thead>
          <tbody>
            {quote?.items.map((i) => (
              <tr key={i.ingredient_name}>
                <td>{i.ingredient_name}</td>
                <td>{i.required_grams}</td>
                <td>{i.purchased_grams}</td>
                <td>{fmtARS(i.total_ars)}</td>
                <td>{fmtUSD(i.total_ars / quote.ars_per_usd)}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="totals">
          <p><strong>Total ARS:</strong> {quote ? fmtARS(quote.total_ars) : "-"}</p>
          <p><strong>Total USD:</strong> {quote ? fmtUSD(quote.total_usd) : "-"}</p>
        </div>
      </section>
    </main>
  );
}
