from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class IngredientRequirement:
    name: str
    required_grams: int


@dataclass(frozen=True)
class Ingredient(IngredientRequirement):
    """Alias semantico para entrevistas/documentacion."""


@dataclass(frozen=True)
class Recipe:
    name: str
    ingredients: list[IngredientRequirement]


@dataclass(frozen=True)
class PriceEntry:
    name: str
    price_ars_per_kg: float


@dataclass(frozen=True)
class PriceItem(PriceEntry):
    """Alias semantico para entrevistas/documentacion."""


@dataclass(frozen=True)
class IngredientQuote:
    ingredient_name: str
    matched_price_name: str
    required_grams: int
    purchased_grams: int
    unit_price_ars_per_kg: float
    total_ars: float


@dataclass(frozen=True)
class QuoteResult:
    recipe_name: str
    quote_date: date
    ars_per_usd: float
    total_ars: float
    total_usd: float
    items: list[IngredientQuote]
