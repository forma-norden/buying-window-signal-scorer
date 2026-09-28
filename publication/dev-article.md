---
title: I built a buying-signal scanner from job posts and company news
description: An open-source Python app that finds relevant hiring, checks company news, and shows the source behind every ranked B2B prospect.
tags: python, opensource, api, tutorial
---

An “Operations Manager” vacancy might be a routine replacement. It might also be the first hire for a new market. The title does not tell you which. The job description often does.

That is the idea behind [Buying Window Signal Scorer](https://github.com/forma-norden/buying-window-signal-scorer), an MIT-licensed Python app I built at Forma Nôrden. It uses SearchApi's Google Jobs and Google News APIs to find companies making changes relevant to **your** offer. You choose the roles, job-description phrases and company events. The app ranks the matches and keeps the original sources beside each score.

![Buying Window Signal Scorer dashboard with editable profiles and source-linked results](https://raw.githubusercontent.com/forma-norden/buying-window-signal-scorer/main/docs/dashboard.png)

This is useful well beyond sales operations. A recruiter can look for new teams, an implementation partner for systems ownership, or a logistics vendor for market openings. They use the same search pipeline with different signal profiles.

## The two-search pipeline

The first search discovers employers from relevant job posts. With the included growth profile, SearchApi gets two Google Jobs queries, one for `operations manager` and one for `business development manager`. The app groups the returned listings by employer, removes duplicates and selects a bounded number of companies.

Only then does it search Google News for those companies. For each selected employer, it looks for the configured events: funding, expansion and leadership changes by default. Searching news *after* jobs matters because it keeps the request count tied to the shortlist, not the number of listings returned.

The requests use one SearchApi key and two engines:

~~~python
{"engine": "google_jobs", "q": "operations manager",
 "location": "United States", "gl": "us"}

{"engine": "google_news",
 "q": '"Harbor Foods" (funding OR expansion OR appoints)',
 "gl": "us"}
~~~

The company in the second query is illustrative. In a real scan it comes from the Jobs results or your watchlist. SearchApi supplies the [Jobs](https://www.searchapi.io/docs/google-jobs?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) and [News](https://www.searchapi.io/docs/google-news?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) results; the selection and scoring rules are open in [`runner.py`](https://github.com/forma-norden/buying-window-signal-scorer/blob/main/buying_window/runner.py) and [`core.py`](https://github.com/forma-norden/buying-window-signal-scorer/blob/main/buying_window/core.py).

## The job title starts the search; the mandate changes the score

The default score totals 100 points:

| Evidence | Points | What it asks |
| --- | ---: | --- |
| Role and mandate | Up to 40 | Is this a relevant title, and does the description name work the hire will do? |
| Job recency | Up to 20 | Is the matching posting dated within 30 days? |
| Company news | 25 | Is there a dated, matching event about the same company? |
| Both sources | 15 | Do a qualified job and news event appear together? |

A recent, strong job title earns **45 points** under the default profile: 25 for the title and 20 for recency. A relevant phrase in the description can add the remaining 15 role points. Dated company news can add 25, plus 15 when both sources qualify.

The bundled **fictional** sample makes this inspectable. Harbor Foods has an operations role with a “build the team” mandate and a recent expansion article. The dashboard shows the title, matching phrase, article, dates and `40 + 20 + 25 + 15` score parts. You can open the sample without an API key.

The code checks identity as well as keywords. A job is attached to the returned employer, not merely a company name mentioned in a search query. For news points, the headline must name the company **and** contain a configured event phrase. A common one-word company name cannot earn news points from a loose mention. Those checks matter more than adding another clever-sounding weight to the score.

## What happened in a small live run

I ran the growth profile on 28 September 2026 with a three-company limit. Two Jobs requests returned **19 relevant, deduplicated listings**. Three News requests checked the selected employers: **five SearchApi requests** in total, with no failed request.

The selected results earned 45 points from recent titles. None gained news points in that scan. That gave me exactly the work I wanted the tool to expose: open the full postings, look for a genuine mandate, and decide whether the profile terms are specific enough for the offer. A title match appears in the queue without being presented as a complete buying story. The [run note](https://github.com/forma-norden/buying-window-signal-scorer/blob/main/docs/live-run-2026-09-28.md) has the settings and counts.

## Run it on a change you care about

Get a [SearchApi key](https://www.searchapi.io/?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com). The [pricing page](https://www.searchapi.io/pricing?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) currently lists 100 free requests on signup. Then:

~~~bash
git clone https://github.com/forma-norden/buying-window-signal-scorer.git
cd buying-window-signal-scorer
python -m venv .venv
~~~

Activate the environment with `source .venv/bin/activate` on macOS/Linux or `.\.venv\Scripts\Activate.ps1` in PowerShell. Install with `python -m pip install -e .`. Copy `.env.example` to an ignored `.env` file and set `SEARCHAPI_API_KEY=your_key`. Start the local dashboard:

~~~bash
python -m buying_window.cli serve
~~~

Open `http://127.0.0.1:8765`. Choose one of the four profiles, select a market, and look at the request estimate before running. You can also enter a watchlist of companies you already know. The dashboard lets you change searches, title matches, mandate phrases, news events and score weights without editing Python.

For a first useful test, pick one offer and one change it helps with:

- **Recruiting:** search for the roles you can fill; add “first hire” or “build the team” to the mandate phrases.
- **Implementation:** search for function leaders; look for descriptions that mention new systems or standardisation.
- **Expansion services:** search for operations roles; pair new-market language with expansion news.

The default discovery run plans at most **two Jobs and six News requests**. The app shows that plan, enforces an attempt cap including retries, and saves redacted raw responses locally. You can export CSV/JSON or replay a saved archive after changing the scoring logic without another search.

The piece to steal is the sequence: **start with a change your offer can address, find its public evidence, then rank documents you can actually open**. The code and setup are in the [repository](https://github.com/forma-norden/buying-window-signal-scorer).

*SearchApi supplied API credits for this project. Forma Nôrden built the app and its scoring rules.*
