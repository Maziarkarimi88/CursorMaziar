# JICA irrigation + watershed scheme table

Attribute table for the 14 JICA 134/JCA packages (7 irrigation + 7 watershed). Use this with your own polygon and line feature classes — this folder does not generate a dashboard or stand-in geometry.

| File | Role |
|---|---|
| `data/schemes_dashboard.csv` | Clean attributes (`SCHEME_UID`, status, cost, HH, LON/LAT) |
| `data/raw_Both_Jica_Irrigation_and_WSM_Schemes_72ae.csv` | Latest raw tracker |

Rebuild: `python3 scripts/clean_schemes.py`

X/Y on the CSV are **district centroids** until you add site GPS. Join to your surveyed layers on `SCHEME_UID` (`JICA-IS-01` … `JICA-WSM-07`).

## Zoom to each scheme in ArcGIS

Each irrigation and each watershed scheme has a **polygon** (command area or watershed) and a **line** (canal or check-dam alignment).

1. Keep `SCHEME_UID` on both layers (or join this CSV onto them).
2. In the web map / dashboard, a list or selector on `SCHEME_UID` should **Filter** both layers and **Zoom** to the **union extent** of that scheme’s polygon and line — not the point centroid alone.
3. Optional: a site selector on `PAIR_ID` zooms to both the IS and WSM pair at the same place.

Review notes: `DATA_REVIEW.md`.
