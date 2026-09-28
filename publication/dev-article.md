---
title: I built an open-source tool that turns job posts into a “why now?” list
description: A small Python app that combines Google Jobs and company news into an inspectable buying-window research queue.
tags: python, opensource, api, sales
---

# I built an open-source tool that turns job posts into a “why now?” list

A list of companies in your target industry tells you *who* might be relevant. It does not tell you why this week is a sensible time to talk.

A job post can answer a more useful question. If a company is hiring its first operations manager to open a new market, someone has budgeted for a change. That does not mean the company wants your software or service. It gives you a concrete reason to look closer. Pair the posting with a recent expansion announcement, and you have two source documents to inspect instead of a generic “growing company” label.

I built [Buying Window Signal Scorer](https://github.com/forma-norden/buying-window-signal-scorer) to make that research repeatable. It is a local Python app, open source and MIT licensed. You choose which roles, description phrases, and news events matter to **your** offer. It searches Google Jobs and Google News through SearchApi, scores the matches, and keeps the source links next to every point.

## Run it with your own search

Get a [SearchApi key](https://www.searchapi.io/?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) first. Its [pricing page](https://www.searchapi.io/pricing?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) currently offers 100 free requests on signup. Then:

```bash
git clone https://github.com/forma-norden/buying-window-signal-scorer.git
cd buying-window-signal-scorer
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e .
python -m buying_window.cli serve
```

Copy `.env.example` to `.env`, add `SEARCHAPI_API_KEY=your_key`, and open `http://127.0.0.1:8765`. Select a profile, check the request estimate, and run a live scan. The ignored `.env` file stays on your computer. A fictional sample is available if you want to inspect the interface before spending a request.

## The useful part is deciding what to search for

The default profile looks for operations and business development roles alongside expansion, funding, and leadership news. It is a starting point, not a universal definition of a buying window.

Suppose you sell warehouse planning software. Search for an operations manager or distribution lead, match job descriptions mentioning a new market or scaled operations, and look for distribution-centre news. If you recruit marketers, search for the marketing roles you can fill and for language about building a new team. If you implement CRMs, use the included revenue-operations profile and tune it to system ownership and migration language.

The dashboard exposes the search phrases, title matches, description phrases, news event groups, market, and score weights. No code change is required to try a different hypothesis. You can discover employers from job results or paste a watchlist of companies you already care about.

Under the hood, the two paths start differently:

```python
# Discovery: find employers in relevant Google Jobs results.
{"engine": "google_jobs", "q": "operations manager", "location": "United States", "gl": "us"}

# Watchlist: search for a known employer and your chosen roles.
{"engine": "google_jobs", "q": "Harbor Foods operations manager OR business development manager", "location": "United States", "gl": "us"}
```

In both paths, the scorer checks the returned employer field before assigning a job to a company. An article about a company is checked against the company name and the selected event terms. [SearchApi's Jobs](https://www.searchapi.io/docs/google-jobs?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) and [News](https://www.searchapi.io/docs/google-news?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) endpoints provide the source results; the matching and scoring rules are local and readable in the repository.

## What earns 100 points?

The default score has four parts. A strong title and relevant job-description phrase can earn 40 points. A matching job posted in the last week earns 20. A dated, identity-supported company news event earns 25. Having both qualified signals earns another 15. You can change the weights as long as they total 100.

Here is a **fictional** example from the bundled sample: Harbor Foods has a recent operations manager listing that says the hire will build a team for a new market, plus a dated expansion article. The tool shows the job and article links, the matched description excerpt, and the 40 + 20 + 25 + 15 breakdown. You can replay that fixture without a key. The real value is seeing which source supplied each part of the score.

For a live sanity check on 28 September 2026, I ran the growth profile with a three-company limit. Two Jobs requests returned **19 relevant, deduplicated listings**; three News requests checked the selected employers. The scan used **five requests** and completed without a failed request. The selected companies each earned 45 points from a recent matching title; no news item earned points in that run. That result is less flashy than a perfect score, but it gives a useful next action: inspect the job descriptions and widen or refine the profile if the mandate is too weak.

The app keeps ambiguous news visible for review while withholding news points. It also flags likely recruiters and job boards. A posting date can be missing; an undated listing remains visible without recency points. These rules make the ranking easier to challenge when a search result looks plausible at first glance.

## Make repeat scans useful without pretending to detect publication dates

Run the same profile again and the app marks job and news IDs absent from the previous matching scan as **first seen in your results**. This is a small but important distinction: an item might have been published earlier and missed by the previous query. The label is a change in your observed results, not a claim about when the internet first saw it.

Every run has an estimate and a hard API attempt cap that includes retries. The local app saves a redacted raw-response archive and exports CSV or JSON. You can replay an archive to change the scoring code without buying the same searches again:

```bash
python -m buying_window.cli replay data/raw/<archive-name>.json
python -m unittest discover -s tests -v
```

The code is intentionally small: `core.py` holds pure parsers and scoring rules, `runner.py` plans searches and comparisons, and `webapp.py` serves the local dashboard. The repository includes tests, a fictional fixture, and the exact notes for the bounded live check.

If you try it, I would start with one offer and one market. Which job description would make you say, “we can help with that change”? Put those words in a profile, run the smallest useful scan, and inspect the original sources before acting on the score.

[Explore the repository and run your own scan](https://github.com/forma-norden/buying-window-signal-scorer).

*Disclosure: SearchApi provided API credits for this project. Forma Nôrden built the application and scoring rules.*
