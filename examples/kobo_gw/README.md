# KOBO well-monitoring tables

De-identified outputs from `python3 tools/kobo_gw.py`. No owner names or phone numbers.

Well identity is **15 m GPS first** (complete linkage), then owner/caretaker split. `cluster_id` runs **01 … N**. The one working file is `kobo_monitoring_clusters.csv`: original KOBO columns (no owner/phone) plus `cluster_id`, `n_monitorings`, `gps_group`. See `cluster_monitorings.png`. Cleaning: `docs/KOBO_DATA_CLEANING.md`.

`dbscan_chains_review.csv` lists 15 m DBSCAN groups that mixed two or more courtyards. Use `well_id` (not `dbscan_id`) for hydrographs. ArcGIS: `docs/ARCGIS_WELL_HYDROGRAPHS.md`.
