"""Small, editable signal profiles for different B2B buying-window hypotheses."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONFIG_PATH = DATA / "config.json"

BASE = {
    "profile_name": "Growth & expansion",
    "role_queries": ["operations manager", "business development manager"],
    "roles": {
        "strong": ["operations manager", "business development manager"],
        "adjacent": ["project manager", "general manager", "head of operations"],
    },
    "mandate_terms": ["build the team", "scale operations", "new market", "new office", "expand our", "implement new systems"],
    "news_query": "funding OR expansion OR appoints",
    "events": {
        "funding": ["funding", "series a", "series b", "investment", "raises"],
        "expansion": ["expands", "expansion", "new office", "new market", "opens office"],
        "leadership": ["appoints", "new ceo", "new chief executive", "new president"],
    },
    "weights": {"role": 40, "recency": 20, "news": 25, "convergence": 15},
    "locations": [{"label": "United States", "gl": "us"}],
    "max_accounts": 6,
    "max_requests": 20,
}


def _profile(**changes):
    value = json.loads(json.dumps(BASE))
    value.update(changes)
    return value


PRESETS = {
    "growth": _profile(),
    "hiring": _profile(
        profile_name="Hiring & team buildout",
        role_queries=["software engineer", "marketing manager"],
        roles={"strong": ["software engineer", "marketing manager"], "adjacent": ["product manager", "engineering manager", "recruiter"]},
        mandate_terms=["build the team", "grow the team", "new team", "first hire", "scale our hiring", "hire and develop"],
        news_query="funding OR hiring OR expansion",
        events={"funding": ["funding", "series a", "series b", "investment"], "expansion": ["hiring", "expansion", "new office", "opens office"]},
    ),
    "leadership": _profile(
        profile_name="New leadership",
        role_queries=["head of engineering", "head of marketing"],
        roles={"strong": ["head of engineering", "head of marketing"], "adjacent": ["vp engineering", "vp marketing", "chief technology officer"]},
        mandate_terms=["build the team", "new strategy", "lead the transformation", "modernize", "modernise", "implement new systems"],
        news_query="appoints OR names OR new leadership",
        events={"leadership": ["appoints", "named", "new ceo", "new cto", "new chief", "joins as"]},
    ),
    "revops": _profile(
        profile_name="Revenue operations",
        role_queries=["revenue operations", "sales operations"],
        roles={"strong": ["revenue operations", "revops", "sales operations", "sales ops"], "adjacent": ["gtm operations", "commercial operations"]},
        mandate_terms=["first dedicated revops hire", "crm isn't fully configured", "gtm systems architecture", "evaluate and implement", "own the tech stack", "build the systems"],
        news_query="funding OR appoints OR chief revenue officer",
        events={"funding": ["funding", "series a", "series b", "investment", "raises"], "leadership": ["appoints", "chief revenue officer", "vp sales", "head of sales"]},
    ),
}

DEFAULT = PRESETS["growth"]


def validate(settings: dict) -> dict:
    if not isinstance(settings, dict):
        raise ValueError("Settings must be a JSON object")
    result = json.loads(json.dumps(DEFAULT))
    for name in result:
        if name in settings:
            result[name] = settings[name]
    if not isinstance(result["profile_name"], str) or not 3 <= len(result["profile_name"].strip()) <= 80:
        raise ValueError("Give the profile a name of 3–80 characters")
    if not isinstance(result["role_queries"], list) or not 1 <= len(result["role_queries"]) <= 6 or any(not isinstance(x, str) or not 2 <= len(x.strip()) <= 60 for x in result["role_queries"]):
        raise ValueError("Enter 1–6 job search phrases of 2–60 characters")
    roles = result["roles"]
    if not isinstance(roles, dict) or set(roles) != {"strong", "adjacent"} or any(not isinstance(v, list) or not v or any(not isinstance(x, str) or not x.strip() for x in v) for v in roles.values()):
        raise ValueError("Set strong and adjacent job-title phrases")
    terms = result["mandate_terms"]
    if not isinstance(terms, list) or not 1 <= len(terms) <= 30 or any(not isinstance(x, str) or not 3 <= len(x.strip()) <= 100 for x in terms):
        raise ValueError("Enter 1–30 job-description phrases")
    if not isinstance(result["news_query"], str) or not 3 <= len(result["news_query"].strip()) <= 150:
        raise ValueError("Enter a news search phrase of 3–150 characters")
    events = result["events"]
    if not isinstance(events, dict) or not 1 <= len(events) <= 6 or any(not isinstance(label, str) or not label.strip() or not isinstance(values, list) or not values or any(not isinstance(x, str) or not x.strip() for x in values) for label, values in events.items()):
        raise ValueError("News event groups must contain at least one phrase")
    weights = result["weights"]
    if not isinstance(weights, dict) or set(weights) != {"role", "recency", "news", "convergence"} or any(type(v) is not int or not 0 <= v <= 100 for v in weights.values()) or sum(weights.values()) != 100:
        raise ValueError("The four weights must be whole numbers that sum to 100")
    locations = result["locations"]
    if not isinstance(locations, list) or len(locations) != 1 or not isinstance(locations[0], dict) or not isinstance(locations[0].get("label"), str) or not locations[0]["label"].strip() or not re.fullmatch(r"[a-z]{2}", str(locations[0].get("gl", ""))):
        raise ValueError("Enter one market label and two-letter country code")
    if type(result["max_accounts"]) is not int or not 1 <= result["max_accounts"] <= 50:
        raise ValueError("max_accounts must be between 1 and 50")
    if type(result["max_requests"]) is not int or not 2 <= result["max_requests"] <= 150:
        raise ValueError("max_requests must be between 2 and 150")
    return result


def load() -> dict:
    if CONFIG_PATH.exists():
        saved = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        # Earlier releases saved a RevOps-only lens. Keep that file for the
        # owner, but start the new interface with the broadly useful preset.
        if "profile_name" in saved:
            return validate(saved)
    return validate({})


def save(settings: dict) -> dict:
    checked = validate(settings)
    DATA.mkdir(exist_ok=True)
    temp = CONFIG_PATH.with_suffix(".tmp")
    temp.write_text(json.dumps(checked, indent=2) + "\n", encoding="utf-8")
    temp.replace(CONFIG_PATH)
    return checked
