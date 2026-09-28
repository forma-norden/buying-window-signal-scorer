"""Pure parsers, identity matching, and explainable single-scan scoring."""
from __future__ import annotations

import hashlib
import html
import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qs, urlparse

LEGAL_SUFFIXES = {"inc", "incorporated", "ltd", "limited", "llc", "plc", "corp", "corporation"}


def normalise_name(value: str) -> str:
    words = re.findall(r"[a-z0-9]+", (value or "").lower())
    while words and words[-1] in LEGAL_SUFFIXES:
        words.pop()
    return " ".join(words)


def identity_confidence(name: str) -> str:
    return "low" if len(normalise_name(name).split()) == 1 else "medium"


def mentions_company(text: str, name: str, aliases: list[str] | None = None) -> bool:
    haystack = " " + normalise_name(text) + " "
    return any(" " + normalise_name(candidate) + " " in haystack for candidate in [name, *(aliases or [])] if normalise_name(candidate))


def age_days(value: object, now: datetime) -> int | None:
    if not value or not isinstance(value, str):
        return None
    s = value.strip().lower()
    if s in {"today", "just now", "now"}:
        return 0
    if s == "yesterday":
        return 1
    m = re.search(r"(\d+)\s*(hour|day|week|month)s?\s+ago", s)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        return n * {"hour": 0, "day": 1, "week": 7, "month": 30}[unit]
    if "30+" in s or "over 30" in s:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            dt = parsedate_to_datetime(value)
        except (ValueError, TypeError, IndexError):
            dt = None
        if dt is None:
            for pattern in ("%b %d, %Y", "%B %d, %Y"):
                try:
                    dt = datetime.strptime(value, pattern)
                    break
                except ValueError:
                    pass
        if dt is None:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return max(0, (now - dt.astimezone(timezone.utc)).days)


def _job_key(item: dict) -> str:
    url = item.get("sharing_link") or ""
    docid = parse_qs(urlparse(url).query).get("htidocid", [None])[0]
    if docid:
        return docid
    source = "|".join(str(item.get(k, "")) for k in ("title", "company_name", "location", "apply_link"))
    return hashlib.sha256(source.encode()).hexdigest()[:20]


def role_fit(title: str, settings: dict) -> tuple[str, str | None]:
    value = normalise_name(title)
    for label in ("strong", "adjacent"):
        for phrase in settings["roles"].get(label, []):
            if " " + normalise_name(phrase) + " " in " " + value + " ":
                return label, phrase
    return "none", None


def mandate_hits(description: str, settings: dict) -> list[str]:
    plain = html.unescape(re.sub(r"<[^>]+>", " ", description or ""))
    plain = re.sub(r"\s+", " ", plain).replace("’", "'")
    lower = plain.lower()
    hits = []
    for term in settings["mandate_terms"]:
        at = lower.find(term.lower().replace("’", "'"))
        if at >= 0:
            start = max(0, at - 55)
            end = min(len(plain), at + len(term) + 75)
            if start:
                boundary = plain.find(" ", start)
                start = boundary + 1 if boundary >= 0 and boundary < at else start
            if end < len(plain):
                boundary = plain.rfind(" ", at, end)
                end = boundary if boundary > at else end
            hits.append(("…" if start else "") + plain[start:end].strip() + ("…" if end < len(plain) else ""))
    return hits[:2]


def parse_jobs(payload: dict, settings: dict, now: datetime) -> list[dict]:
    jobs = []
    for item in payload.get("jobs", []):
        if not isinstance(item, dict):
            continue
        company = item.get("company_name") or ""
        title = item.get("title") or ""
        if not company or not title:
            continue
        fit, phrase = role_fit(title, settings)
        if fit == "none":
            continue
        posted = (item.get("detected_extensions") or {}).get("posted_at")
        jobs.append({
            "id": _job_key(item), "company": company, "title": title,
            "location": item.get("location") or "", "posted_at": posted,
            "age_days": age_days(posted, now), "role_fit": fit, "role_phrase": phrase,
            "url": item.get("apply_link") or item.get("sharing_link") or "",
            "mandate_evidence": mandate_hits(item.get("description") or "", settings),
        })
    return jobs


