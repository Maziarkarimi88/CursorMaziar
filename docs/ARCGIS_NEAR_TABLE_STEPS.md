# ArcGIS Pro — tool by tool: Near Table to `well_id`

Each KOBO row is a **visit**. The well id is a **15 m complete-linkage** GPS
group. Owner / caretaker is a **check after** that group. Do not connect
`IN_FID`–`NEAR_FID` as a network (that is DBSCAN).

Open the **Geoprocessing** pane (Analysis → Tools) and search each tool name
below. Toolbox paths are for ArcGIS Pro 3.x.

---

## Before you start

| Need | Setting |
|---|---|
| Point layer of visits | One point per KOBO row. Call it `visits_wgs84`. |
| CRS | **GCS WGS 1984** (EPSG 4326). Do not use Web Mercator. |
| Linear units for Near | **Meters**, Method **Geodesic**. |
| Empty X/Y | 26 rows with no GPS: export them aside. Do not run Near on them. |

If you only have the KOBO table, make points first:

**Tool:** Data Management Tools → Layers and Table Views → **XY Table To Point**

| Parameter | Value |
|---|---|
| Input Table | KOBO export |
| X Field | `X` |
| Y Field | `Y` |
| Coordinate System | GCS WGS 1984 |
| Output Feature Class | `visits_wgs84` |

---

## Step 1 — Copy ObjectID to a long field `VID`

ObjectID can be rewritten if you export or copy the layer. `VID` is a frozen
copy so the Near Table still matches after CSV export.

### Tool A — Add Field

**Tool:** Data Management Tools → Fields → **Add Field**

| Parameter | Value |
|---|---|
| Input Table | `visits_wgs84` |
| Field Name | `VID` |
| Field Type | **Long** (64-bit integer if offered: **Big integer**) |
| Field Alias | Visit ID (copy of ObjectID) |
| Field Is Nullable | Yes |

Run. Confirm `VID` is empty in the attribute table.

### Tool B — Calculate Field

**Tool:** Data Management Tools → Fields → **Calculate Field**

| Parameter | Value |
|---|---|
| Input Table | `visits_wgs84` |
| Field Name | `VID` |
| Expression Type | **Python 3** (or Arcade) |
| Expression (Python) | `!OBJECTID!` |
| Expression (Arcade) | `$feature.OBJECTID` |

Run. Spot-check: `VID` equals `OBJECTID` on the first and last rows.

Optional: **Add Attribute Index** on `VID` (Data Management → Indexes → Add Attribute Index).

---

## Step 2 — Generate Near Table (15 m, geodesic, all neighbours)

This writes every pair of visits ≤ 15 m. It does **not** create a well id.

**Tool:** Analysis Tools → Proximity → **Generate Near Table**

| Parameter | Value | Why |
|---|---|---|
| Input Features | `visits_wgs84` | Each visit |
| Near Features | `visits_wgs84` | Same layer (self-near) |
| Output Table | `near_15m` | Standalone table, not a layer |
| Search Radius | **15** | Then set unit to **Meters** (not Unknown, not Feet) |
| Location | Unchecked | You already have X/Y on the points |
| Angle | Unchecked | Not needed |
| **Find only closest feature** | **Unchecked** | You need **all** neighbours ≤ 15 m, not one |
| Maximum number of closest matches | 0 or blank (all) | Only if the closest box is off |
| Method | **Geodesic** | Ground metres on WGS 1984. **Planar** is wrong here |

Run. Open `near_15m`. You should see:

| Field | Meaning |
|---|---|
| `IN_FID` | ObjectID of the from-visit (same numbers as `VID` / `OBJECTID`) |
| `NEAR_FID` | ObjectID of the neighbour |
| `NEAR_DIST` | Distance in **metres** (about 0–15) |
| `NEAR_RANK` | 1 = closest neighbour, 2 = next, … (if present) |

**Checks**

- `NEAR_DIST` maximum should be ≤ 15. If you see values like 0.0001, the unit
  was degrees (Method was Planar). Re-run with Geodesic / Metres.
- Count of distinct `IN_FID` with at least one row ≈ **2,939** on this file.
- Visits that **never** appear in `IN_FID` ≈ **415**. Those are 1-visit wells.
  Keep them.
- If you see ~2,339 rows-with-a-neighbour, the radius is still ~5 m.

**Do not** Join this table to the points and Dissolve / Generate Connected
Components. That rebuilds DBSCAN.

---

## Step 3 — Export points and the Near Table to CSV

You need two CSVs for complete linkage.

### Tool C — Export Table (visits)

**Tool:** Data Management Tools → Table → **Export Table**

(Right-click `visits_wgs84` → Data → Export Table also works.)

| Parameter | Value |
|---|---|
| Input Table | `visits_wgs84` |
| Output Table | `visits_points.csv` (folder + `.csv`) |

Keep at least these columns (names can match the KOBO headings):

| Must export | Typical field |
|---|---|
| `OBJECTID` | ObjectID |
| `VID` | the copy from Step 1 |
| X / lon | `X` or `POINT_X` |
| Y / lat | `Y` or `POINT_Y` |
| Province | `1. Province` or `province` |
| Village | `3. Village Name` or `village` |
| Owner / caretaker | `8. Owner/caretaker name` or `owner` |
| Measure date | `23. Date of water level measurement` |
| Current DTW | `24. Current water table depth (m)` |
| Submission id | `_id` if present |

### Tool D — Export Table (Near)

**Tool:** Data Management Tools → Table → **Export Table**

| Parameter | Value |
|---|---|
| Input Table | `near_15m` |
| Output Table | `near_15m.csv` |

Must include `IN_FID`, `NEAR_FID`, `NEAR_DIST`.

