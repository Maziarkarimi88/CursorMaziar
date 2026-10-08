# KOBO well-monitoring tables

De-identified outputs from `python3 tools/kobo_gw.py`. No owner names or phone numbers.

Well identity is **15 m GPS and the same owner/caretaker**. `cluster_id` runs **01 … N**. The working file `kobo_monitoring_clusters.csv` keeps every original KOBO column and adds `cluster_id`, `n_monitorings`, `gps_group`, `split_by_owner` (that file is gitignored because it has names/phones). See `cluster_monitorings.png`. Cleaning: `docs/KOBO_DATA_CLEANING.md`.

`dbscan_chains_review.csv` lists 15 m DBSCAN groups that mixed two or more courtyards. Use `well_id` (not `dbscan_id`) for hydrographs. ArcGIS: `docs/ARCGIS_WELL_HYDROGRAPHS.md`.
