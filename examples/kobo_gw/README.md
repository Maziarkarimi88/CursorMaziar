# KOBO well-monitoring tables

De-identified outputs from `python3 tools/kobo_gw.py`. No owner names or phone numbers.

Well identity is **15 m GPS first**, then owner/caretaker names cleaned (trim, extra spaces) and matched at **≥ 90%** similarity — not exact spelling. `cluster_id` runs **01 … N**. The working file `kobo_monitoring_clusters.csv` keeps every original KOBO column (gitignored: names/phones). See `cluster_monitorings.png`. Cleaning: `docs/KOBO_DATA_CLEANING.md`.

`dbscan_chains_review.csv` lists 15 m DBSCAN groups that mixed two or more courtyards. Use `well_id` (not `dbscan_id`) for hydrographs. ArcGIS: `docs/ARCGIS_WELL_HYDROGRAPHS.md`.
