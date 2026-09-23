# JICA Schemes Dashboard

Dark (MetroTel Pulse) ArcGIS Dashboard for the 14 JICA irrigation + watershed schemes.

## Start here

1. Open the click-path: [`docs/UPLOAD_AND_VISUALIZE.md`](docs/UPLOAD_AND_VISUALIZE.md)
2. Open the layout mock: [`design/pulse-jica-preview.html`](design/pulse-jica-preview.html)
3. Copy colors from [`docs/pulse-theme.json`](docs/pulse-theme.json)

Publish **from your geodatabase**. The GIS CSVs are attribute checklists and have no coordinates.

## Data

| File | What it is |
| --- | --- |
| [`data/schemes_dashboard.csv`](data/schemes_dashboard.csv) | 14 scheme rows for every KPI / chart / list |
| [`data/JICA_Lines_attributes.csv`](data/JICA_Lines_attributes.csv) | Canal + riverbank attributes (15) |
| [`data/JICA_Areas_attributes.csv`](data/JICA_Areas_attributes.csv) | Command / incremental / catchment attributes (36) |
| [`data/JICA_Points_attributes.csv`](data/JICA_Points_attributes.csv) | Structure attributes (38) |

Join GIS layers to the scheme table on `Scheme_UID`. Never sum cost from exploded structures.

## Also in this folder

- [`docs/JICA_DARK_DASHBOARD_BUILD.md`](docs/JICA_DARK_DASHBOARD_BUILD.md) — shorter Pulse theme notes
- [`design/metro-tel-pulse-reference.webp`](design/metro-tel-pulse-reference.webp) — original Pulse screenshot
