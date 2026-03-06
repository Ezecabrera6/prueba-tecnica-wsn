from __future__ import annotations

import re
import unicodedata


def read_text_with_fallback(path: str) -> str:
    encodings = ("utf-8", "cp1252", "latin-1")
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as fh:
                text = fh.read()
            return fix_mojibake(text)
        except UnicodeDecodeError:
            continue
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fix_mojibake(fh.read())


def fix_mojibake(text: str) -> str:
    try:
        repaired = text.encode("latin-1").decode("utf-8")
        if repaired.count("\ufffd") <= text.count("\ufffd"):
            return repaired
    except UnicodeError:
        pass
    return text


def canonical_name(value: str) -> str:
    value = fix_mojibake(value).lower().strip()
    value = value.replace("\ufffd", "")
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    value = re.sub(r"[^a-z0-9]+", " ", value).strip()
    return value


def clean_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()
