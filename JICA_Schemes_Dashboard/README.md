# JICA irrigation + watershed scheme tracker

HTML dashboard for the 14 JICA 134/JCA packages (7 irrigation + 7 watershed). Each scheme draws a **polygon** (command area or watershed) and a **line** (canal or check-dam alignment). Click a row or a feature to zoom the map to that scheme’s combined extent.

## Open the dashboard

```bash
cd JICA_Schemes_Dashboard
python3 -m http.server 8770
```

Then open `http://127.0.0.1:8770/`.

## Data

| File | Role |
|---|---|
| `data/schemes_dashboard.csv` | Attribute table (upload layer) |
| `data/schemes_areas.geojson` | One polygon per `SCHEME_UID` |
| `data/schemes_lines.geojson` | One line per `SCHEME_UID` |
| `data/raw_Both_Jica_Irrigation_and_WSM_Schemes_72ae.csv` | Latest raw tracker |

Rebuild:

```bash
python3 scripts/clean_schemes.py
python3 scripts/build_geometries.py
python3 scripts/test_scheme_geometries.py
```

X/Y on the CSV are district centroids until site GPS arrives. The GeoJSON is a stand-in from those centroids plus `AREA_HA` / `CANAL_KM`. Replace both GeoJSON files with surveyed features; keep `SCHEME_UID` on every record. Use **Replace areas** / **Replace lines** on the dashboard, or rebuild the embed.

Native ArcGIS Online rebuild: `agol/NATIVE_DASHBOARD.md`.
