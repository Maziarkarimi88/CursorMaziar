# Same-well GPS groups in ArcGIS

Each KOBO row is a **visit**. The same home-dug well is sent again each week with a
new GPS ping. You want one site = one courtyard, not one hamlet.

**Target rule (this project):** every pair of visits in a well is ≤ **15 m**
(complete linkage). Isolated points stay as **1-visit wells**. They are not
“noise” to delete. Owner name is a **check after** the GPS group exists.

ArcGIS built-in cluster tools are **single-linkage / DBSCAN**. At 15 m they
chain A–B–C down a street. That is why a GIS “15 m” run can look different
from `tools/kobo_gw.py`. Use the tools below in this order.

---

## Which tool gives a better same-well list

| Rank | Tool (ArcGIS Pro) | What it does | Use it for |
|---:|---|---|---|
| 1 | **Generate Near Table** (Analysis → Proximity), Method = **Geodesic**, radius **15 Meters**, all neighbours | Writes every pair ≤ 15 m. Does not invent a well id. | **Best ArcGIS output.** QA, maps, and input to a complete-linkage group. |
| 2 | **Near** (same toolbox), Method = **Geodesic** | One nearest neighbour and `NEAR_DIST` on each visit. | Histogram of revisit jitter. Isolates have `NEAR_DIST` empty or > 15 m. |
| 3 | **XY Table To Point** + **Project** (only if you refuse geodesic) | Builds the point layer in metres. | Required setup. Not a clustering tool. |
| 4 | **Minimum Bounding Geometry** (circle or convex hull) on a trial cluster | Measures the diameter of a GIS cluster. | Split any cluster whose diameter **> 15 m** — it chained. |
| 5 | **Summary Statistics** / **Frequency** of owner name by cluster | Counts distinct caretakers on one GPS site. | Owner check: one name = agree; several = mixed. |
| 6 | **Density-based Clustering (DBSCAN)** at **8–10 m**, min features = 2 | Single-linkage groups + “noise”. | Draft picture only. Then check hull diameter. **Do not use 15 m.** |
| — | `tools/kobo_gw.py` (complete linkage) | Every pair ≤ 15 m; isolates kept as wells. | **Best well_id.** Join that table back into ArcGIS. |

**Do not use for well identity**

| Tool | Why the output is worse |
|---|---|
| DBSCAN / Find Point Clusters at **15 m**, min 2 | Chains a street. On this file that is 441 “noise” / 2,939 clustered, not one well per courtyard. Your 1,041 / 2,339 split was ~**5.2 m**, the GPS precision, not 15 m geodesic. |
| **Group By Proximity** at 15 m | Same chaining as DBSCAN. |
| **Pairwise Buffer 15 m** + **Dissolve** | Same chaining. A 15 m buffer is a 30 m search between centroids. |
| **Pairwise Buffer 7.5 m** + **Dissolve** | Still single-linkage at 15 m. Use buffers only to **draw**, not to dissolve. |
| **Integrate** (XY tolerance 15 m) | Snaps coordinates. Destroys the original GPS. Can chain. |
| **Collect Events** / **Aggregate Points** | Coincidence / large bins, not a 15 m courtyard. |
| **Near** or DBSCAN with Method = **Planar** on WGS 1984 | Distance is in degrees. “15” is not 15 metres. |
| Web Mercator (EPSG 3857) “metres” | Stretched. At 35°N, 15 map metres ≈ 12 m on the ground. |

---

## Expected counts on this KOBO file (check your GIS)

| What you ran | Isolated / “noise” | In a group of 2+ |
|---|---:|---:|
| Your earlier GIS “15 m” | 1,041 | 2,339 |
| Geodesic DBSCAN **5.2 m**, min 2 (GPS precision) | ≈ 1,040 | ≈ 2,340 |
| Geodesic DBSCAN **15 m**, min 2 | **441** (415 GPS + 26 empty) | **2,939** |
| Complete linkage **15 m** (this repo) | **533** one-visit wells | **2,821** visits in **548** wells (**1,081** wells) |

