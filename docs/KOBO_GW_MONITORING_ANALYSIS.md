# Using the FAO KOBO groundwater monitoring export

The cleaned export is one **visit per row**. Enumerators resubmitted the whole form; the weekly repeat group is empty. Rebuild wells from a **15 m GPS cluster** (complete linkage). Owner name is a **cross-check** only — the same personal name appears in many provinces. Cleaning rules are in [`KOBO_DATA_CLEANING.md`](KOBO_DATA_CLEANING.md).
ArcGIS: [`ARCGIS_SAME_WELL_CLUSTERING.md`](ARCGIS_SAME_WELL_CLUSTERING.md),
hydrographs: [`ARCGIS_WELL_HYDROGRAPHS.md`](ARCGIS_WELL_HYDROGRAPHS.md).

**DTW** (questions 14, 15, 24) is depth to water in metres. Larger = deeper = less water, unless an enumerator entered water-column height instead.

## Run

Put the export at `data/kobo/groundwater_monitoring.csv` (gitignored; owner names and phones stay off GitHub).

```bash
pip install -r requirements.txt
python3 tests/test_kobo_gw.py
python3 tools/kobo_gw.py --csv data/kobo/groundwater_monitoring.csv
```

| Output | What it is |
|--------|------------|
| `examples/kobo_gw/wells_unique.csv` | One row per well: static attributes, first/last DTW, recalled and measured change, QA exclude flag |
| `examples/kobo_gw/visits.csv` | Visit panel: `well_id`, dates, DTW, `dbscan_id`, `split_review`, `hydro_class` |
| `examples/kobo_gw/dbscan_chains_review.csv` | DBSCAN 15 m groups that mixed two or more 15 m wells (split these) |
| `examples/kobo_gw/dbscan_chain_visits.csv` | Visits inside those groups, already tagged with the split `well_id` |
| `examples/kobo_gw/qa_flags.csv` | One row per flag instance |
| `examples/kobo_gw/perception_vs_measured.csv` | Reported Q30 vs tape/rope class |
| `examples/kobo_gw/province_stats.csv` | Usable-well counts and median DTW change by province |
| `examples/kobo_gw/nearby_other_wells.csv` | Different wells with centroids ≤ 15 m (owner cross-check) |
| `examples/kobo_gw/same_owner_splits.csv` | Same owner, more than one 15 m site |
| `examples/kobo_gw/CLEANING.md` | Identity counts and outlier rules from the last run |
| `examples/kobo_gw/CLUSTER_COMPARE.md` | 15 m wells vs GIS DBSCAN (1,041 noise / 2,339 clustered is ~5.2 m) |
| `examples/kobo_gw/RADIUS_CHOICE.md` | Why 15 m (not 5 / 10 / 12 / 20) is the same-well radius |
| `examples/kobo_gw/SUMMARY.md` | Counts and medians written by the last run |
| `figures/kobo_gw/map_wells.png` | Unique-well map (size = visits) |
| `figures/kobo_gw/box_dtw_change_by_*.png` | Recalled DTW change by province, distance, intervention |
| `figures/kobo_gw/perception_vs_measured.png` | Heatmap of Q30 vs measured class |
| `figures/kobo_gw/hydrographs_longest12.png` | Twelve longest series (y inverted: 0 at top) |
| `figures/kobo_gw/hydrographs_8plus.pdf` | Every well with ≥8 unique dates |

Recalled change = typical WT before − latest measured DTW. **Positive means the water is shallower now.** Impact medians drop wells flagged for unit confusion, DTW deeper than well depth, DTW > 100 m, or distance > 5 km.

## What to do with the tables

1. **Inventory and map** — `wells_unique.csv` plus `map_wells.png`. Depth, year dug, use, intervention, upstream/downstream.
2. **Recalled before vs now** — boxplots. This is memory + one snapshot, not a designed BACI. Stratify by distance and intervention; do not read “Check dam looks better” as a national result (Kapisa/Kunar dominate that class).
3. **Short hydrographs** — wells with ≥8 dates. These show the 2026 season, not a multi-year recovery.
4. **Perception vs tape** — treat Q32 as satisfaction. It often disagrees with measured DTW.
5. **QA** — diameter 2025/900, household = phone, Herat 12–15 km, WT-before < 1 m in a deep well.

## What not to do

- Mann–Kendall / Sen on the full file. Most wells have one visit; the longest series is about one year. A “significant” weekly slope is usually the season.
- Treat upstream wells as a control wadi. They sit on the same intervention.
- Convert DTW to water-table elevation until GPS altitude is checked against a DEM.
- Claim I4 from the check-dam protocol. This survey has no pond log, no untreated fan, and no pumping meter.

Join later: CHIRPS or station rain, structure GPS, DEM elevation. Keep collecting the same `well_id` weekly if you want a real trend test in later years.
