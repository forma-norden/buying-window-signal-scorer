---
title: "A RevOps Hiring Signal Is Not Buying Intent: What 16 SearchApi Requests Actually Found"
slug: revops-hiring-signals-searchapi-account-research
description: "We built an open-source account research tool, checked 35 relevant jobs across the US and UK, and found three concrete operations mandates. Here is the scoring model, evidence, false positive, and workflow."
category: RevOps
cluster: Signal-based prospecting
intent: practitioner implementation
date: 2026-09-28
status: draft awaiting site editorial release
---

# A RevOps hiring signal is not buying intent: what 16 SearchApi requests actually found

An open RevOps role can tell you that a company is changing how it runs revenue operations. It cannot tell you that the company is about to buy your software. That distinction matters when a sales team is deciding which accounts deserve research today.

We built the [Buying Window Signal Scorer](https://github.com/forma-norden/buying-window-signal-scorer) to turn public job and news results into an *inspectable research queue*. It searches [Google Jobs](https://www.searchapi.io/docs/google-jobs) and [Google News](https://www.searchapi.io/docs/google-news) through SearchApi, shows source links and dates, and ranks accounts using rules a RevOps operator can edit. Its first live US/UK scan on **28 September 2026** made **16 API requests**, found **35 relevant, deduplicated job listings**, and shortlisted **12 employers**. Three job descriptions contained a concrete operations mandate. No news result passed our identity and recency rules, so news contributed zero points.

That last zero is a feature of the analysis. Adding a weak news match would make the leaderboard look more exciting while making the next sales action less defensible.

**TL;DR:** Public RevOps hiring is a useful *research trigger* when the posting names real systems work, its employer and date can be checked, and the account fits your market. In our 28 September scan, three descriptions met that bar, while news added no qualified evidence. The open-source dashboard keeps every score attached to the source and makes uncertain identities visible.

**In this article:** [The account question](#what-question-does-the-tool-answer) · [Live scan](#the-live-scan-three-different-60-point-accounts) · [Scoring](#how-we-score-without-hiding-the-evidence) · [False positive](#the-false-positive-that-changed-the-model) · [Review sequence](#a-practical-account-review-before-outreach) · [Cost and fit](#when-the-api-workflow-is-worth-running) · [FAQs](#frequently-asked-questions) · [Run it](#run-it-yourself)

## What question does the tool answer?

For a team selling CRM implementation, data infrastructure, revenue intelligence, or GTM systems work, the useful question is: **Which accounts have recent, verifiable signs of operational change, and what would we need to confirm before approaching them?**

Job descriptions sometimes disclose the work more clearly than an intent score: a first dedicated RevOps hire, a CRM that is not fully configured, or ownership of GTM systems architecture. A funding announcement or senior commercial appointment can add context, but only if it refers to the *same company* and happened recently. The scorer therefore keeps employer matching, evidence age, score, and ICP judgment separate.

This is a companion to Forma Nôrden's [Signal-Based List Building Workflow](https://formanorden.com/open-source/signal-based-list-building-workflow/) and [Buying Window Signal Workflow](https://formanorden.com/open-source/buying-window-signal-workflow/). The new tool gathers and prioritises candidate accounts. Those workflows help decide whether and how to route a confirmed signal.

## The live scan: three different 60-point accounts

The scan used two SaaS-qualified role searches in both the US and UK, then searched company news for the 12 selected employers. The role list, mandate phrases, weights and account cap are saved in the repository's [case-study settings](https://github.com/forma-norden/buying-window-signal-scorer/blob/main/examples/case-study-settings.json). A 60 is the maximum achieved in this sample, not a percentile or a probability of purchase.

| Account | Employer-controlled source checked on 28 September | Why it entered the research queue | Next check |
| --- | --- | --- | --- |
| [Safe Software](https://www.safe.com/careers/) | Official careers page listed VP, Revenue Operations | The job description said its CRM was not fully configured and its AI tooling stack was unevaluated | Confirm the team's current stack and whether the role owns vendor evaluation |
| [Matia](https://jobs.ashbyhq.com/matia/1b579e8a-0eb6-4c15-90d3-851786caac65) | Employer's Ashby listing | The posting described a first dedicated RevOps hire and building the GTM foundation | Check whether the hire is planned, active, or already filled |
| [NetBox Labs](https://jobs.ashbyhq.com/netboxlabs/6db20463-5f41-4aaa-8118-081c76e4f01f) | Employer's Ashby listing | The Sales Operations brief included pipeline, forecasting and GTM systems architecture | Map the actual systems remit to a relevant offer |

Each account scored 60 from a strong, recent role with a configured mandate phrase in its description. The tie hides differences that matter commercially. Safe Software's wording suggests a possible stack evaluation; Matia's suggests a foundational first hire; NetBox Labs' suggests architecture and reporting work. None of those observations establishes budget, decision authority, vendor shortlist, or permission to infer a buying timeline.

The scan found 35 matching listings in four Jobs responses, **not 35 distinct buying companies**. It carried 12 employers into the news stage. Coverage depends on the search phrasing, geography, what Google Jobs returned that day, and the one-page-per-query collection used here. This was a bounded demonstration, not an estimate of the wider market.

## How we score without hiding the evidence

The default 100-point model is deliberately small:

| Component | Points | What qualifies |
| --- | ---: | --- |
| Role relevance | 40 | A strong or adjacent title; description phrases add to this component when they describe an operations or tooling mandate |
| Job recency | 20 | A dated matching role within seven days earns 20; within 30 days earns 12 |
| Relevant company news | 25 | A dated funding or commercial leadership event with sufficient company identity confidence |
| Convergence | 15 | Both a recent job and qualified recent news exist |

An undated or older job remains visible but earns no points. A news link with an uncertain company match also remains visible, but earns no news or convergence points. The dashboard shows the job description excerpt, role, date, source link, account review flags, and each component's contribution. You can change the role queries, title terms, mandate phrases, news events, weights, locations and account ceiling for your market. **Score changes when the lens changes**; compare runs only with their settings attached.

Before sending a live request, the app estimates the upper bound. Discovery first runs Jobs searches, then at most one News search per selected employer. Watchlist mode accepts up to 50 named accounts. The hard cap is 150 HTTP attempts, including retries, and errors mark a result as partial. SearchApi's commercial plan determines the actual charge; the request estimate is not a dollar quote.

## The false positive that changed the model

Our first implementation briefly ranked **NICE** at 100/100. A Jobs result attributed a role to NICE, while Google News returned recent stories about the UK's National Institute for Health and Care Excellence. The names matched as text, but the entities did not. Giving full news and convergence points would have turned a common-name collision into a top-priority account.

We changed the scorer so short, ambiguous company names and mentions confined to a snippet are marked for identity review. Their candidate news stays visible, but scores zero. In the corrected run, NICE scored **45/100 from its job title and recency alone**, with its news match withheld. A regression test fixes that rule. The tool also flags likely recruiters and job boards, because the `company_name` field may describe an intermediary instead of the ultimate employer.

This is the boundary of automation in this project. Exact names, recent dates and a deterministic formula can make research consistent. They cannot resolve every corporate identity or turn a listing into a commercial conversation.

## A practical account review before outreach

1. **Open the original posting.** Confirm the role, employer, location and whether it is still open. Treat a relative date as a snapshot, not a permanent fact.
2. **Read the mandate.** Look for an actual operational job to be done. A generic RevOps title alone gives less direction than a description that names systems, reporting or a first hire.
3. **Check fit in your CRM.** Remove current customers, excluded industries, existing opportunities and duplicate owners. ICP fit is intentionally left as a human decision.
4. **Validate a plausible first action.** If the role owns CRM configuration, offer a relevant diagnostic or implementation perspective. If it focuses on forecasting, an infrastructure pitch may be misplaced.
5. **Record the evidence used.** Save the job URL, observed date, excerpt, settings and owner. Recheck before sending because vacancies and company circumstances change.

That process can produce a smaller, more useful list than a broad “companies hiring RevOps” export. It also gives the seller a reason to stop: if the employer, date or mandate cannot be verified, the account should not receive a signal-based message.

## When the API workflow is worth running

For a handful of named accounts, a person may be faster: inspect the official careers pages and record a reason for follow-up in the CRM. The API workflow becomes more useful when an operator needs to repeat the same role and news checks across a watchlist, export a consistent evidence table, or review a discovery queue with a team. It is especially useful when the team wants to compare the *same configured rules* across scans rather than rely on a spreadsheet of undocumented judgement calls.

The economics are bounded by requests, not a fictional return-on-investment claim. Our case-study run used **four Jobs requests plus twelve News requests**. A 50-account watchlist across two locations has a planned upper bound of **150 initial searches**: 100 Jobs and 50 News. Retries also count toward the hard attempt cap, so a run can stop or be partial before all planned results arrive. SearchApi plan prices and credits can change; check your account's current terms before scaling. The tool cannot establish pipeline impact because we did not run an outreach or conversion experiment.

The commercially useful output is a research queue with a **reason to proceed or disqualify**, not a list of supposed active buyers. An account with a current, employer-confirmed systems mandate may merit a relevant CRM or RevOps conversation. An account represented by a recruiter, an ambiguous news match or an undated posting may be removed from outreach even if its title contains the right words.

## Frequently asked questions

### Does a RevOps job posting mean the company is buying software?

No. It may signal an internal project, a replacement hire or routine team growth. A description that names a CRM configuration or systems architecture mandate is more informative than a title alone, but you still need to check employer identity, present systems, budget and the role's decision authority. The scorer deliberately calls its output a research priority.

### Why did the tool award zero news points in the live scan?

The news results did not satisfy the configured combination of a recent date, relevant event and sufficiently confident company match. A result about a same-name organisation could be inspected, but it could not improve an account's rank. This makes the scan less dramatic and the evidence chain easier to defend.

### Should I run discovery or a watchlist?

Use a watchlist when you already have a target-account set and need a bounded update; review one employer at a time and use aliases for known naming variants. Use discovery when you need to find employers from current role searches. Either way, review the request estimate first and record the settings with the results. Neither mode replaces a CRM exclusion check or first-party employer verification.

## Run it yourself

The [MIT-licensed repository](https://github.com/forma-norden/buying-window-signal-scorer) includes the local dashboard, Python CLI, fictional demo fixture, replayable raw-response archive format, CSV/JSON export, tests and a [dated run note](https://github.com/forma-norden/buying-window-signal-scorer/blob/main/docs/live-run-2026-09-28.md). Python 3.11+ is required.

```bash
git clone https://github.com/forma-norden/buying-window-signal-scorer
cd buying-window-signal-scorer
python -m venv .venv
python -m pip install -e .
python -m buying_window.cli serve
```

Open `http://127.0.0.1:8765` and try the demo without a key. For live queries, copy `.env.example` to `.env` and add a SearchApi key locally. The key is sent in an authorization header, excluded from Git and redacted from archives. A rerun will produce different results because the sources are live.

**Disclosure:** SearchApi supplied API credits for this collaboration. Forma Nôrden selected the use case, built the scorer and reports the results and limitations here. [SearchApi](https://www.searchapi.io/?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) provides the Jobs and News endpoints used by the tool.