If ArcGIS still shows ~1,041 / 2,339 after you set 15 m, the search is not 15 m
on the ground. Fix CRS / Method before you change the well list.

If **Generate Near Table** and **DBSCAN** both show **2,939** points, the 15 m
search is correct. Those tools must match on that count (a point with ≥1
neighbour ≤ 15 m). Next checks:

- **415** GPS points with no Near row → 1-visit wells (keep them).
- DBSCAN **359** groups of 2+. **165** of those groups have diameter **> 15 m**
  (chains; largest about 44 visits / 76 m). Split those with hulls, or use
  `tools/kobo_gw.py` for the **1,081**-well list.
- 2,939 visits ≠ 2,939 wells. Complete-linkage multi-visit wells hold **2,821**
  visits in **548** sites. The extra **118** points are only “clustered”
  because they chain through a neighbour.

---

## 0. Prepare the layer (do this once)

1. Export the KOBO table with `X`, `Y`, `_id` (or `submission_id`), province,
   village, owner, `GPS_Precision`, measurement date, current DTW.
2. **XY Table To Point**
   - X Field = `X`, Y Field = `Y`
   - Coordinate System = **GCS WGS 1984** (EPSG 4326)
   - Output: `visits_wgs84`
3. Drop or set aside the **26** rows with empty X/Y. They are not noise wells.
   Keep them in a separate table if you need the raw row count (3,380).
4. Check **GPS_Precision**: median about 4.6 m, maximum 5.0 m. That field is
   the quality of one ping. It is **not** the cluster radius.

### Distance must be metres on the ground

**Preferred (national file):** leave the layer in WGS 1984 and set every
Proximity tool to **Method = Geodesic**, distance **15** with unit **Meters**.

**If the tool has no geodesic option:** **Project** to a metre system.

- One province in the east / centre (Kapisa, Kabul, Kandahar, Kunar, Kunduz):
  **WGS 1984 UTM Zone 42N**
- Far west (Herat, Farah, Badghis, Nimroz): **UTM Zone 41N**
- Do **not** project the whole country to one UTM zone and then measure 15 m.
- Do **not** use WGS 1984 Web Mercator (Auxiliary Sphere).

After Project, open the layer properties and confirm **Linear Unit = Meter**.

---

## 1. Best ArcGIS tool — Generate Near Table (15 m geodesic)

This is the table you should trust in GIS. It does not chain a street.

1. **Analysis Tools → Proximity → Generate Near Table**
2. Input Features = `visits_wgs84`
3. Near Features = `visits_wgs84` (same layer)
4. Search Radius = **15** **Meters**
5. Uncheck **Find only closest feature** (you want **all** neighbours ≤ 15 m)
6. Method = **Geodesic**
7. Output = `near_15m`

**How to read it**

- A visit that **never appears** as IN_FID (or has no row ≤ 15 m) is a
  **1-visit well**. Keep it.
- A pair with `NEAR_DIST` ≤ 15 m is a candidate same courtyard.
- If the same three IDs form a triangle and one side is 22 m, that side will
  **not** be in the table. Those three points are **two wells**, not one.
  DBSCAN would have merged them.

**Optional QA histogram**

1. Run **Near** (one neighbour only), Method = Geodesic.
2. Chart `NEAR_DIST`.
3. Same-owner revisits on this file sit about **3.2 m** (median) and **7.3 m**
   (75th percentile). A pile-up at 5 m means you are still on GPS precision.

---

## 2. Build a well id (pick one)

### A. Better output — Python complete linkage, then join in ArcGIS

ArcGIS has no complete-linkage tool. The script does.

```bash
python3 tools/kobo_gw.py --csv data/kobo/groundwater_monitoring.csv --no-plots
```

1. **XY Table To Point** on `examples/kobo_gw/visits.csv` (`lon`, `lat`) and
   on `examples/kobo_gw/wells_unique.csv`.
2. Display wells (one point per `well_id`, size = `n_visits`).
3. Join `well_id` / `owner_check` back to the original KOBO points if needed.

You should get **1,081** wells: **548** with 2+ visits, **533** measured once.

