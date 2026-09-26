# JICA Schemes Dashboard

Dark (MetroTel Pulse) ArcGIS Dashboard for the 14 JICA irrigation + watershed schemes.

Join is complete on the three GIS layers. Continue here:

1. [`docs/AFTER_JOIN_BUILD.md`](docs/AFTER_JOIN_BUILD.md) — publish + visualize; **Physical works** is per project only
2. [`design/pulse-jica-preview.html`](design/pulse-jica-preview.html) — Pulse layout mock
3. [`docs/pulse-theme.json`](docs/pulse-theme.json) — colors and expected totals
4. [`design/icons/`](design/icons/) — KPI SVGs; how to attach: [`docs/ADD_KPI_ICONS.md`](docs/ADD_KPI_ICONS.md)

## Data

| File | What it is |
| --- | --- |
| [`data/schemes_dashboard.csv`](data/schemes_dashboard.csv) | 14 scheme rows including `PROGRESS_PCT` |
| [`data/raw_Both_Jica_Irrigation_and_WSM_Schemes_abc3.csv`](data/raw_Both_Jica_Irrigation_and_WSM_Schemes_abc3.csv) | Table you joined (Excel-style names) |
| [`data/JICA_Lines_attributes.csv`](data/JICA_Lines_attributes.csv) | Canal + riverbank checklist |
| [`data/JICA_Areas_attributes.csv`](data/JICA_Areas_attributes.csv) | Area checklist |
| [`data/JICA_Points_attributes.csv`](data/JICA_Points_attributes.csv) | Structure checklist |

KPIs use the 14-row table only. **Physical works** is never totaled or averaged across projects. The green tile stays empty until one list row is selected, then that project’s `%` only.
