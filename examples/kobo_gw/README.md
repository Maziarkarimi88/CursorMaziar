# KOBO well-monitoring tables

De-identified outputs from `python3 tools/kobo_gw.py`. No owner names or phone numbers.

Well identity is **15 m GPS first** (complete linkage), then an owner-name cross-check. Common names are not used as the well key. Start with `CLEANING.md`. Cleaning rules: `docs/KOBO_DATA_CLEANING.md`.

`dbscan_chains_review.csv` lists 15 m DBSCAN groups that mixed two or more courtyards. Use `well_id` (not `dbscan_id`) for hydrographs. ArcGIS: `docs/ARCGIS_WELL_HYDROGRAPHS.md`.
