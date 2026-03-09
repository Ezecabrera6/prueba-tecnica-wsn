from __future__ import annotations

from fastapi.testclient import TestClient

from src.wns_challenge.errors import ChallengeError
from src.wns_challenge.models import IngredientQuote, QuoteResult, Recipe
import web_fastapi

class _ServiceOk:
    @property
    def recipes(self) -> list[Recipe]:
        return [Recipe(name="Asado", ingredients=[])]

    def quote(self, recipe_name: str, quote_date):
        return QuoteResult(
            recipe_name=recipe_name,
            quote_date=quote_date,
            ars_per_usd=1000.0,
            total_ars=2500.0,
            total_usd=2.5,
            items=[
                IngredientQuote(
                    ingredient_name="Carne",
                    matched_price_name="Carne",
                    required_grams=200,
                    purchased_grams=250,
                    unit_price_ars_per_kg=10000.0,
                    total_ars=2500.0,
                )
            ],
        )


class _ServiceErr(_ServiceOk):
    def quote(self, recipe_name: str, quote_date):
        raise ChallengeError("error-controlado")


def test_list_recipes(monkeypatch) -> None:
    monkeypatch.setattr(web_fastapi, "service", _ServiceOk())
    client = TestClient(web_fastapi.app)

    response = client.get("/api/recipes")

    assert response.status_code == 200
    assert response.json() == {"recipes": ["Asado"]}


def test_quote_success(monkeypatch) -> None:
    monkeypatch.setattr(web_fastapi, "service", _ServiceOk())
    client = TestClient(web_fastapi.app)

    response = client.post(
        "/api/quote",
        json={"recipe_name": "Asado", "quote_date": "2026-03-01"},
    )

    payload = response.json()
    assert response.status_code == 200
    assert payload["recipe_name"] == "Asado"
    assert payload["total_ars"] == 2500.0
    assert payload["total_usd"] == 2.5
    assert len(payload["items"]) == 1


def test_quote_maps_domain_error_to_400(monkeypatch) -> None:
    monkeypatch.setattr(web_fastapi, "service", _ServiceErr())
    client = TestClient(web_fastapi.app)

    response = client.post(
        "/api/quote",
        json={"recipe_name": "Asado", "quote_date": "2026-03-01"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "error-controlado"
