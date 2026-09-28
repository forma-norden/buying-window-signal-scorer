"""Validated local settings and the GTM/RevOps starter lens."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONFIG_PATH = DATA / "config.json"

DEFAULT = {
    "role_queries": ["revenue operations", "sales operations"],
    "roles": {
        "strong": ["revenue operations", "revops", "sales operations", "sales ops"],
        "adjacent": ["gtm operations", "go-to-market operations", "commercial operations"],
    },
    "mandate_terms": ["first dedicated revops hire", "crm isn't fully configured", "tooling stack is unevaluated", "gtm systems architecture", "evaluate and implement", "select and implement", "own the tech stack", "build the systems"],
    "events": {
        "funding": ["funding", "raises", "raised", "series a", "series b", "series c"],
        "leadership": ["chief revenue officer", "chief sales officer", "cro appointment", "vp sales", "head of sales", "vp revenue"],
    },
    "weights": {"role": 40, "recency": 20, "news": 25, "convergence": 15},
    "locations": [
        {"label": "United States", "gl": "us"},
        {"label": "United Kingdom", "gl": "uk"},
    ],
    "max_accounts": 50,
    "max_requests": 150,
}


def validate(settings: dict) -> dict:
    if not isinstance(settings, dict):
        raise ValueError("Settings must be a JSON object")
    result = json.loads(json.dumps(DEFAULT))
    for name in ("role_queries", "roles", "mandate_terms", "events", "weights", "locations", "max_accounts"):
        if name in settings:
            result[name] = settings[name]
    for name in ("role_queries",):
        if not isinstance(result[name], list) or not 1 <= len(result[name]) <= 6 or not all(isinstance(x, str) and 2 <= len(x.strip()) <= 60 for x in result[name]):
            raise ValueError("Enter 1–6 role queries of 2–60 characters")
    for bucket in ("roles", "events"):
        value = result[bucket]
        if not isinstance(value, dict) or not value or any(not isinstance(items, list) or not items or any(not isinstance(x, str) or not x.strip() for x in items) for items in value.values()):
            raise ValueError(f"{bucket} must map labels to non-empty phrase lists")
    if not isinstance(result["mandate_terms"], list) or not 1 <= len(result["mandate_terms"]) <= 30 or any(not isinstance(x, str) or not 3 <= len(x.strip()) <= 100 for x in result["mandate_terms"]):
        raise ValueError("Enter 1–30 mandate phrases of 3–100 characters")
    weights = result["weights"]
    if set(weights) != {"role", "recency", "news", "convergence"} or any(type(v) is not int or v < 0 or v > 100 for v in weights.values()) or sum(weights.values()) != 100:
        raise ValueError("The four weights must be whole numbers that sum to 100")
    locations = result["locations"]
    if not isinstance(locations, list) or not 1 <= len(locations) <= 3 or any(not isinstance(x, dict) or not isinstance(x.get("label"), str) or x.get("gl") not in ("us", "uk") for x in locations):
        raise ValueError("Choose 1–3 US/UK locations")
    if type(result["max_accounts"]) is not int or not 1 <= result["max_accounts"] <= 50:
        raise ValueError("max_accounts must be between 1 and 50")
    return result


def load() -> dict:
    if CONFIG_PATH.exists():
        return validate(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
    return validate({})


def save(settings: dict) -> dict:
    checked = validate(settings)
    DATA.mkdir(exist_ok=True)
    temp = CONFIG_PATH.with_suffix(".tmp")
    temp.write_text(json.dumps(checked, indent=2) + "\n", encoding="utf-8")
    temp.replace(CONFIG_PATH)
    return checked
