"""Latest snapshot and local raw-response archive; no credentials are persisted."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .config import DATA


def redact(value):
    if isinstance(value, dict):
        return {k: ("[redacted]" if k.lower() in {"api_key", "authorization"} else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, str):
        return re.sub(r"([?&]api_key=)[^&\s]+", r"\1[redacted]", value, flags=re.I)
    return value


def save_run(report: dict, entries: list[dict], settings: dict, watchlist: str = "") -> Path:
    DATA.mkdir(exist_ok=True)
    raw_dir = DATA / "raw"
    raw_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = raw_dir / f"{stamp}.json"
    suffix = 1
    while path.exists():
        path = raw_dir / f"{stamp}-{suffix}.json"
        suffix += 1
    path.write_text(json.dumps(redact({"report": report, "entries": entries, "settings": settings, "watchlist": watchlist}), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    latest = DATA / "latest.json"
    temp = latest.with_suffix(".tmp")
    temp.write_text(json.dumps(redact(report), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temp.replace(latest)
    return path


def latest_report() -> dict | None:
    path = DATA / "latest.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def load_archive(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
