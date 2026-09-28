---
title: "How to Find B2B Buying Signals in Job Posts and Company News"
slug: buying-window-signals-jobs-news
description: "Find companies whose hiring briefs and recent news point to a relevant change. See how to search, score and qualify the evidence with an open-source SearchApi tool."
category: Sales Prospecting
cluster: Signal-based prospecting
intent: practitioner implementation
date: 2026-09-28
status: draft awaiting site editorial release
---

# How to find B2B buying signals in job posts and company news

A company hiring an operations manager might be replacing someone. It might be opening a new market, building its first regional team or trying to fix a process that stopped scaling. The title gets the company onto a list. The job description can reveal which of those changes is happening.

That distinction matters if you sell to businesses. A logistics software vendor, a recruiter and a systems consultancy could all be interested in the same employer, but each needs a different reason to pursue it. A generic “hiring” alert cannot make that decision for them.

We built [Buying Window Signal Scorer](https://github.com/forma-norden/buying-window-signal-scorer), a small open-source Python app, to make the research repeatable. It searches [Google Jobs](https://www.searchapi.io/docs/google-jobs?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) and [Google News](https://www.searchapi.io/docs/google-news?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) through SearchApi, ranks companies under rules you can edit, and keeps the original sources beside every score.

**TL;DR:** Start with a change your offer can help with. Search for the roles and job-description language that would reveal it. Check company news for context, then open the sources before deciding whether to act. The [tool](https://github.com/forma-norden/buying-window-signal-scorer) turns that process into a source-linked shortlist you can run yourself.

**In this article:** [Choose a signal](#choose-the-change-before-the-company) · [Search Jobs and News](#how-the-search-finds-and-checks-companies) · [Read the score](#a-score-you-can-check-against-the-sources) · [Use the result](#turn-a-result-into-an-account-note) · [Request budget](#what-a-search-costs-in-requests) · [Run the tool](#run-your-own-search) · [FAQs](#frequently-asked-questions)

## Choose the change before the company

The useful question is not “which companies are hiring?” It is “which companies are hiring to do work we can help with?” Define that work before you write a search query.

| Your offer | Change worth finding | Clue in a job post | News that could add context |
| --- | --- | --- | --- |
| Logistics or process software | A new market or facility | Operations role tasked with opening a location or scaling a network | Market entry or facility announcement |
| Recruiting or training | A new function or growing team | First hire, team lead or several roles in the same function | Funding or announced hiring plans |
| Implementation services | A leader changing a process | Senior role with a systems or transformation mandate | New executive appointment |
| CRM or revenue systems | New ownership of commercial operations | Sales-operations role that will implement or rebuild a stack | Commercial leadership change |

The same company can be relevant to one offer and irrelevant to another. That is why the app's growth, team buildout, new leadership and revenue-operations profiles are starting points. Each contains job queries, strong and adjacent title matches, description phrases, news events and score weights. You can change them in the dashboard without editing code.

If your offer is warehouse planning, “operations manager” is a useful search term but a weak conclusion. “Open a new distribution centre” or “scale our fulfilment network” is closer to the work you solve. Put those phrases in the profile and judge the full posting against them.

## How the search finds and checks companies

In **discovery mode**, the app sends the selected role queries to SearchApi's Google Jobs engine for one market. It groups the returned listings by employer, removes duplicate jobs and chooses a bounded number of companies for a News search. The default profile uses two Jobs queries and checks news for up to six employers.

In **watchlist mode**, you provide the companies first. The app searches for each name alongside the relevant roles, then checks news for the same employers. This is useful when your target accounts are already known and you want to know whether any of them show a new hiring or company event. Aliases can be entered for companies that appear under different names.

The two SearchApi requests have a simple shape:

~~~json
{"engine":"google_jobs","q":"operations manager","location":"United States","gl":"us"}
{"engine":"google_news","q":"\"Example Company\" (funding OR expansion OR appoints)","gl":"us"}
~~~

The Jobs search discovers candidates; the News search adds context to the selected companies. The app checks the employer returned with a job before attaching that listing to an account. For news to earn points, the headline must name the company and contain one of the configured event phrases. A passing mention in an article excerpt is not enough.

That sequencing also controls cost. The tool does not search news for every listing it sees. It searches news for the employers it has selected under your profile and company limit. The dashboard displays the planned request count before you run anything.

## A score you can check against the sources

The default growth profile has four score parts. A strong role title can earn **25 points**; a matching mandate in the job description can add **15**. A recent job can earn **20** more. A dated, matched company news event adds **25**, with **15** for having both qualified sources. The maximum is 100, and you can change the four weights.

The bundled sample uses a **fictional** company, Harbor Foods, so anyone can see the complete path without API calls. Its recent operations-manager posting includes a team-building mandate for a new market. An expansion headline names the company. Open the result and you can see the job, article, dates, matched phrases and the `40 + 20 + 25 + 15` breakdown.

That example shows what the highest score requires. A current title match without a description mandate or matched news earns 45 under the default rules. Both results are visible, but they call for different amounts of follow-up research.

We checked the live integration on **28 September 2026** with a three-company growth scan. Two Jobs requests returned **19 relevant, deduplicated listings**. Three News requests checked the selected employers, making **five SearchApi requests** in total. The selected companies scored 45 from recent role matches. The [dated run note](https://github.com/forma-norden/buying-window-signal-scorer/blob/main/docs/live-run-2026-09-28.md) records the settings and counts.

The valuable distinction is between a role that gets your attention and a mandate that gives you something specific to investigate. The score makes that distinction visible beside the source links. You still decide whether the company is in your market and whether the change affects the work you sell.

## Turn a result into an account note

Open the top result before exporting it. A useful note takes five lines:

1. **Change:** the exact responsibility or company event that matters.
2. **Source:** the posting or article link and its date.
3. **Employer:** the organisation that actually owns the job, confirmed against the source.
4. **Offer fit:** one sentence connecting the change to a problem you can solve.
5. **Next question:** what you still need to learn before contacting anyone.

For example, if a posting says a new operations lead will open a regional distribution centre, a warehouse software vendor could investigate the rollout, systems and owner of that work. A recruiter could instead look at which roles the new lead needs to hire. The same document can support two different account hypotheses. Keeping the quoted responsibility and source link prevents either team from turning a vague “growth” label into a confident but empty pitch.

This is where the tool fits in Forma Nôrden's open-source library. The [Signal-Based List Building Workflow](https://formanorden.com/open-source/signal-based-list-building-workflow/) helps choose sources and target lists. This scorer searches and prioritises relevant public evidence. The [Buying Window Signal Workflow](https://formanorden.com/open-source/buying-window-signal-workflow/) helps decide who owns a verified signal and what should happen next.

## What a search costs in requests

SearchApi currently lists [100 free requests on signup](https://www.searchapi.io/pricing?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com). The default discovery profile plans **two Jobs requests plus up to six News requests**, or at most eight initial searches. A three-company run plans five. The app enforces a configurable attempt cap, including retries, and shows the estimate before a live scan.

At eight initial requests, 100 requests could cover twelve full default scans with four left over if there were no retries or other usage. Use that as a trial-planning calculation, then choose the market, company count and profile that answer a real question for your team.

The app archives redacted raw responses locally. If you change the scoring rules, you can replay an archive without making the same API calls again. Run a later live scan with the same settings and the app highlights items newly seen in your results. CSV and JSON exports let you carry the shortlist into your existing research process.

## Run your own search

The project is [MIT licensed on GitHub](https://github.com/forma-norden/buying-window-signal-scorer). Get a [SearchApi key](https://www.searchapi.io/?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com), then follow the [repository quickstart](https://github.com/forma-norden/buying-window-signal-scorer#get-started) to install the Python app and start the local dashboard.

Choose **Growth & expansion**, **Team buildout**, **New leadership** or **Revenue operations**. Pick one market and use the small discovery size first. Open the highest-ranked source documents, then narrow the profile to the type of work your offer addresses. You can also start from a watchlist if you already know which companies to investigate.

No key is needed to click **View growth sample** and inspect the fictional example. A live scan uses your key from a local environment variable or ignored `.env` file.

## Frequently asked questions

### What counts as a buying signal in a job posting?

The most useful part is a responsibility that points to a change: building a team, entering a market, implementing a system or taking ownership of a new function. A relevant title helps find the posting; the description tells you what the employer wants that person to do. Read the full source before connecting it to your offer.

### Why add company news to a jobs search?

An expansion, investment or leadership announcement can explain the timing of a hire. The app awards news points only when a dated headline names the employer and matches an event in the chosen profile. Jobs and news can each be useful on their own; together they may give you a more specific question to investigate.

### Can I search a list of companies I already work with?

Yes. **Check my watchlist** accepts one company per line and optional aliases. The dashboard estimates Jobs and News requests from the size of your list before you run it.

### Does a high score mean a company is ready to buy?

The score is an order for reading source documents under the profile you chose. It does not know your commercial fit criteria, whether the project has a vendor budget or whether the work is already committed to someone else. Those decisions belong in the account note and the next conversation.

*SearchApi supplied API credits for this project. Forma Nôrden built the app, scoring rules and article.*
