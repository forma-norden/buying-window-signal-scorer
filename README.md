# Buying Window Signal Scorer

An open-source, local dashboard for prioritising B2B accounts from [SearchApi Google Jobs](https://www.searchapi.io/docs/google-jobs) and [Google News](https://www.searchapi.io/docs/google-news). It combines a hiring signal with company news, but keeps the evidence and uncertainty visible. A score is a research priority, **not a prediction that an account will buy**.

Built by [Forma Nôrden](https://formanorden.com/open-source/) as a companion to the [Buying Window Signal Workflow](https://github.com/forma-norden/buying-window-signal-workflow) and [Signal-Based List Building Workflow](https://github.com/forma-norden/signal-based-list-building-workflow).

![Dashboard showing an evidence-led account list](docs/dashboard.png)

## Try it in two minutes

Requires Python 3.11 or newer.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -e .
python -m buying_window.cli serve
```

Open **http://127.0.0.1:8765** and choose **Explore demo**. The bundled fixture is fictional and labelled as demo data; it makes no API calls.

For live searches, copy `.env.example` to `.env`, add `SEARCHAPI_API_KEY=...`, then choose **Run live scan**. The dashboard binds to your computer only. Do not commit `.env`.

## Two ways to scan

- **Discover employers:** Search relevant roles across the configured US/UK locations, group the employers returned by Google Jobs, then query Google News for the highest-priority employers. The default limit is 50 accounts; edit it in the dashboard.
- **Check a watchlist:** Paste up to 50 company names, one per line. Optional aliases use `Company | alias one, alias two`. Jobs are matched against the employer field, not merely against a search result that happens to mention the name.

The default lens looks for RevOps and Sales Ops hiring. The dashboard lets you edit search phrases, strong and adjacent roles, job-description mandate phrases, news event terms, four score weights, and the discovery account limit. Settings live in ignored `data/config.json`.

## How the score works

| Component | Maximum | Rule |
| --- | ---: | --- |
| Role relevance | 40 | Strong role title earns 25, adjacent earns 15. A matching operations or tooling mandate in the job description adds up to 15 or 10 respectively. |
| Job recency | 20 | Latest matching job earns 20 if posted within 7 days, or 12 if posted within 30 days. |
| Relevant news | 25 | A funding or commercial-leadership event earns points only when dated within 30 days and the company match is sufficiently specific. |
| Convergence | 15 | Both a recent job and qualifying recent news are present. |

Undated and older jobs remain visible but do not score. Low-confidence news also remains visible, but cannot earn news or convergence points. This matters for names shared by unrelated organisations: in our first live run, news about the UK health body NICE appeared beside a job attributed to NICE software. The revised scorer withheld those news points. The [dated run notes](docs/live-run-2026-09-28.md) show what the scan actually found.

The `identity confidence` indicator describes the **name match**, not the trustworthiness of the publisher. `ICP fit` stays unknown until a person verifies the company against their own market definition. Possible recruiters and job boards are flagged for review, not silently filtered out.

## Cost and reproducibility

Before a live run, the UI shows an upper bound for initial requests. The run has a hard limit of **150 HTTP attempts**, including retries; any failed request stays visible as a partial-result warning. The budget is a request count, not a claim about your SearchApi bill. Check the credits and pricing on your own plan.

Each live run writes the latest report to `data/latest.json` and a redacted raw-response archive to `data/raw/`. Both directories are ignored by Git. The dashboard exports the latest account table as CSV or JSON and offers the last raw archive for inspection. Re-score an archive without API calls:

```bash
python -m buying_window.cli replay data/raw/<archive-name>.json
```

For a repeatable live CLI scan using the saved lens:

```bash
python -m buying_window.cli scan --mode discovery --max-accounts 12
```

The [case-study lens](examples/case-study-settings.json) documents the US/UK SaaS search used for the dated run. Copy it to ignored `data/config.json` to reproduce those parameters. Results will change as listings and news change.

## Limitations

- Google Jobs can attribute a posting to a recruiter or job board rather than the hiring company. The tool flags likely intermediaries; verify the employer before outreach.
- The API does not reliably supply an employer domain. Name matching alone cannot establish corporate identity, especially for short or common names.
- Posting dates are often relative or absent. An absent date earns no points; a relative date is interpreted against the scan time.
- A role and a news article do not prove procurement intent. Job descriptions, official careers pages, news context, and your ICP still require review.
- This is one snapshot, not a trend detector. It does not claim that a job is new because it appears in today's scan.

## Tests and project layout

```bash
python -m unittest discover -s tests -v
```

`buying_window/core.py` contains the pure matching and scoring logic. `searchapi.py` bounds API attempts. `runner.py` plans and analyses scans. `webapp.py` serves the local dashboard. `examples/demo-responses.json` is a fictional, key-free fixture. The tests cover date and response parsing, deduplication, ambiguous identity, score behaviour, budgets, and credential redaction. CI runs them on Python 3.11 and 3.13.

## Partnership

This project was built for a SearchApi Developer Ambassador collaboration. SearchApi supplied API credits for testing. Forma Nôrden chose the use case, wrote the code, and reports the observed limitations and results. [SearchApi](https://www.searchapi.io/?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) provides the Google Jobs and Google News data used here.

MIT licensed. See [LICENSE](LICENSE).

## Publication pack

The [site blog, DEV article, LinkedIn article, and LinkedIn launch post](publication/README.md) are written from the same dated run, with different reader angles and platform formats. The Forma Nôrden blog draft follows the site's separate editorial release gate.
