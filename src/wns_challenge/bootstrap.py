from __future__ import annotations

from pathlib import Path

from .models import PriceEntry
from .parsers import load_protein_prices, load_vegetable_prices, parse_recipes
from .service import QuoteService


def build_service(base_dir: str | Path = ".") -> QuoteService:
    base_path = Path(base_dir)
    input_dir = base_path / "inputs"

    recipes = parse_recipes(input_dir / "Recetas.md")
    prices: dict[str, PriceEntry] = {}
    prices.update(load_protein_prices(input_dir / "Carnes y Pescados.xlsx"))
    prices.update(load_vegetable_prices(input_dir / "verduleria.pdf"))

    return QuoteService(recipes=recipes, prices=prices)
