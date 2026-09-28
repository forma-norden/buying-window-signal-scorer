"""Local dashboard API. Bind to loopback only; no remote service is needed."""
from __future__ import annotations

import csv
import io
import os
from pathlib import Path

from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from .config import DATA, ROOT, load, save, validate
from .runner import collect, demo, estimate
from .storage import latest_report, save_run

app = FastAPI(title="Buying Window Signal Scorer", docs_url=None, redoc_url=None)
app.mount("/assets", StaticFiles(directory=ROOT / "web"), name="assets")


def _key() -> str:
    key = os.getenv("SEARCHAPI_API_KEY", "").strip()
    if key:
        return key
    path = ROOT / ".env"
    if path.exists():
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if line.startswith("SEARCHAPI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


@app.get("/")
def index():
    return FileResponse(ROOT / "web" / "index.html")


@app.get("/api/config")
def get_config():
    return {"config": load(), "key_ready": bool(_key())}


@app.put("/api/config")
def put_config(body: dict = Body(...)):
    try:
        return {"config": save(body)}
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/api/estimate")
def post_estimate(body: dict = Body(...)):
    try:
        return estimate(body.get("mode", "discovery"), body.get("watchlist", ""), load())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.get("/api/latest")
def get_latest():
    return {"report": latest_report()}


@app.post("/api/demo")
def post_demo():
    report, entries = demo()
    path = save_run(report, entries, load())
    report["archive_name"] = path.name
    return {"report": report}


@app.post("/api/scan")
def post_scan(body: dict = Body(...)):
    if not _key():
        raise HTTPException(400, "Add SEARCHAPI_API_KEY to the local .env file before a live scan")
    mode, watchlist = body.get("mode", "discovery"), body.get("watchlist", "")
    settings = load()
    try:
        report, entries, _ = collect(mode, watchlist, settings, _key())
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    path = save_run(report, entries, settings, watchlist)
    report["archive_name"] = path.name
    return {"report": report}


@app.get("/api/export.json")
def export_json():
    report = latest_report()
    if not report:
        raise HTTPException(404, "Run a scan first")
    return JSONResponse(report, headers={"Content-Disposition": 'attachment; filename="buying-window-snapshot.json"'})


@app.get("/api/export.csv")
def export_csv():
    report = latest_report()
    if not report:
        raise HTTPException(404, "Run a scan first")
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["company", "score", "identity_confidence", "icp_fit", "job_count", "news_count", "role_points", "recency_points", "news_points", "convergence_points", "evidence_urls"])
    writer.writeheader()
    for row in report["accounts"]:
        writer.writerow({
            "company": row["company"], "score": row["score"], "identity_confidence": row["identity_confidence"], "icp_fit": row["icp_fit"],
            "job_count": len(row["jobs"]), "news_count": len(row["news"]),
            "role_points": row["parts"]["role"], "recency_points": row["parts"]["recency"],
            "news_points": row["parts"]["news"], "convergence_points": row["parts"]["convergence"],
            "evidence_urls": " | ".join(x["url"] for x in row["jobs"] + row["news"] if x["url"]),
        })
    return Response(output.getvalue(), media_type="text/csv", headers={"Content-Disposition": 'attachment; filename="buying-window-snapshot.csv"'})


@app.get("/api/raw-latest")
def raw_latest():
    raw = DATA / "raw"
    files = sorted(raw.glob("*.json")) if raw.exists() else []
    if not files:
        raise HTTPException(404, "No archived response yet")
    return FileResponse(files[-1], filename=files[-1].name, media_type="application/json")
