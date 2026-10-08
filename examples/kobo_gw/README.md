# KOBO well-monitoring tables

De-identified outputs from `python3 tools/kobo_gw.py`. No owner names or phone numbers.

Well identity is **15 m GPS first** (complete linkage) → `well_id` / `site_id`. Different owner/caretaker names inside that radius get different `cluster_id`s (spelling drift stays one cluster). Common names are not used as a nationwide key. Start with `CLEANING.md`. Use `wells_clusters.csv` / `visits_clusters.csv` for hydrographs. Cleaning rules: `docs/KOBO_DATA_CLEANING.md`.

`dbscan_chains_review.csv` lists 15 m DBSCAN groups that mixed two or more courtyards. Use `well_id` (not `dbscan_id`) for hydrographs. ArcGIS: `docs/ARCGIS_WELL_HYDROGRAPHS.md`.