### B. ArcGIS-only draft — DBSCAN at 8–10 m, then cut chains

Use this only if you cannot run the script. It is a **draft**, not the lock.

1. **Spatial Statistics → Mapping Clusters → Density-based Clustering**
   (or **Find Point Clusters**).
2. Clustering Method = **DBSCAN**
3. Minimum Features per Cluster = **2**
4. Search Distance = **8** or **10 Meters** (not 5, not 15)
5. Method / distance = geodesic metres (or a UTM layer)
6. Output field `CLUSTER_ID`: negative or −1 = isolate. **Keep isolates.**

Then **break chains**:

1. **Minimum Bounding Geometry**
   - Input = clustered points only (`CLUSTER_ID` ≥ 0)
   - Group Option = **List** / group field = `CLUSTER_ID`
   - Geometry Type = **CONVEX_HULL** (or **CIRCLE**)
2. **Add Geometry Attributes** → length / diameter, or measure the hull.
3. Any hull **longer than 15 m** is a street, not a well. Split it:
   - select those points
   - re-run DBSCAN on the selection at **5–8 m**, **or**
   - assign IDs by hand from the Near Table (only add a point if it is
     ≤ 15 m from **every** member already in the group).

**Why 8–10 m here, not 15 m.** DBSCAN at 15 m already swallows the street.
8–10 m is about two GPS-precision fixes. You will split some true weekly
revisits (p75 jitter is 7.3 m). That is safer in GIS than chaining. The
Python 15 m complete-linkage list is still the one to lock.

### C. Do not “Buffer + Dissolve”

A dissolved 7.5 m or 15 m buffer is the same as DBSCAN. Use **Pairwise Buffer
7.5 m** only as a **drawing** of “this ping’s 15 m courtyard.” Do not dissolve.

---

## 3. Owner name — check only

1. **Spatial Join** or attribute join: owner name → the GPS group.
2. **Summary Statistics**
   - Case field = `well_id` or `CLUSTER_ID`
   - Statistic: **Count Distinct** on a cleaned owner name
     (or Frequency, then count rows per cluster).
3. Read the result:
   - 1 distinct name → `agree` (repeat visits)
   - 2+ distinct names → `mixed` (shared well, or one courtyard, many interviews)
   - blank → `missing`
4. **Do not** split a 15 m site because two names disagree.
5. **Do not** merge two sites in different provinces because both say
   “Gul Ahmad”.
6. Same name, same village, GPS **> 200 m** → two wells (or office vs field
   GPS). Review; do not auto-merge.

---

## 4. Suggested map

| Layer | Symbology |
|---|---|
| `wells_unique` (from the script) | One point per well. Size = `n_visits`. Colour = `owner_check`. |
| `near_15m` (optional as lines) | Draw only pairs ≤ 15 m. A long line is a mistake in CRS. |
| 7.5 m buffer (no dissolve) | See courtyard overlap. Overlap = candidate same well. |
| Hulls with diameter > 15 m | Red. These are chained DBSCAN groups to split. |

---

## 5. Short click-path (ArcGIS Pro)

1. **XY Table To Point** → WGS 1984.
2. **Generate Near Table** → 15 m, **Geodesic**, all neighbours.
3. Count isolates (no neighbour ≤ 15 m). They stay as wells.
4. Run `tools/kobo_gw.py` and add `wells_unique.csv`.
5. If you must cluster inside ArcGIS: **Density-based Clustering** DBSCAN
   **8–10 m**, min 2 → **Minimum Bounding Geometry** → split hulls > 15 m.
6. **Summary Statistics** on owner name by `well_id`.
7. Compare counts to the table above. If you are near 1,041 / 2,339, the
   radius is still ~5 m or the layer is not in geodesic metres.

Details on why 15 m (not 5 / 10 / 20): `examples/kobo_gw/RADIUS_CHOICE.md`.
GIS vs script counts: `examples/kobo_gw/CLUSTER_COMPARE.md`.
Cleaning rules: `KOBO_DATA_CLEANING.md`.
