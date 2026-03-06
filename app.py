from __future__ import annotations

import argparse
import logging
import sys
from datetime import date
from pathlib import Path

from src.wns_challenge.bootstrap import build_service
from src.wns_challenge.errors import ChallengeError


logger = logging.getLogger("wns_challenge")


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Cotiza recetas en ARS/USD usando fuentes locales + API de currency."
    )
    parser.add_argument("--recipe", required=True, help="Nombre de la receta.")
    parser.add_argument("--date", required=True, help="Fecha YYYY-MM-DD.")
    return parser.parse_args()


def print_quote(result) -> None:
    print("\n=== Cotizacion ===")
    print(f"Plato: {result.recipe_name}")
    print(f"Fecha: {result.quote_date.isoformat()}")
    print(f"ARS por USD: {result.ars_per_usd:.4f}")
    print("\nIngredientes:")
    for item in result.items:
        print(
            f"- {item.ingredient_name} | requerido={item.required_grams}g | "
            f"compra={item.purchased_grams}g | ARS/kg={item.unit_price_ars_per_kg:.2f} | "
            f"subtotal={item.total_ars:.2f}"
        )
    print(f"\nTotal ARS: {result.total_ars:.2f}")
    print(f"Total USD: {result.total_usd:.2f}")


def main() -> int:
    configure_logging()
    args = parse_args()

    try:
        quote_date = date.fromisoformat(args.date)
    except ValueError:
        logger.error("Fecha invalida: %s (esperado YYYY-MM-DD).", args.date)
        return 2

    try:
        project_root = Path(__file__).resolve().parent.parent
        service = build_service(project_root)
        result = service.quote(recipe_name=args.recipe, quote_date=quote_date)
    except ChallengeError as exc:
        logger.error(str(exc))
        return 1

    print_quote(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
