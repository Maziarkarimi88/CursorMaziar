# START HERE

The GIS join is done. Build the Pulse-dark dashboard from here.

1. **`docs/AFTER_JOIN_BUILD.md`** — remaining steps.
2. **`design/pulse-jica-preview.html`** — open in a browser.
3. **`docs/pulse-theme.json`** — hex colors.

## Progress rule (do not break this)

Each of the **14 projects is independent**. `PROGRESS_PCT` / `Physical_Progress_Percentage` is that project’s physical works only.

Do **not** show 27.7%, an irrigation total, a watershed total, or a site total (SITE-01 is **not** 49%).

- Headline **Physical works** tile = empty until you click **one** list row, then that row’s % only (IS-01 → 13%, WSM-01 → 85%).
- Bar chart = **Features**, one bar per `Scheme_UID`.
- List / pop-up = that row’s %.

Unfiltered roll-ups (no progress mix-in): **14 · 9 · $2,294,514 · 12,225 ha · 15,887 HH · 97.3 km**
