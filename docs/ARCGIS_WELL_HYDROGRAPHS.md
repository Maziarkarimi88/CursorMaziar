# ArcGIS Pro: review chained groups, then hydrographs per well

**Do not chart DBSCAN clusters.** Chart **`well_id`** from the 15 m complete-linkage
list. DBSCAN at 15 m still glues neighbouring courtyards into one group.

On this export that list is **1,081 wells**. DBSCAN’s 2,939 “clustered” visits
are only “has a neighbour within 15 m.” **165** of the 359 DBSCAN groups mix
**two or more** real wells (street chains). Those groups are the review set.

| File | Load as | Use |
|---|---|---|
| `examples/kobo_gw/wells_unique.csv` | XY to point (`lon`, `lat`) | One row per well. Walk this table. |
| `examples/kobo_gw/visits.csv` | XY to point (`lon`, `lat`) | One row per visit. Time + DTW chart. |
| `examples/kobo_gw/dbscan_chains_review.csv` | XY to point (`lon`, `lat`) | Centroids of **wrong** DBSCAN groups. |
| `examples/kobo_gw/dbscan_chain_visits.csv` | XY to point (`lon`, `lat`) | Visits inside those groups, already tagged with the **split** `well_id`. |

`wt_now` is depth to water (m). **Larger = deeper = less water.** Put 0 at the
**top** of the chart.

`hydro_class` on both tables:

- `one_visit` — one date. Skip for a hydrograph (one point).
- `short_2to7` — a short line. Useful, not a season.
- `long_8plus` — **99 wells**. Start the visual review here.

---

## 0. What “split” means

You do **not** have to digitise new well ids by hand.

- **`dbscan_id`** = the ArcGIS DBSCAN / Near-Table chain (can be a street).
- **`well_id`** = the courtyard (every GPS pair ≤ 15 m). This is the split.
- **`split_review = 1`** = this visit sits in a DBSCAN group that contains
  **several** `well_id`s. Review on the map; keep `well_id` for analysis.

Example: DBSCAN group 44 visits spanning 42 m. `n_wells_to_split_into` might be
5. The five hashed ids in `well_ids` are the split. Chart those five separately.

---

## 1. Load the layers (once)

1. **XY Table To Point**
   - Input = `wells_unique.csv`
   - X = `lon`, Y = `lat`
   - Coordinate system = **GCS WGS 1984**
   - Output = `wells_15m`
2. Repeat for `visits.csv` → `visits_15m`
3. Repeat for `dbscan_chains_review.csv` → `dbscan_wrong_groups`
   (X = `lon`, Y = `lat`)
4. Repeat for `dbscan_chain_visits.csv` → `chain_visits` (optional; already
   inside `visits_15m` where `split_review = 1`)
5. **Add Attribute Index** on `well_id` (both wells and visits) and on
   `dbscan_id` (visits).
6. **Create Relationship Class** (or **Add Relate**)
   - Origin = `wells_15m`
   - Destination = `visits_15m`
   - Primary / foreign key = `well_id`
   - Cardinality = **One to many**

Confirm `wells_15m` has about **1,081** points and `visits_15m` **3,354**.

---

## 2. Review the groups DBSCAN got wrong (split list)

1. Open `dbscan_wrong_groups` attribute table.
2. Sort by `n_wells_to_split_into` (then `spread_m`) descending.
   - `spread_m` > 15 = the group is longer than one courtyard.
   - `n_wells_to_split_into` = how many 15 m wells to split it into.
3. Select the top row. Zoom to it. The centroid sits on the street chain.
4. On `visits_15m` set a **Definition Query**:
   `split_review = 1`
5. Symbology → Unique Values → `well_id` (the **split**).
   Optional second copy of the layer: Unique Values → `dbscan_id` (the **wrong** group).
6. You should see several colours (`well_id`) inside one DBSCAN blob.
7. **Minimum Bounding Geometry** on `chain_visits` grouped by `dbscan_id`
   (convex hull). Hulls longer than 15 m are the chains. About **165** hulls.
8. **Do not** assign a new id by dissolving the hull. Use `well_id` as it is.

If you still want to “split” inside ArcGIS: select one `dbscan_id`, then
**Summary Statistics** / **Frequency** of `well_id`. Those names are the
pieces. Copy `well_id` into any field you were using as CLUSTER_ID.

Walk the table until the large `n_wells_to_split_into` rows are checked.
Small chains (`n_wells_to_split_into` = 2, `spread_m` ≈ 16–20 m) are usually
two courtyards 11 m + 11 m apart.

---

## 3. Walk the well table (the list you analyse)

Clear the `split_review` query on `visits_15m` (all visits).

