from __future__ import annotations

from dataclasses import asdict
from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.wns_challenge.bootstrap import build_service
from src.wns_challenge.errors import ChallengeError


BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
service = build_service(PROJECT_ROOT)

app = FastAPI(title="WNS Challenge - Cotizador")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuoteRequest(BaseModel):
    recipe_name: str
    quote_date: date


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "WNS API running"}


@app.get("/api/recipes")
def list_recipes() -> dict[str, list[str]]:
    return {"recipes": [recipe.name for recipe in service.recipes]}


@app.post("/api/quote")
def quote_api(payload: QuoteRequest) -> dict:
    try:
        result = service.quote(recipe_name=payload.recipe_name, quote_date=payload.quote_date)
    except ChallengeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "recipe_name": result.recipe_name,
        "quote_date": result.quote_date.isoformat(),
        "ars_per_usd": result.ars_per_usd,
        "total_ars": result.total_ars,
        "total_usd": result.total_usd,
        "items": [asdict(item) for item in result.items],
    }
