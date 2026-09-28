import unittest
from datetime import datetime, timezone

from buying_window.config import DEFAULT, PRESETS, validate
from buying_window.core import age_days, deduplicate_jobs, mandate_hits, mentions_company, normalise_name, parse_jobs, parse_news, score_account
from buying_window.runner import annotate_comparison, demo, estimate, parse_watchlist, _news_query
from buying_window.storage import redact

NOW = datetime(2026, 9, 28, 12, tzinfo=timezone.utc)


class CoreTests(unittest.TestCase):
    def test_company_identity_is_exact_after_legal_suffix(self):
        self.assertEqual(normalise_name("Northstar Cloud Ltd."), "northstar cloud")
        self.assertTrue(mentions_company("Northstar Cloud raises funding", "Northstar Cloud"))
        self.assertFalse(mentions_company("A Northstar Cloudy forecast", "Northstar Cloud"))

    def test_relative_and_absolute_dates(self):
        self.assertEqual(age_days("3 weeks ago", NOW), 21)
        self.assertEqual(age_days("2026-09-23", NOW), 5)
        self.assertIsNone(age_days("30+ days ago", NOW))
        self.assertIsNone(age_days("unknown", NOW))

    def test_job_key_deduplicates_cross_location_listing(self):
        data = {"jobs": [{"title": "Operations Manager", "company_name": "Acme Ltd", "sharing_link": "https://google.com/search?htidocid=same", "detected_extensions": {"posted_at": "1 day ago"}}]}
        jobs = parse_jobs(data, DEFAULT, NOW) + parse_jobs(data, DEFAULT, NOW)
        self.assertEqual(len(deduplicate_jobs(jobs)), 1)

    def test_news_requires_company_and_event_in_headline(self):
        payload = {"organic_results": [
            {"title": "Acme raises Series B", "date": "2026-09-26", "link": "https://example.com/1"},
            {"title": "Otherco raises funding", "snippet": "Acme is a customer", "date": "2026-09-26"},
            {"title": "Acme launches a feature", "snippet": "funding discussion", "date": "2026-09-26"},
        ]}
        found = parse_news(payload, "Acme", [], DEFAULT, NOW)
        self.assertEqual(len(found), 1)  # A company named only in the snippet is not an event about that company.
        self.assertEqual(found[0]["event"], "funding")

    def test_undated_and_stale_evidence_gets_no_points(self):
        job = {"id": "1", "company": "Example Co", "title": "RevOps Manager", "age_days": None, "role_fit": "strong", "url": ""}
        news = {"title": "Example Co raises funding", "age_days": 50, "identity_confidence": "medium", "url": ""}
        result = score_account("Example Co", [job], [news], DEFAULT)
        self.assertEqual(result["score"], 0)
        self.assertEqual(len(result["jobs"]), 1)

    def test_convergence_is_not_awarded_to_one_signal(self):
        report, _ = demo()
        by_name = {x["company"]: x for x in report["accounts"]}
        self.assertEqual(by_name["Harbor Foods"]["score"], 100)
        self.assertEqual(by_name["Cedar Health"]["parts"]["convergence"], 0)
        self.assertEqual(report["job_count"], 3)
        self.assertTrue(report["demo"])

    def test_one_word_homonym_news_is_visible_but_cannot_score(self):
        job = {"id": "1", "company": "NICE", "title": "Revenue Operations Lead", "age_days": 2, "role_fit": "strong", "url": ""}
        news = {"title": "UK NICE issues health funding guidance", "age_days": 2, "identity_confidence": "low", "url": ""}
        result = score_account("NICE", [job], [news], DEFAULT)
        self.assertEqual(result["score"], 45)
        self.assertEqual(result["parts"]["news"], 0)
        self.assertEqual(result["parts"]["convergence"], 0)
        self.assertEqual(len(result["news"]), 1)

    def test_watchlist_budget_preflight(self):
        text = "\n".join(f"Account {i}" for i in range(50))
        self.assertEqual(estimate("watchlist", text, DEFAULT)["planned_upper_bound"], 100)
        self.assertEqual(len(parse_watchlist("Acme | Acme Ltd, ACME\nAcme")), 1)
        with self.assertRaises(ValueError):
            parse_watchlist("\n".join(f"Account {i}" for i in range(51)))

    def test_invalid_weights_fail(self):
        with self.assertRaises(ValueError):
            validate({"weights": {"role": 40, "recency": 20, "news": 25, "convergence": 14}})

    def test_credentials_are_redacted_from_archive(self):
        value = {"api_key": "secret", "request_url": "https://example.com/?api_key=secret&q=x"}
        output = redact(value)
        self.assertNotIn("secret", str(output))

    def test_profiles_change_the_search_and_hypothesis(self):
        self.assertEqual(DEFAULT["profile_name"], "Growth & expansion")
        self.assertNotIn("revenue operations", DEFAULT["role_queries"])
        self.assertNotEqual(PRESETS["hiring"]["role_queries"], PRESETS["leadership"]["role_queries"])
        self.assertIn(PRESETS["leadership"]["news_query"], _news_query({"company": "Example Co"}, PRESETS["leadership"])["q"])

    def test_mandate_phrase_does_not_match_inside_another_word(self):
        self.assertEqual(mandate_hits("We need new marketing material.", DEFAULT), [])
        self.assertTrue(mandate_hits("We are opening a new market next year.", DEFAULT))

    def test_repeat_scan_marks_only_unseen_evidence(self):
        prior = {"scan_key": "same", "scanned_at": "2026-09-27T00:00:00Z", "accounts": [{"company": "Example Co", "jobs": [{"id": "a"}], "news": [{"id": "n"}]}]}
        current = {"scan_key": "same", "accounts": [{"company": "Example Co", "jobs": [{"id": "a"}, {"id": "b"}], "news": [{"id": "n"}]}]}
        result = annotate_comparison(current, prior)
        self.assertEqual(result["comparison"], "repeat")
        self.assertEqual(result["accounts"][0]["first_seen_jobs"], ["b"])
        self.assertEqual(result["accounts"][0]["first_seen_news"], [])


if __name__ == "__main__":
    unittest.main()
