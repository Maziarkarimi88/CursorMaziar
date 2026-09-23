# START HERE

The GIS join is done. Build the Pulse-dark dashboard from here.

1. **`docs/AFTER_JOIN_BUILD.md`** — remaining steps (verify join → publish → 7 KPIs).
2. **`design/pulse-jica-preview.html`** — open in a browser (dark layout + progress tile).
3. **`docs/pulse-theme.json`** — hex colors and expected totals.

Unfiltered KPIs must read:

**14 · 9 · 27.7% · $2,294,514 · 12,225 ha · 15,887 HH · 97.3 km**

The seventh tile is **Awarded progress**: Average of `PROGRESS_PCT` on the 9 awarded rows only, from the 14-row `JICA_Schemes` table — never from canals, catchments, or structures.

Use `data/schemes_dashboard.csv` as that 14-row source (commas stripped, `PROGRESS_PCT` filled, dates ISO).
