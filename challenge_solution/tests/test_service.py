from __future__ import annotations

from datetime import date, timedelta

import pytest

from src.wns_challenge.errors import (
    IngredientPriceNotFoundError,
    InvalidQuoteDateError,
    RecipeNotFoundError,
)
from src.wns_challenge.models import IngredientRequirement, PriceEntry, Recipe
from src.wns_challenge.service import QuoteService


def _build_service() -> QuoteService:
    recipes = [
        Recipe(
            name="Milanesa con pure",
            ingredients=[IngredientRequirement(name="Carne", required_grams=800)],
        )
    ]
    prices = {"carne": PriceEntry(name="Carne", price_ars_per_kg=10000.0)}
    return QuoteService(recipes=recipes, prices=prices)


def test_quote_success(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _build_service()
    quote_date = date.today() - timedelta(days=1)

    monkeypatch.setattr("src.wns_challenge.service.fetch_ars_per_usd", lambda _d: 1000.0)

    result = service.quote(recipe_name="Milanesa con pure", quote_date=quote_date)

    assert result.recipe_name == "Milanesa con pure"
    assert result.ars_per_usd == 1000.0
    assert result.total_ars == 10000.0
    assert result.total_usd == 10.0
    assert len(result.items) == 1
    assert result.items[0].purchased_grams == 1000


def test_quote_rejects_out_of_range_date() -> None:
    service = _build_service()
    old_date = date.today() - timedelta(days=31)

    with pytest.raises(InvalidQuoteDateError):
        service.quote(recipe_name="Milanesa con pure", quote_date=old_date)


def test_quote_rejects_unknown_recipe() -> None:
    service = _build_service()
    valid_date = date.today() - timedelta(days=1)

    with pytest.raises(RecipeNotFoundError):
        service.quote(recipe_name="Receta inexistente", quote_date=valid_date)


def test_quote_rejects_unknown_ingredient_price(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recipes = [
        Recipe(
            name="Milanesa con pure",
            ingredients=[IngredientRequirement(name="Ingrediente sin precio", required_grams=200)],
        )
    ]
    service = QuoteService(recipes=recipes, prices={})
    valid_date = date.today() - timedelta(days=1)
    monkeypatch.setattr("src.wns_challenge.service.fetch_ars_per_usd", lambda _d: 1000.0)

    with pytest.raises(IngredientPriceNotFoundError):
        service.quote(recipe_name="Milanesa con pure", quote_date=valid_date)
