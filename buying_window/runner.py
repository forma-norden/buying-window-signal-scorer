"""Search planning, collection, and offline analysis."""
from __future__ import annotations

import json
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

from .config import DEFAULT, ROOT, validate
from .core import deduplicate_jobs, normalise_name, parse_jobs, parse_news, score_account
from .searchapi import BudgetExceeded, SearchApiClient


def parse_watchlist(text: str) -> list[dict]:
    result = []
    seen = set()
    for line in (text or "").splitlines():
        cells = line.split("|", 1)
        name = cells[0].strip()
        if not name:
            continue
        if len(name) > 100:
            raise ValueError("Company names must be under 100 characters")
        key = normalise_name(name)
        if key in seen:
            continue
        seen.add(key)
        aliases = [x.strip() for x in cells[1].split(",") if x.strip()] if len(cells) == 2 else []
        result.append({"company": name, "aliases": aliases[:5]})
    if len(result) > 50:
        raise ValueError("A run supports at most 50 accounts")
    return result


def estimate(mode: str, watchlist: str, settings: dict) -> dict:
    settings = validate(settings)
    if mode not in {"discovery", "watchlist"}:
        raise ValueError("Choose discovery or watchlist")
    accounts = parse_watchlist(watchlist)
    if mode == "watchlist" and not accounts:
        raise ValueError("Add at least one company")
    jobs = len(settings["role_queries"]) * len(settings["locations"]) if mode == "discovery" else len(accounts) * len(settings["locations"])
    news = settings["max_accounts"] if mode == "discovery" else len(accounts)
    planned = jobs + news
    return {"jobs_requests": jobs, "news_requests_upper_bound": news, "planned_upper_bound": planned, "attempt_cap": settings["max_requests"], "within_cap": planned <= settings["max_requests"]}


def _job_queries(mode: str, accounts: list[dict], settings: dict):
    if mode == "discovery":
        for loc in settings["locations"]:
            for role in settings["role_queries"]:
                yield {"engine": "google_jobs", "q": role, "location": loc["label"], "gl": loc["gl"], "hl": "en"}
    else:
        joined = " OR ".join(settings["role_queries"])
        for account in accounts:
            for loc in settings["locations"]:
                yield {"engine": "google_jobs", "q": f'{account["company"]} {joined}', "location": loc["label"], "gl": loc["gl"], "hl": "en"}


def _news_query(account: dict, settings: dict) -> dict:
    name = account["company"].replace('"', "")
    return {"engine": "google_news", "q": f'"{name}" ({settings["news_query"]})', "gl": settings["locations"][0]["gl"], "hl": "en", "link": "resolved"}


def scan_key(mode: str, watchlist: str, settings: dict) -> str:
    shape = {"mode": mode, "watchlist": parse_watchlist(watchlist) if mode == "watchlist" else [], "profile": settings}
    return hashlib.sha256(json.dumps(shape, sort_keys=True).encode()).hexdigest()[:16]


def annotate_comparison(report: dict, previous: dict | None) -> dict:
    if not previous or previous.get("scan_key") != report.get("scan_key") or previous.get("demo"):
        report["comparison"] = "baseline"
        return report
    old = {normalise_name(row["company"]): row for row in previous.get("accounts", [])}
    for row in report["accounts"]:
        prior = old.get(normalise_name(row["company"]))
        if prior is None:
            row["first_seen_jobs"] = [x["id"] for x in row["jobs"]]
            row["first_seen_news"] = [x["id"] for x in row["news"]]
        else:
            old_jobs = {x.get("id") for x in prior.get("jobs", [])}
            old_news = {x.get("id") for x in prior.get("news", [])}
            row["first_seen_jobs"] = [x["id"] for x in row["jobs"] if x["id"] not in old_jobs]
            row["first_seen_news"] = [x["id"] for x in row["news"] if x["id"] not in old_news]
    report["comparison"] = "repeat"
    report["compared_to"] = previous["scanned_at"]
    return report


