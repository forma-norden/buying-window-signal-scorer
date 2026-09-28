import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from buying_window.searchapi import BudgetExceeded, SearchApiClient, SearchApiError
from buying_window.runner import _job_queries, analyse, estimate
from buying_window.config import DEFAULT, validate
from buying_window.core import mandate_hits


class _Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class TransportTests(unittest.TestCase):
    def test_no_results_is_empty_not_failed(self):
        client = SearchApiClient("local-test-key", 2)
        payload = _Response(json.dumps({"error": "Google didn't return any results."}).encode())
        with patch("buying_window.searchapi.urlopen", return_value=payload):
            self.assertEqual(client.search({"engine": "google_jobs", "q": "unlikely"}), {"jobs": []})
        self.assertEqual(client.attempts, 1)

    def test_bearer_key_stays_out_of_url(self):
        client = SearchApiClient("local-test-key")
        seen = []

        def fake_open(req, timeout):
            seen.append(req)
            return _Response(b'{"jobs": []}')

        with patch("buying_window.searchapi.urlopen", side_effect=fake_open):
            client.search({"engine": "google_jobs", "q": "revenue operations"})
        self.assertNotIn("local-test-key", seen[0].full_url)
        self.assertEqual(seen[0].get_header("Authorization"), "Bearer local-test-key")

    def test_retry_counts_against_hard_cap(self):
        client = SearchApiClient("local-test-key", 1)
        error = HTTPError("https://example.com", 429, "rate limited", {}, None)
        with patch("buying_window.searchapi.urlopen", side_effect=error), patch("buying_window.searchapi.time.sleep"):
            with self.assertRaises(BudgetExceeded):
                client.search({"engine": "google_news", "q": "Acme"})
        self.assertEqual(client.attempts, 1)

    def test_network_failure_is_redacted(self):
        client = SearchApiClient("local-test-key", 2)
        with patch("buying_window.searchapi.urlopen", side_effect=URLError("secret backend")), patch("buying_window.searchapi.time.sleep"):
            with self.assertRaises(SearchApiError) as context:
                client.search({"engine": "google_news", "q": "Acme"})
        self.assertNotIn("secret backend", str(context.exception))
        self.assertEqual(client.attempts, 2)

    def test_unrecognised_engine_never_calls_transport(self):
        client = SearchApiClient("local-test-key")
        with patch("buying_window.searchapi.urlopen") as transport:
            with self.assertRaises(ValueError):
                client.search({"engine": "google_maps", "q": "Acme"})
        transport.assert_not_called()

    def test_watchlist_queries_are_broad_and_employer_scoped(self):
        settings = validate({"role_queries": ["revenue operations saas"]})
        queries = list(_job_queries("watchlist", [{"company": "Safe Software"}], settings))
        self.assertEqual(len(queries), 2)
        self.assertIn("Safe Software revenue operations", queries[0]["q"])
        self.assertNotIn("saas", queries[0]["q"])

    def test_preflight_rejects_over_cap(self):
        settings = validate({"role_queries": ["one", "two", "three", "four", "five", "six"]})
        estimate_result = estimate("discovery", "", settings)
        self.assertEqual(estimate_result["planned_upper_bound"], 62)

    def test_mandate_excerpt_has_word_boundaries(self):
        hits = mandate_hits("Long introduction with useful context about how the team will build the systems required for launch next year.", DEFAULT)
        self.assertIn("build the systems", hits[0])
        self.assertFalse(hits[0].startswith("ong"))


if __name__ == "__main__":
    unittest.main()
