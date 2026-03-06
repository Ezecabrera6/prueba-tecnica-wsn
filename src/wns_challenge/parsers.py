from __future__ import annotations

import re
import xml.etree.ElementTree as et
import zipfile
from pathlib import Path

from pypdf import PdfReader

from .models import IngredientRequirement, PriceEntry, Recipe
from .text_utils import canonical_name, clean_spaces, fix_mojibake, read_text_with_fallback


LIST_PREFIX_RE = re.compile(r"^\s*(?:[-*]|\d+\.|[a-zA-Z]\.)\s*")
COLON_RE = re.compile(
    r"^(?P<name>[^:]+):\s*(?P<qty>\d+(?:[.,]\d+)?)\s*(?P<unit>kg|g)\b",
    flags=re.IGNORECASE,
)
DE_RE = re.compile(
    r"^(?P<qty>\d+(?:[.,]\d+)?)\s*(?P<unit>kg|g)\s*de\s*(?P<name>.+)$",
    flags=re.IGNORECASE,
)


def parse_recipes(markdown_path: str | Path) -> list[Recipe]:
    text = read_text_with_fallback(str(markdown_path))
    lines = [fix_mojibake(line).rstrip() for line in text.splitlines()]

    recipes: list[Recipe] = []
    current_name: str | None = None
    current_ingredients: list[IngredientRequirement] = []

    for line in lines:
        heading = re.match(r"^#\s+(.+?)\s*$", line)
        if heading:
            if current_name and current_ingredients:
                recipes.append(Recipe(name=current_name, ingredients=current_ingredients))
            current_name = clean_spaces(heading.group(1))
            current_ingredients = []
            continue

        if not current_name:
            continue

        if not LIST_PREFIX_RE.match(line):
            continue

        parsed = _parse_ingredient_line(line)
        if parsed is None:
            continue
        current_ingredients.append(parsed)

    if current_name and current_ingredients:
        recipes.append(Recipe(name=current_name, ingredients=current_ingredients))

    if not recipes:
        raise ValueError(f"No se pudieron parsear recetas desde: {markdown_path}")

    return recipes


def _parse_ingredient_line(line: str) -> IngredientRequirement | None:
    candidate = LIST_PREFIX_RE.sub("", line).strip()
    if not candidate:
        return None

    colon_match = COLON_RE.match(candidate)
    if colon_match:
        name = clean_spaces(colon_match.group("name"))
        qty = _parse_number(colon_match.group("qty"))
        unit = colon_match.group("unit").lower()
        grams = _to_grams(qty, unit)
        return IngredientRequirement(name=name, required_grams=grams)

    de_match = DE_RE.match(candidate)
    if de_match:
        name = clean_spaces(de_match.group("name"))
        qty = _parse_number(de_match.group("qty"))
        unit = de_match.group("unit").lower()
        grams = _to_grams(qty, unit)
        return IngredientRequirement(name=name, required_grams=grams)

    return None


def load_protein_prices(xlsx_path: str | Path) -> dict[str, PriceEntry]:
    xlsx_path = Path(xlsx_path)
    with zipfile.ZipFile(xlsx_path) as zf:
        shared_strings = _read_shared_strings(zf)
        sheet = et.fromstring(zf.read("xl/worksheets/sheet1.xml"))

    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    prices: dict[str, PriceEntry] = {}

    for row in sheet.findall(".//a:row", ns):
        values = {}
        for cell in row.findall("a:c", ns):
            ref = cell.attrib.get("r", "")
            col = "".join(ch for ch in ref if ch.isalpha())
            val_node = cell.find("a:v", ns)
            if val_node is None:
                continue
            raw = val_node.text or ""
            if cell.attrib.get("t") == "s":
                if raw.isdigit() and int(raw) < len(shared_strings):
                    raw = shared_strings[int(raw)]
            values[col] = fix_mojibake(raw).strip()

        _maybe_add_price(values.get("C"), values.get("D"), prices)
        _maybe_add_price(values.get("F"), values.get("G"), prices)

    if not prices:
        raise ValueError(f"No se pudieron parsear precios desde: {xlsx_path}")

    return prices


def _read_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = et.fromstring(zf.read("xl/sharedStrings.xml"))
    strings = []
    for si in root.findall("a:si", ns):
        txt = "".join((node.text or "") for node in si.findall(".//a:t", ns))
        strings.append(fix_mojibake(txt))
    return strings


def _maybe_add_price(name: str | None, raw_price: str | None, prices: dict[str, PriceEntry]) -> None:
    if not name or not raw_price:
        return
    price = _parse_price(raw_price)
    if price is None:
        return
    cleaned_name = clean_spaces(name)
    prices[canonical_name(cleaned_name)] = PriceEntry(
        name=cleaned_name,
        price_ars_per_kg=price,
    )


def load_vegetable_prices(pdf_path: str | Path) -> dict[str, PriceEntry]:
    reader = PdfReader(str(pdf_path))
    category_names = {"fruto", "hoja", "raiz", "tuberculo"}
    prices: dict[str, PriceEntry] = {}

    for page in reader.pages:
        text = fix_mojibake(page.extract_text() or "")
        lines = [clean_spaces(line) for line in text.splitlines()]
        lines = [line for line in lines if line]

        for idx, line in enumerate(lines):
            next_line = lines[idx + 1] if idx + 1 < len(lines) else ""
            if canonical_name(next_line) not in category_names:
                continue
            if line.startswith("$") or "http" in line.lower():
                continue
            if "built with" in line.lower():
                continue

            raw_price = ""
            for j in range(idx + 1, min(idx + 6, len(lines))):
                m = re.search(r"\$([\d\.,]+)", lines[j])
                if m:
                    raw_price = m.group(1)
                    break
            if not raw_price:
                continue

            price = _parse_price(raw_price)
            if price is None:
                continue
            prices[canonical_name(line)] = PriceEntry(name=line, price_ars_per_kg=price)

    if not prices:
        raise ValueError(f"No se pudieron parsear precios desde: {pdf_path}")

    return prices


def _parse_number(raw: str) -> float:
    return float(raw.replace(",", "."))


def _to_grams(quantity: float, unit: str) -> int:
    if unit == "kg":
        return int(round(quantity * 1000))
    return int(round(quantity))


def _parse_price(raw: str) -> float | None:
    digits = "".join(ch for ch in raw if ch.isdigit())
    if not digits:
        return None
    return float(digits)
