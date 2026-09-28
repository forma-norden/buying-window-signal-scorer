# How to find a real reason to contact a company this week

*A practical way to connect public hiring and company news to the problem your offer solves.*

“They are growing” is rarely enough to write a useful first message. Growth can mean a new territory, a delayed rollout, a team without a manager, or simply another role on a careers page. Those situations create different needs.

The better question is: **what changed at this company, and does that change make our help relevant?**

Job descriptions are a surprisingly direct place to look. A title tells you the function. The description can tell you what the person is expected to build, fix, or expand. Company news can provide another piece of context. The two sources are public, dated when the publisher supplies a date, and available for a prospect to verify.

That was the idea behind [Buying Window Signal Scorer](https://github.com/forma-norden/buying-window-signal-scorer), a small open-source app we built at Forma Nôrden. It searches Google Jobs and Google News through SearchApi, then assembles a research queue with the original sources beside each company. It works with a watchlist or can discover employers from roles that matter to your offer.

## Start with your offer, not a generic intent label

Imagine three teams:

- A logistics software company wants to find distributors opening a new market. Operations roles, new locations, and distribution expansion matter.
- A recruiting firm wants to find companies building a marketing function. “First marketing hire” or a cluster of relevant roles matters more than a funding headline alone.
- A systems consultancy wants to find companies hiring a new head of operations to standardise processes. The mandate in the job description matters more than the title by itself.

All three can use the same data sources. They should **not** use the same definition of a good lead. The scorer therefore offers editable profiles for growth, team buildout, new leadership, and revenue operations. Each profile is a starting hypothesis. You can change the job queries, strong and adjacent titles, mandate phrases, news events, market, and scoring weights in the dashboard.

## What the queue actually tells you

The default 100-point score gives up to 40 points for a relevant title and job-description mandate, 20 for a recent job, 25 for a recent company event, and 15 when both signals are present. Open a company and you see the job, article, dates, matched text, score parts, and any identity flags. Older or undated material can remain visible without earning recency points.

In a small live check on 28 September 2026, the growth profile used five API requests: two job searches and news checks for three selected employers. The job results contained 19 relevant, deduplicated listings. The three selected employers earned 45 points each from recent role matches; no news result qualified for points. This is an observation about one bounded search, not a measurement of market demand or buying intent. Its value was to show exactly which companies warranted a closer look and why the news did not strengthen the case.

If the description says the new hire will open a territory or implement a system, read the full posting and check the employer. If the description only lists routine responsibilities, the timing case may be weak, even if the title matches. A score should shorten the path to that judgment, not replace it.

## A repeatable weekly practice

1. Write down the change your offer can help with. Be as specific as “opening a second distribution centre” or “building a first marketing operations team.”
2. Choose the roles and company events that would make that change visible. Search one market first.
3. Run a small scan and inspect the top source documents. Confirm that the job belongs to the employer named in the result.
4. Record the useful companies in your existing account workflow. Keep the job or article link, the date, and the actual mandate.
5. Re-run the same profile later. The tool marks evidence first seen in *your scan results*, so you can review the changes without mistaking that label for a publication date.

The app displays an API request estimate before each run and enforces an attempt cap. It also exports CSV and JSON for teams that want to bring the evidence into their own process. SearchApi currently offers [100 free requests at signup](https://www.searchapi.io/pricing); [get a key here](https://www.searchapi.io/?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) and the [repository has the setup steps](https://github.com/forma-norden/buying-window-signal-scorer). The app runs locally, so you can try one profile and inspect the sources yourself.

The test for a buying window is not whether a dashboard gives a company a high score. It is whether you can explain the change in one accurate sentence, point to the source, and connect it to something you can genuinely help with.

*Disclosure: SearchApi supplied API credits for this project. Forma Nôrden built the application and scoring rules.*