def analyse(entries: list[dict], mode: str, watchlist: str, settings: dict, now: datetime | None = None, errors: list[dict] | None = None) -> dict:
    settings = validate(settings)
    now = now or datetime.now(timezone.utc)
    jobs = deduplicate_jobs([job for entry in entries if entry.get("stage") == "jobs" for job in parse_jobs(entry.get("response", {}), settings, now)])
    if mode == "discovery":
        grouped = {}
        for job in jobs:
            key = normalise_name(job["company"])
            if key:
                grouped.setdefault(key, []).append(job)
        def discovery_priority(group):
            dated = [job for job in group if job["age_days"] is not None and job["age_days"] <= 30]
            strong = any(job["role_fit"] == "strong" for job in dated)
            mandate = any(job.get("mandate_evidence") for job in dated)
            youngest = min((job["age_days"] for job in dated), default=999)
            name = group[0]["company"]
            intermediary = bool(re.search(r"recruitment|staffing|job board|legal entity|^\d{3,}[-\s]", name, re.I))
            return (int(intermediary), -int(mandate), -int(strong), -int(bool(dated)), youngest, -len(group), name.lower())
        ordered = sorted(grouped.values(), key=discovery_priority)
        accounts = [{"company": group[0]["company"], "aliases": []} for group in ordered[:settings["max_accounts"]]]
    else:
        accounts = parse_watchlist(watchlist)
    rows = []
    for account in accounts:
        news = []
        for entry in entries:
            if entry.get("stage") == "news" and normalise_name(entry.get("company", "")) == normalise_name(account["company"]):
                news.extend(parse_news(entry.get("response", {}), account["company"], account["aliases"], settings, now))
        rows.append(score_account(account["company"], jobs, news, settings, account["aliases"]))
    rows.sort(key=lambda row: (-row["score"], row["company"].lower()))
    return {
        "scanned_at": now.isoformat(), "mode": mode, "profile_name": settings["profile_name"], "scan_key": scan_key(mode, watchlist, settings), "account_count": len(rows),
        "job_count": len(jobs), "request_count": len(entries), "errors": errors or [],
        "partial": bool(errors), "weights": settings["weights"], "accounts": rows,
        "method": "Scores use matching jobs and company news from the past 30 days.",
    }


def collect(mode: str, watchlist: str, settings: dict, api_key: str) -> tuple[dict, list[dict], int]:
    settings = validate(settings)
    preflight = estimate(mode, watchlist, settings)
    if not preflight["within_cap"]:
        raise ValueError(f'Planned upper bound {preflight["planned_upper_bound"]} exceeds the {settings["max_requests"]}-attempt cap')
    accounts = parse_watchlist(watchlist)
    client = SearchApiClient(api_key, settings["max_requests"])
    entries, errors = [], []
    for params in _job_queries(mode, accounts, settings):
        try:
            entries.append({"stage": "jobs", "params": params, "response": client.search(params)})
        except BudgetExceeded:
            errors.append({"stage": "jobs", "query": params["q"], "message": "Attempt cap reached"})
            break
        except Exception as exc:
            errors.append({"stage": "jobs", "query": params["q"], "message": str(exc)})
    if mode == "discovery":
        preview = analyse(entries, mode, watchlist, settings)
        accounts = [{"company": row["company"], "aliases": []} for row in preview["accounts"]]
    for account in accounts:
        params = _news_query(account, settings)
        try:
            entries.append({"stage": "news", "company": account["company"], "params": params, "response": client.search(params)})
        except BudgetExceeded:
            errors.append({"stage": "news", "query": account["company"], "message": "Attempt cap reached"})
            break
        except Exception as exc:
            errors.append({"stage": "news", "query": account["company"], "message": str(exc)})
    report = analyse(entries, mode, watchlist, settings, errors=errors)
    report["request_count"] = client.attempts
    report["planned_upper_bound"] = preflight["planned_upper_bound"]
    return report, entries, client.attempts


def demo() -> tuple[dict, list[dict]]:
    archive = json.loads((ROOT / "examples" / "demo-responses.json").read_text(encoding="utf-8"))
    now = datetime.fromisoformat(archive["as_of"].replace("Z", "+00:00"))
    report = analyse(archive["entries"], archive["mode"], archive.get("watchlist", ""), DEFAULT, now)
    report["demo"] = True
    return report, archive["entries"]


def replay(path: Path) -> dict:
    archive = json.loads(path.read_text(encoding="utf-8"))
    if "as_of" in archive:
        now = datetime.fromisoformat(archive["as_of"].replace("Z", "+00:00"))
        return analyse(archive["entries"], archive["mode"], archive.get("watchlist", ""), archive.get("settings", DEFAULT), now)
    previous = archive["report"]
    now = datetime.fromisoformat(previous["scanned_at"])
    report = analyse(archive["entries"], previous["mode"], archive.get("watchlist", ""), archive.get("settings", DEFAULT), now, previous.get("errors", []))
    return annotate_comparison(report, archive.get("previous_report"))
