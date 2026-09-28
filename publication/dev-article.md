---
title: "We Built a RevOps Buying-Signal Scanner. Its Top Result Was Wrong."
description: "A SearchApi Google Jobs + News project found 35 relevant roles in 16 requests. The false positive was more instructive than the leaderboard."
tags: python, opensource, sales, api
published: false
---

# We built a RevOps buying-signal scanner. Its top result was wrong.

We wanted a short list of B2B SaaS accounts whose public hiring and company news suggested a real operations project. Our first version produced a beautiful 100/100 result for **NICE**. The job was attributed to a software company called NICE. The news was about the unrelated UK health body of the same name.

That mistake changed the build. The open-source [Buying Window Signal Scorer](https://github.com/forma-norden/buying-window-signal-scorer) now shows uncertain matches without awarding them points. It treats a score as a research priority, never as proof that a company intends to buy.

**TL;DR:** A live US/UK run on 28 September 2026 made **16 SearchApi requests**, found **35 deduplicated relevant job listings**, and carried **12 employers** into a news check. Three job descriptions described a concrete operations mandate. **Zero** news events passed our date and identity rules. The project includes a local dashboard, editable scoring lens, request cap, source drilldown, exports, demo fixture, replay and tests.

## Why build another signal tool?

“Hiring RevOps” is easy to search. It is hard to use responsibly. The search result might be stale, the employer might be a recruiter, and a generic job title rarely tells you what systems work is happening. Adding company news can help, but it can also amplify a homonym like NICE.

We wanted a tool where an operator can answer five questions before contacting an account: **What was observed? When? At which employer? What exact work does the description imply? What still needs verification?** That is a narrower and more useful goal than predicting purchase intent.

The input comes from [SearchApi's Google Jobs](https://www.searchapi.io/docs/google-jobs) and [Google News](https://www.searchapi.io/docs/google-news) endpoints. The app runs on your machine; no hosted dashboard or database is needed. The two modes are discovery across configured role and location searches, and a named watchlist of up to 50 accounts.

## The small scoring model

The default lens awards at most 100 points:

| Signal | Max | Rule |
| --- | ---: | --- |
| Role relevance | 40 | Strong or adjacent title, with extra weight for a configured job-description mandate |
| Job recency | 20 | Dated role within 7 days: 20; within 30 days: 12 |
| Qualified news | 25 | Recent funding or commercial leadership event linked confidently to the company |
| Convergence | 15 | Both a recent job and qualified news |

An old or undated posting stays in the results but scores zero. A questionable news match stays visible but cannot create news or convergence points. The role terms, mandate phrases, news events and weights are editable in the UI. ICP fit is marked separately because a text match cannot know your customers, exclusions or sales territories.

The code is intentionally deterministic. The relevant shape is:

```python
recent_job = job_age is not None and job_age <= 30
qualified_news = (
    news_age is not None
    and news_age <= 30
    and identity_confidence != "low"
)
convergence = recent_job and qualified_news
```

The [full scorer](https://github.com/forma-norden/buying-window-signal-scorer/blob/main/buying_window/core.py) also handles title fit, description excerpts, duplicate listings and source URLs. The important product choice is that the UI exposes the evidence and flags alongside the score.

## What the live run found

We used two SaaS-qualified role searches in the US and UK: four Jobs queries, followed by 12 employer News queries. The dated [run note and exact lens](https://github.com/forma-norden/buying-window-signal-scorer/blob/main/docs/live-run-2026-09-28.md) are in the repo.

| Account | Signal from job description | Score | News points |
| --- | --- | ---: | ---: |
| [Safe Software](https://www.safe.com/careers/) | VP, Revenue Operations; CRM not fully configured and AI tooling stack unevaluated | 60 | 0 |
| [Matia](https://jobs.ashbyhq.com/matia/1b579e8a-0eb6-4c15-90d3-851786caac65) | First dedicated RevOps hire, building GTM foundation | 60 | 0 |
| [NetBox Labs](https://jobs.ashbyhq.com/netboxlabs/6db20463-5f41-4aaa-8118-081c76e4f01f) | Senior Sales Ops role with GTM systems architecture | 60 | 0 |

We checked the employer-controlled career or ATS pages separately on 28 September. Those links can change as roles close. The three accounts received the same points for different reasons; a salesperson still needs to confirm employer identity, current need, ICP fit and an appropriate offer. The scan does **not** show that any of them are buying software.

## The 100-point false positive

Our original news rule searched the headline for the company name and event words. It was too generous for a short name. A result about the UK National Institute for Health and Care Excellence was paired with a Jobs result attributed to NICE software. The formula then added news and convergence points and placed NICE at 100.

We changed the rule so one-word ambiguous names and snippet-only mentions are treated as low-confidence. The candidate article remains inspectable, but its news and convergence points are zero. NICE ended at **45** from a dated job title alone. A regression test covers that exact failure.

This was more consequential than tuning a weight from 20 to 25. A precise-looking score can hide an identity mistake. We would rather see “review company identity” next to a plausible listing than have an unexplained top account in an export.

## Try the local demo

The demo uses explicitly fictional response data and makes no paid calls:

```bash
git clone https://github.com/forma-norden/buying-window-signal-scorer
cd buying-window-signal-scorer
python -m venv .venv
python -m pip install -e .
python -m buying_window.cli serve
```

Open `http://127.0.0.1:8765` and click **Explore demo**. To run live queries, copy `.env.example` to `.env`, add `SEARCHAPI_API_KEY`, and check the request estimate before starting. The app caps attempts at 150, including retries, and marks partial runs when a request fails. It can export CSV/JSON and replay a redacted local response archive without another API call.

The key stays local and is excluded from Git. The public repository contains code, a fictional fixture, the dated run methodology and tests; it does not contain the live API responses. Search coverage and results will change on a future run, and request count is not a dollar cost estimate for your SearchApi plan.

If you use this for outbound, make the **original posting** the start of account research, not the end. Confirm the employer, date and mandate, check your CRM, then decide whether any contact is warranted. A score can help choose what to read next. It should not write the buyer's story for you.

**Disclosure:** SearchApi supplied API credits for this Developer Ambassador collaboration. Forma Nôrden chose the use case and reports the failure and limits alongside the results. [SearchApi](https://www.searchapi.io/?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) supplies the Google Jobs and News data used by the project.