1. Open `wells_15m` attribute table.
2. **Filter** / definition query:
   - Start: `hydro_class = 'long_8plus'` → **99** wells
   - Then: `hydro_class = 'short_2to7'`
   - Skip: `hydro_class = 'one_visit'` for hydrographs (keep them on the map)
3. Sort by `n_unique_dates` descending (longest series first).
4. Keep these fields visible: `well_id`, `province`, `village`,
   `n_visits`, `n_unique_dates`, `first_meas_date`, `last_meas_date`,
   `first_wt_now_m`, `last_wt_now_m`, `dtw_change_measured_m`,
   `owner_check`, `exclude_from_impact`, `hydro_class`.
5. Click the first row. **Related Data** → `visits_15m`.
   Only that well’s visits highlight. Zoom to related.

`dtw_change_measured_m` = first tape − last tape. **Positive = shallower now.**
`exclude_from_impact = True` → still draw the hydrograph, but do not use the
well in a before/after median (DTW > depth, unit mix-up, etc.).

---

## 4. Hydrograph for the selected well (ArcGIS Pro chart)

Do this from the **related visits**, not from the well point.

1. With related visits selected: on `visits_15m` → **Create Chart** → **Line Chart**.
2. Chart properties:
   - **X-axis** (Date) = `meas_date`
   - **Y-axis** (Numeric) = `wt_now`  (current depth to water, m)
   - **Split by** = `well_id`  (one line; or leave split off if only one well is selected)
   - Check **Filter by selection** (so the chart follows the table click)
3. **Axes**
   - Reverse / invert the **Y** axis so **0 is at the top**.
     Deeper water (larger `wt_now`) plots **down**, as in a well.
   - Y label: `Depth to water (m)`
   - X label: `Measurement date`
4. Series: markers on, line connecting dates.
5. Title Arcade or manual: `$feature.province + " / " + $feature.village + " / " + $feature.well_id`

Click the **next row** in `wells_15m`. If Filter by selection is on and the
relate is active, the line updates. That is the walkthrough.

**Time slider (optional)**

1. `visits_15m` → Properties → **Time**
2. Layer Time = each feature has a single time field = `meas_date`
3. Time step = 1 week
4. Use with **one well selected**. All 3,354 points on the slider is noise.

**Do not** split the chart by `dbscan_id`. That mixes several wells on one line
and invents fake jumps (the `dtw_jump` flags).

---

## 5. Several wells on one chart (optional)

Only after the one-well walkthrough.

1. Select 8–12 wells in the same **village** (or the 12 longest).
2. Chart: X = `meas_date`, Y = `wt_now`, **Split by** = `well_id`.
3. Invert Y. Legend = `well_id`.
4. If two lines sit on top of each other, they may still be the same courtyard
   (check `gps_spread_m` ≤ 15 on `wells_15m`).

More than ~12 series is unreadable. Use **Map Series** instead:

1. Layout with map + chart element.
2. **Map Series** → Spatial, layer = `wells_15m` (filtered `long_8plus`).
3. Page name = `well_id`.
4. Chart filtered by map series page (Pro 3.1+: chart “Filter by map series”).
5. Export PDF → one page per long well.

The Python run already writes `figures/kobo_gw/hydrographs_longest12.png` and
`hydrographs_8plus.pdf` if you only need the pictures.

---

## 6. Map that matches the table

| Layer | Symbology |
|---|---|
| `wells_15m` | Size = `n_visits`. Colour = `hydro_class` (grey one-visit, orange short, blue long). |
| `wells_15m` copy | Colour = `owner_check` (agree / mixed / missing). |
| `visits_15m` | Small points. Transparent. Time enabled. |
| `dbscan_wrong_groups` | Hollow red circle, size ~ `spread_m`. Label `n_wells_to_split_into`. |
| Hulls of `split_review = 1` | Outline only. These are the groups **not** to use as well ids. |

7.5 m **Pairwise Buffer** on `wells_15m` (no dissolve) shows the 15 m courtyard.

---

## 7. Order of work (short)

1. Load `wells_15m` + `visits_15m` + relate on `well_id`.
2. Inspect `dbscan_chains_review` (wrong DBSCAN groups). Confirm `well_id`
   already splits them. Do not chart `dbscan_id`.
3. Filter wells to `hydro_class = 'long_8plus'` (99 wells).
4. Click well → related visits → line chart of `meas_date` vs `wt_now`, Y inverted.
5. Step through the table. Note jumps > 3 m in ≤ 21 days (`qa_flags.csv`
   `dtw_jump`) — often two wells still mixed or a tape start-point change.
6. Then short series, then maps / boxplots. One-visit wells stay on the map
   only.

Field names: `meas_date` = tape date, `wt_now` = current DTW (m),
`well_id` = 15 m courtyard. Cleaning rules: `KOBO_DATA_CLEANING.md`.
Clustering tools: `ARCGIS_SAME_WELL_CLUSTERING.md`.
