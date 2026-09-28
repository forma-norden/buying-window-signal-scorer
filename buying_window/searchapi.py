"""Bounded SearchApi transport. The key is sent only in an Authorization header."""
from __future__ import annotations

import json
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ENDPOINT = "https://www.searchapi.io/api/v1/search"


class BudgetExceeded(RuntimeError):
    pass


class SearchApiError(RuntimeError):
    pass


class SearchApiClient:
    def __init__(self, api_key: str, max_attempts: int = 150):
        if not api_key:
            raise ValueError("SEARCHAPI_API_KEY is missing")
        self.api_key = api_key
        self.max_attempts = max_attempts
        self.attempts = 0

    def search(self, params: dict) -> dict:
        if params.get("engine") not in {"google_jobs", "google_news"}:
            raise ValueError("Unsupported engine")
        url = ENDPOINT + "?" + urlencode(params)
        last_error = None
        for attempt in range(2):
            if self.attempts >= self.max_attempts:
                raise BudgetExceeded(f"Stopped at the {self.max_attempts}-attempt cap")
            self.attempts += 1
            req = Request(url, headers={"Authorization": f"Bearer {self.api_key}", "Accept": "application/json", "User-Agent": "FormaNordenBuyingWindow/0.1"})
            try:
                with urlopen(req, timeout=25) as response:
                    payload = json.load(response)
                if not isinstance(payload, dict):
                    raise SearchApiError("Unexpected response shape")
                if payload.get("error"):
                    if "didn't return any results" in str(payload["error"]).lower():
                        return {"jobs": []} if params["engine"] == "google_jobs" else {"organic_results": []}
                    raise SearchApiError(str(payload["error"]))
                return payload
            except HTTPError as exc:
                last_error = SearchApiError(f"SearchApi HTTP {exc.code}")
                if exc.code not in {429, 500, 502, 503, 504} or attempt == 1:
                    break
                time.sleep(1)
            except (URLError, TimeoutError) as exc:
                last_error = SearchApiError(f"SearchApi connection failed: {type(exc).__name__}")
                if attempt == 1:
                    break
                time.sleep(1)
        raise last_error or SearchApiError("SearchApi request failed")
