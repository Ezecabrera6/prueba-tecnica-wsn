from __future__ import annotations

import json
from datetime import date
from urllib.error import URLError
from urllib.request import urlopen

from .errors import FXApiError


_FX_CACHE: dict[str, float] = {}


def fetch_ars_per_usd(for_date: date, timeout_sec: int = 10) -> float:
    date_value = for_date.isoformat()
    if date_value in _FX_CACHE:
        return _FX_CACHE[date_value]

    url = f"https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@{date_value}/v1/currencies/usd.json"
    try:
        with urlopen(url, timeout=timeout_sec) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except URLError as exc:
        raise FXApiError(f"No se pudo consultar cotizacion USD para {date_value}: {exc}") from exc

    usd = payload.get("usd", {})
    ars = usd.get("ars")
    if ars is None:
        raise FXApiError(f"La API no devolvio cotizacion ARS para la fecha {date_value}.")
    value = float(ars)
    _FX_CACHE[date_value] = value
    return value
