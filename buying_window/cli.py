"""Serve the dashboard, produce a demo, or replay a local archive."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .config import load
from .runner import collect
from .runner import demo, replay
from .storage import save_run


def main():
    parser = argparse.ArgumentParser(description="Buying-window signal scorer")
    sub = parser.add_subparsers(dest="command", required=True)
    serve = sub.add_parser("serve", help="Start the local dashboard")
    serve.add_argument("--port", type=int, default=8765)
    sub.add_parser("demo", help="Run the bundled, labelled example without API calls")
    rep = sub.add_parser("replay", help="Re-score a raw response archive without API calls")
    rep.add_argument("archive", type=Path)
    scan = sub.add_parser("scan", help="Run a live scan with the saved lens")
    scan.add_argument("--mode", choices=["discovery", "watchlist"], default="discovery")
    scan.add_argument("--watchlist-file", type=Path)
    scan.add_argument("--max-accounts", type=int, default=None)
    args = parser.parse_args()
    if args.command == "serve":
        import uvicorn
        uvicorn.run("buying_window.webapp:app", host="127.0.0.1", port=args.port)
    elif args.command == "scan":
        from .webapp import _key
        settings = load()
        if args.max_accounts is not None:
            settings["max_accounts"] = args.max_accounts
        watchlist = args.watchlist_file.read_text(encoding="utf-8") if args.watchlist_file else ""
        report, entries, _ = collect(args.mode, watchlist, settings, _key())
        path = save_run(report, entries, settings, watchlist)
        print(json.dumps({"archive": str(path), "scanned_at": report["scanned_at"], "account_count": report["account_count"], "job_count": report["job_count"], "request_count": report["request_count"], "partial": report["partial"], "top_accounts": [{"company": x["company"], "score": x["score"]} for x in report["accounts"][:10]]}, indent=2))
    else:
        report = demo()[0] if args.command == "demo" else replay(args.archive)
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
