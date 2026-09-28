# Buying Window Signal Scorer

**An open-source Python tool that uses SearchApi's Google Jobs and Google News APIs to find companies whose hiring and news signal a relevant change. Every score links to its source documents.**

<a href="https://www.searchapi.io/?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="./web/search-api-dark.svg">
<img alt="Search powered by SearchApi" src="./web/search-api-light.svg" width="196">
</picture>
</a>

[![CI](https://github.com/forma-norden/buying-window-signal-scorer/actions/workflows/ci.yml/badge.svg)](https://github.com/forma-norden/buying-window-signal-scorer/actions/workflows/ci.yml) [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE) [![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-black.svg)](pyproject.toml) [![Offline tests](https://img.shields.io/badge/tests-offline%20%C2%B7%200%20API%20requests-black.svg)](tests)

A list of suitable companies tells you **who** to research. A new job post may tell you **what they are trying to do now**. Search the roles and company events that matter to your offer, then open a ranked result to check the exact posting, article, date and matched phrase.

The same tool works for a recruiter looking for new teams, a consultant looking for operational change, or a software company looking for expansion projects. Pick a ready-made profile and run it, or change the terms in the dashboard.

![Dashboard showing signal profiles, a request estimate and source-linked company results](docs/dashboard.png)

| I want to… | Start here |
| --- | --- |
| Run a live search on my market | [Get started](#get-started) |
| See the interface without an API key | [Try the sample](#try-the-sample-without-api-requests) |
| Search for a different type of change | [Set up a signal profile](#set-up-a-signal-profile) |
| Understand a score or request count | [How a scan works](#how-a-scan-works) |
| Extend the code | [Repository map](#repository-map) |

## Get started

You need Python 3.11+ and a [SearchApi key](https://www.searchapi.io/?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com). SearchApi offers [100 free requests on signup](https://www.searchapi.io/pricing?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) at the time of writing.

~~~bash
git clone https://github.com/forma-norden/buying-window-signal-scorer.git
cd buying-window-signal-scorer
python -m venv .venv
~~~

Activate the environment:

~~~bash
# macOS / Linux
source .venv/bin/activate
~~~

~~~powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
~~~

Then install and start the app:

~~~bash
python -m pip install -e .
python -m buying_window.cli serve
~~~

Copy `.env.example` to `.env` in the project folder and set `SEARCHAPI_API_KEY=your_key` before your first live scan. The file is ignored by Git; the dashboard reads key availability, never the key itself. Open **http://127.0.0.1:8765**, choose a profile and market, check the request estimate, and click **Run live scan**. If you added the key after starting the server, reload the page.

### Try the sample without API requests

Start the server and click **View growth sample**. The sample is fictional and exercises the same parsing and scoring path as a live search. No SearchApi key or requests are needed.

## Set up a signal profile

A signal profile is the change you are looking for, expressed as job queries, title matches, description phrases and news events. The dashboard starts with four editable options:

| If your offer helps with… | Try | Look for |
| --- | --- | --- |
| Opening a market or scaling operations | **Growth & expansion** | Operations hires, new-market mandates, expansion news |
| Filling roles or training a growing team | **Team buildout** | First hires, team-building language, relevant openings |
| Implementing a leader's new plan | **New leadership** | Senior appointments and roles with change mandates |
| Improving commercial systems | **Revenue operations** | Systems ownership, sales-operations hires, commercial leadership |

For example, a logistics software team can start with **Growth & expansion**, then narrow the job-title and description phrases to distribution roles and new-facility language. A recruiter can choose **Team buildout** and enter the functions they place. Fine-tuning is optional; the presets run as shipped.

Use **Discover companies** to find employers from matching jobs. Use **Check my watchlist** for companies you already follow; enter one name per line and add an alias as `Company | alternate name` when needed.

## How a scan works

1. SearchApi Google Jobs returns postings for the selected roles and market. The app groups matching jobs by employer and removes duplicate listings.
2. SearchApi Google News checks the selected employers for the event phrases in the profile. The company and event must appear in the headline to count.
3. The scorer ranks recent, matching evidence. Open any company to see the job, article, matched phrase, date and points.
4. Export the shortlist as CSV or JSON, or run the same settings later to highlight newly seen items.

The default **100-point score** is deliberately readable:

| Signal | Maximum | What earns it |
| --- | ---: | --- |
| Role and mandate | 40 | A matching title earns points; a matching job-description phrase strengthens it |
| Job recency | 20 | A matching job dated within 30 days; the newest week earns the most |
| Company news | 25 | A dated event whose headline names the company |
| Jobs and news together | 15 | Both qualified signals appear for the same company |

The score orders your research under **your profile**. Read the linked sources before deciding whether the company fits your offer.

## Requests, exports and replay

The default discovery plan makes **two Jobs searches and up to six News searches**: at most eight initial SearchApi requests. The dashboard shows the estimate before a live run and enforces an attempt cap that includes retries. A watchlist's estimate grows with the number of companies you enter.

The API key stays in your environment or ignored `.env` file. Raw responses and the latest report stay under ignored `data/`; exports are available in the dashboard. To re-score a saved archive after changing the code, spend **zero** new API requests:

~~~bash
python -m buying_window.cli replay data/raw/<archive-name>.json
~~~

You can also run the saved profile without the browser:

~~~bash
python -m buying_window.cli scan --mode discovery --max-accounts 3
~~~

## Repository map

| Path | Responsibility |
| --- | --- |
| [`buying_window/config.py`](buying_window/config.py) | Presets, saved settings and validation |
| [`buying_window/runner.py`](buying_window/runner.py) | Search plan, request estimate, collection and repeat-scan comparison |
| [`buying_window/core.py`](buying_window/core.py) | Job/news parsing, identity checks and scoring |
| [`buying_window/searchapi.py`](buying_window/searchapi.py) | Bounded SearchApi client; key sent in an authorization header |
| [`buying_window/webapp.py`](buying_window/webapp.py) and [`web/`](web/) | Local dashboard and exports |
| [`examples/demo-responses.json`](examples/demo-responses.json) and [`tests/`](tests/) | Fictional sample and offline verification |

Run the tests with `python -m unittest discover -s tests -v`. They use fixtures and make no API requests. A [dated live-run note](docs/live-run-2026-09-28.md) records the bounded integration check separately from this guide.

## Where it fits

This is the research step in Forma Nôrden's open-source library. The [Signal-Based List Building Workflow](https://github.com/forma-norden/signal-based-list-building-workflow) helps build a source and target list; the [Buying Window Signal Workflow](https://github.com/forma-norden/buying-window-signal-workflow) helps decide what to do with a verified signal. The scorer supplies the source-linked shortlist between them.

SearchApi supplied API credits for the project. Forma Nôrden built the app and scoring rules. The code is released under the [MIT licence](LICENSE); the SearchApi wordmark is their trademark.
