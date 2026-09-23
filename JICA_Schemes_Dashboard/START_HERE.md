# START HERE

This pack builds the **JICA Irrigation & Watershed** dashboard in ArcGIS Online using the MetroTel Pulse dark template.

## Open these three files first

1. **`docs/UPLOAD_AND_VISUALIZE.md`** — numbered upload + visualization steps (Pro → publish → web map → dashboard).
2. **`design/pulse-jica-preview.html`** — open in a browser. This is the dark layout to copy (six KPIs, map left, pie / bar / list right).
3. **`docs/pulse-theme.json`** — copy-paste hex colors.

## Then follow this order

1. Confirm your geodatabase fields (`Scheme_UID`, `Pair_ID`, `Program`, `Feature_Role`, `Feature_Name`, `Asset_Name`).
2. XY-event `data/schemes_dashboard.csv` as `JICA_Schemes` (14 points). Fix blank `LON` on `JICA-WSM-03`.
3. Join scheme fields onto areas / lines / points on `Scheme_UID`.
4. Symbolize teal = irrigation, gold = watershed. Publish **one** feature service with four layers.
5. Dark web map → Create app → Dashboards → Theme Dark → Pulse hex.
6. Map + always-on **Map legend** element.
7. Six indicators on `JICA_Schemes` only (not on structures).
8. Pie (Program), bar (awarded cost by province), scheme list (zoom / flash).
9. Header selectors: Program, Status, Province, Site (`Pair_ID`), Asset.
10. Share the layer + map + dashboard together.

Unfiltered KPIs must read **14 · 9 · $2,294,514 · 12,225 ha · 15,887 HH · 97.3 km**.

The three `data/JICA_*_attributes.csv` files are **attribute checklists**. They have no coordinates. Do not upload them as new geometry.
