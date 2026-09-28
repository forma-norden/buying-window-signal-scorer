# Find B2B Buying Windows in Job Posts and Company News

*A practical way to turn public company changes into a useful account shortlist.*

“They are growing” is a weak reason to contact a company. “They are hiring someone to build the operations team for a new market” is much more useful. The second statement tells you what changed, which team owns it, and where to verify it.

The most revealing line is often inside the job description. A title names a function. The brief explains the work: open a territory, standardise a process, build a team, or replace a system. A company announcement can add context, but the job itself is often the better starting point.

We built [Buying Window Signal Scorer](https://github.com/forma-norden/buying-window-signal-scorer) at Forma Nôrden to make that research repeatable. This small, open-source app uses SearchApi's Google Jobs and Google News APIs. It finds relevant roles, checks news about the employers, ranks the companies under a profile you choose, and keeps the original sources with every result.

## One source, different opportunities

The same hiring signal can matter to several teams for different reasons.

- **A recruiter** might look for a first marketing hire or a growing engineering team.
- **An implementation partner** might look for a new operations leader tasked with changing systems.
- **A logistics vendor** might look for operations roles tied to a new facility or market.

None of them should use a generic “hiring equals intent” rule. Each needs its own job titles, description phrases and company events. The app ships editable profiles for growth, team buildout, new leadership and revenue operations; a team can narrow any profile to its own offer in the dashboard.

## Read the evidence, not just the score

The default ranking gives up to 40 points for a relevant role and description mandate, 20 for a recent job, 25 for matching company news, and 15 when both sources qualify. A dated title match alone earns 45. A stronger result needs a meaningful job description and, for the highest score, a separate company event.

Open a result and you see the posting, article, dates and phrases that produced those points. That makes the shortlist useful even when the final decision is to pass on a company. You can tell whether the work in the posting is something your offer actually addresses.

For a small live check on 28 September 2026, our growth profile used five SearchApi requests and found 19 relevant, deduplicated job listings. It checked news for three selected employers. The run showed how quickly a broad role search can produce a shortlist, and why the full job brief is the next document to read. The [public repository](https://github.com/forma-norden/buying-window-signal-scorer) includes the settings, tests and run note.

## Make it a weekly research habit

1. **Name one change your offer can help with.** “Opening a second distribution centre” is more useful than “growth.”
2. **Choose the visible clues.** Which roles, mandate phrases and announcements would signal that change?
3. **Search one market.** Start with a small discovery run or a short watchlist. The app shows the API request estimate before it searches.
4. **Open the top sources.** Confirm the employer, read the whole posting, and check whether the news is about the same company.
5. **Keep an account note.** Save the source, date, relevant line and one question you still need answered.

Re-run the same profile later and the app highlights items newly seen in your results. Export the shortlist to CSV or JSON if your team works elsewhere.

The result is a better first conversation. Instead of “I noticed you are growing,” you can discuss a specific initiative disclosed in a public source and explain why your experience is relevant to it.

The app is [MIT licensed on GitHub](https://github.com/forma-norden/buying-window-signal-scorer). [Get a SearchApi key here](https://www.searchapi.io/?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com) to run your own Jobs and News search; SearchApi currently lists [100 free requests on signup](https://www.searchapi.io/pricing?utm_source=dev&utm_medium=ambassador&utm_campaign=formanorden.com).

*SearchApi supplied API credits for this project. Forma Nôrden built the app and scoring rules.*