Open both CSVs in a text editor: first row is column names, `NEAR_DIST` looks
like `3.2` or `14.8`, not `0.00003`.

---

## Step 4 — Complete linkage (this is the well cluster)

ArcGIS Pro has **no** complete-linkage tool. The Near Table is only the pair
list. A visit joins a well only if it has a Near row to **every** other visit
already in that well.

**Tool (outside Pro):** `tools/near_table_wells.py` (Python 3, pandas, numpy)

```bash
pip install pandas numpy
python3 tools/near_table_wells.py --points visits_points.csv --near near_15m.csv --oid OBJECTID --out-dir examples/kobo_gw
```

If the ObjectID column is named `VID`:

```bash
python3 tools/near_table_wells.py --points visits_points.csv --near near_15m.csv --oid VID --out-dir examples/kobo_gw
```

`--oid` must be the same id that `IN_FID` / `NEAR_FID` use (usually
`OBJECTID` at the time you ran Generate Near Table). If you exported after
recalculating ObjectID, use `--oid VID` **and** the Near Table must have been
built when `VID` still equalled `IN_FID`. Safest: export immediately after
Step 2, use `--oid OBJECTID`.

**Writes**

| File | What it is |
|---|---|
| `visits_from_near.csv` | Every visit + `well_id` + `owner_check` (no owner/phone columns) |
| `wells_from_near.csv` | One row per well: count, centroid, `owner_check` |
| `same_owner_splits_from_near.csv` | Same caretaker name, more than one `well_id` in one village |

On this KOBO file you should get about **1,081** wells (not 2,939).

Owner is applied **after** GPS:

- `agree` — one caretaker on that 15 m site (repeat monitoring)
- `mixed` — several names at one site (keep one `well_id`; review)
- `missing` — no name

Same personal name in two provinces stays two wells. Same name, two `well_id`s
in one village, GPS > 200 m → two wells.

Alternatively skip the Near export and run the same rule from coordinates:

```bash
python3 tools/kobo_gw.py --csv data/kobo/groundwater_monitoring.csv --no-plots
```

That writes `examples/kobo_gw/wells_unique.csv` and `visits.csv` (already
1,081 wells on this export).

---

## Step 5 — Join `well_id` back in ArcGIS Pro

### Tool E — XY Table To Point (optional, if you want a new well layer)

**Tool:** Data Management Tools → Layers and Table Views → **XY Table To Point**

| Parameter | Value |
|---|---|
| Input Table | `wells_from_near.csv` or `wells_unique.csv` |
| X Field | `lon` |
| Y Field | `lat` |
| Coordinate System | GCS WGS 1984 |
| Output | `wells_15m` |

### Tool F — Join Field (put `well_id` on the original visits)

**Tool:** Data Management Tools → Joins → **Join Field**

| Parameter | Value |
|---|---|
| Input Table | `visits_wgs84` |
| Input Join Field | `OBJECTID` (or `VID` if that is what `--oid` used) |
| Join Table | `visits_from_near.csv` (add it with **Add Data**) |
| Join Table Field | `OBJECTID` (or `VID`) |
| Transfer Fields | `well_id`, `owner_check` |

Run. Every visit now has a courtyard id.

**Add Relate** (optional, for hydrographs):

**Tool:** Data Management Tools → Joins → **Add Relate** (or layer properties → Relates)

| Parameter | Value |
|---|---|
| Layer | `wells_15m` |
| Related table / layer | `visits_wgs84` |
| Input field / related field | `well_id` |
| Cardinality | One to many |
| Relate name | `visits_of_well` |

---

## Step 6 — Owner check in Pro (does not change `well_id`)

**Tool:** Analysis Tools → Statistics → **Summary Statistics**

| Parameter | Value |
|---|---|
| Input Table | `visits_wgs84` |
| Statistics Field | owner name → **Count Distinct** (or Frequency, then count rows) |
| Case Field | `well_id` |
| Output | `owner_by_well` |

Read against `owner_check`. Do not dissolve on owner name.

**Tool:** Analysis Tools → Statistics → **Frequency** (optional)

Case fields: `province`, `village`, `well_id` — only to list mixed sites.

---

## Step 7 — Hydrograph (after the join)

See `ARCGIS_WELL_HYDROGRAPHS.md`. Short path:

1. Filter `wells_15m` to `hydro_class = 'long_8plus'` if you used `kobo_gw.py`
   (99 wells), or `n_visits >= 8` on `wells_from_near.csv`.
2. Click a well → Related Data → visits.
3. **Create Chart** → Line: X = measure date, Y = current DTW (`wt_now`),
   Split by = `well_id`, Filter by selection. Reverse the Y axis (0 at top).

Do not chart a group built from `IN_FID`–`NEAR_FID`.

---

## Tools you must not use for the well id

| Tool | What goes wrong |
|---|---|
| Density-based Clustering / Find Point Clusters (DBSCAN) at 15 m | Chains A–B–C. 2,939 points ≠ 2,939 wells. |
| Group By Proximity at 15 m | Same chain. |
| Pairwise Buffer + Dissolve | Same chain. |
| Integrate (15 m XY tolerance) | Snaps GPS. Destroys the raw points. |
| Join Near Table + Dissolve | Rebuilds DBSCAN from `IN_FID`–`NEAR_FID`. |
| Near (one neighbour only) | Fine for a histogram; not a well id. |

---

## Expected counts on this KOBO file

| After | Number |
|---|---:|
| Visit points with GPS | 3,354 |
| Distinct `IN_FID` in `near_15m` | ≈ 2,939 |
| Visits with no Near row | ≈ 415 (keep as wells) |
| `well_id` from complete linkage | **1,081** |
| Wells with 2+ visits | 548 |
| Owner agree / mixed / missing | 938 / 140 / 3 |