def parse_news(payload: dict, company: str, aliases: list[str], settings: dict, now: datetime) -> list[dict]:
    items = payload.get("organic_results") or payload.get("news_results") or []
    results = []
    for item in items:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "")
        snippet = str(item.get("snippet") or "")
        if not mentions_company(title + " " + snippet, company, aliases):
            continue
        normal_title = " " + normalise_name(title) + " "
        event = next((label for label, terms in settings["events"].items() if any(" " + normalise_name(term) + " " in normal_title for term in terms)), None)
        if event == "funding" and not any(term in normal_title for term in ("funding", "series", "seed", "investment", "million", "billion")) and not re.search(r"\$\s*\d", title):
            event = None
        if not event:
            continue
        date = item.get("date") or item.get("published_at")
        results.append({
            "title": title, "snippet": snippet, "event": event,
            "date": date, "age_days": age_days(date, now),
            "source": item.get("source") or "", "url": item.get("link") or "",
            "identity_confidence": "medium" if mentions_company(title, company, aliases) and identity_confidence(company) == "medium" else "low",
        })
    return results


def deduplicate_jobs(jobs: list[dict]) -> list[dict]:
    by_id = {}
    for job in jobs:
        old = by_id.get(job["id"])
        if old is None or (old["age_days"] is None and job["age_days"] is not None):
            by_id[job["id"]] = job
    return list(by_id.values())


def score_account(company: str, jobs: list[dict], news: list[dict], settings: dict, aliases: list[str] | None = None) -> dict:
    aliases = aliases or []
    matched_jobs = [x for x in deduplicate_jobs(jobs) if normalise_name(x["company"]) in {normalise_name(company), *(normalise_name(a) for a in aliases)}]
    matched_news = [x for x in news if x["age_days"] is None or x["age_days"] <= 90]
    current_jobs = [x for x in matched_jobs if x["age_days"] is not None and x["age_days"] <= 30]
    current_news = [x for x in matched_news if x["age_days"] is not None and x["age_days"] <= 30 and x["identity_confidence"] == "medium"]
    role_fraction = max(((25 if x["role_fit"] == "strong" else 15) + (15 if x["role_fit"] == "strong" and x.get("mandate_evidence") else 10 if x.get("mandate_evidence") else 0)) / 40 for x in current_jobs) if current_jobs else 0
    youngest_job = min((x["age_days"] for x in current_jobs), default=None)
    recency_fraction = 1 if youngest_job is not None and youngest_job <= 7 else .6 if youngest_job is not None else 0
    convergence_fraction = 1 if current_jobs and current_news else 0
    weights = settings["weights"]
    parts = {
        "role": round(weights["role"] * role_fraction),
        "recency": round(weights["recency"] * recency_fraction),
        "news": weights["news"] if current_news else 0,
        "convergence": round(weights["convergence"] * convergence_fraction),
    }
    confidence = "low" if identity_confidence(company) == "low" or any(n["identity_confidence"] == "low" for n in current_news) else "medium"
    flags = []
    if re.search(r"recruitment|staffing|jobs|remotehub|job board", company, re.I):
        flags.append("Possible recruiter or job board; verify the actual employer")
    if identity_confidence(company) == "low":
        flags.append("Short company name may match unrelated organisations")
    if any(n["identity_confidence"] == "low" for n in matched_news):
        flags.append("Low-confidence news is shown but excluded from scoring")
    return {
        "company": company, "score": sum(parts.values()), "parts": parts,
        "identity_confidence": confidence, "icp_fit": "unknown",
        "jobs": matched_jobs, "news": matched_news,
        "explanation": f"{len(current_jobs)} dated relevant job(s) and {len(current_news)} identity-supported, dated news event(s) in the last 30 days. Low-confidence news is visible but earns no points.",
        "aliases": aliases,
        "review_flags": flags,
    }
