from __future__ import annotations

import difflib
import math
from datetime import date, timedelta

from .exchange_rate import fetch_ars_per_usd
from .errors import (
    IngredientPriceNotFoundError,
    InvalidQuoteDateError,
    RecipeNotFoundError,
)
from .models import IngredientQuote, PriceEntry, QuoteResult, Recipe
from .text_utils import canonical_name


class QuoteService:
    def __init__(self, recipes: list[Recipe], prices: dict[str, PriceEntry]) -> None:
        self._recipes = recipes
        self._recipe_index = {canonical_name(r.name): r for r in recipes}
        self._prices = prices

    @property
    def recipes(self) -> list[Recipe]:
        return self._recipes

    def quote(self, recipe_name: str, quote_date: date) -> QuoteResult:
        self._validate_date(quote_date)
        recipe = self._resolve_recipe(recipe_name)
        ars_per_usd = fetch_ars_per_usd(quote_date)

        items: list[IngredientQuote] = []
        total_ars = 0.0
        for req in recipe.ingredients:
            price = self._resolve_price(req.name)
            purchased_grams = round_up_to_step(req.required_grams, step=250)
            item_total_ars = price.price_ars_per_kg * (purchased_grams / 1000.0)
            total_ars += item_total_ars
            items.append(
                IngredientQuote(
                    ingredient_name=req.name,
                    matched_price_name=price.name,
                    required_grams=req.required_grams,
                    purchased_grams=purchased_grams,
                    unit_price_ars_per_kg=price.price_ars_per_kg,
                    total_ars=item_total_ars,
                )
            )

        total_usd = total_ars / ars_per_usd
        return QuoteResult(
            recipe_name=recipe.name,
            quote_date=quote_date,
            ars_per_usd=ars_per_usd,
            total_ars=total_ars,
            total_usd=total_usd,
            items=items,
        )

    def _resolve_recipe(self, recipe_name: str) -> Recipe:
        key = canonical_name(recipe_name)
        if key in self._recipe_index:
            return self._recipe_index[key]
        match = self._best_key_match(key, list(self._recipe_index))
        if match:
            return self._recipe_index[match]
        raise RecipeNotFoundError(f"Receta no encontrada: {recipe_name}")

    def _resolve_price(self, ingredient_name: str) -> PriceEntry:
        key = canonical_name(ingredient_name)
        if key in self._prices:
            return self._prices[key]
        match = self._best_key_match(key, list(self._prices), cutoff=0.72)
        if match:
            return self._prices[match]
        raise IngredientPriceNotFoundError(
            f"No hay precio cargado para ingrediente: {ingredient_name}"
        )

    @staticmethod
    def _best_key_match(query: str, universe: list[str], cutoff: float = 0.82) -> str | None:
        candidates = difflib.get_close_matches(query, universe, n=1, cutoff=cutoff)
        return candidates[0] if candidates else None

    @staticmethod
    def _validate_date(quote_date: date) -> None:
        today = date.today()
        min_date = today - timedelta(days=30)
        if quote_date < min_date or quote_date > today:
            raise InvalidQuoteDateError(
                f"La fecha debe estar entre {min_date.isoformat()} y {today.isoformat()}."
            )


def round_up_to_step(value: int, step: int) -> int:
    if step <= 0:
        raise ValueError("step debe ser mayor a 0")
    if value <= 0:
        return 0
    return int(math.ceil(value / step) * step)
