# How to clean the KOBO well file (before more analysis)

Each row is a **visit**. The same physical well is resubmitted with a new GPS
each week. GPS precision in this export is about **4.6–5 m**, so **15 m complete
linkage** is the same-standing-point window (about three fixes of jitter).
That is **not** the same as “every well in the hamlet.” **5 m is too
small** (it is the GPS precision itself and splits weekly revisits).
**20 m is too large** (it reaches the next compound). See
`examples/kobo_gw/RADIUS_CHOICE.md`.

## 1. Identify the well (distance first, then owner check)

Personal names repeat across Afghanistan (`Gul Ahmad`, `Mohammad`). Do **not**
use owner name as the well key. Cluster **GPS first**. Then read the names
on that cluster.

**Do this**

1. Group visits whose GPS points are all within **15 m** of each other
   (complete linkage: every pair ≤ 15 m). That is one monitoring site / well.
   Same-owner revisits on a later date sit **3.2 m** apart at the median and
   **7.3 m** at the 75th percentile. 15 m is about three GPS-precision
   fixes, not a whole street. Do not use 5 m — that is the precision field.
2. Do **not** use single-linkage (A near B, B near C…). That chains a hamlet.
   Complete linkage keeps A and C at 22 m as two wells.
3. Cluster inside each **province** so a common name in Kapisa never touches
   the same name in Kunduz.
4. **Cross-check owner names** on the cluster, then **split** on caretaker:
   - `agree` — one caretaker (spelling drift allowed). Repeat visits to one well.
   - `mixed` — several distinct names at the same spot. Shared/public well, or
     the enumerator stood in one courtyard and entered many households.
     GPS `well_id` / `site_id` stays one courtyard; `cluster_id` splits each
     owner/caretaker into its own monitoring well.
   - `missing` — no name (missing names cluster together by GPS only).
5. If the **same name in the same village** appears on two 15 m sites more
   than 200 m apart, treat them as two wells (or office vs field GPS). Do not
   merge that name nationwide.

| Pattern | Meaning |
|---------|---------|
| GPS ≤ 15 m (all pairs) | One GPS site (`well_id`). Then split by owner into `cluster_id`. |
| Owner names agree | Confident repeat monitoring. One `cluster_id`. |
| Owner names mixed | Same GPS site; **split** into different `cluster_id`s. |
| Same name, other province | Different well. Distance already kept them apart. |
| Same name, same village, GPS > 200 m | Two wells or office GPS. |

GIS DBSCAN “noise” is not the same as a 1-visit well. On this file a true
15 m great-circle DBSCAN (min 2) gives **441 noise / 2,939 clustered**,
not 1,041 / 2,339. That 1,041 / 2,339 split matches a search of about **5.22 m**
(the GPS precision is 4.6–5.0 m). See `examples/kobo_gw/CLUSTER_COMPARE.md`.
ArcGIS steps and which tool to use: `ARCGIS_SAME_WELL_CLUSTERING.md`
(**Generate Near Table**, geodesic 15 m — not DBSCAN at 15 m).

The script writes:

- `examples/kobo_gw/nearby_other_wells.csv` — different wells whose centroids are ≤ 15 m
- `examples/kobo_gw/same_owner_splits.csv` — one owner, several 15 m sites
- `data/kobo/review_owners.csv` — owner names and phones for follow-up (gitignored)

## 2. Identify outliers (rules, not national IQR)

A 105 m well in Paktya is not an outlier. National IQR on depth or DTW will
flag real deep wells. Use **physical rules**, then **within-well** jumps, then
**copied form fields**.

### A. Impossible or mixed units — drop from impact numbers

| Rule | Typical mistake |
|------|-----------------|
| Current DTW > total depth | Tape past the bottom, or depth typed wrong |
| Current DTW = 0 or > 100 m | Missed decimal or wrong well |
| “Typical WT before” < 1 m while depth > 5 m | Water **in** the well typed as DTW |
| Diameter ≥ 100 m (2025, 900) | Year or village code in the diameter box |
| Diameter 5–100 m | Centimetres typed as metres |
| Households = phone, or households > 200 | Phone pasted into the household box |
| Distance to structure > 5 km | Structure GPS or office GPS |
| Measured before intervention completion | Date swap |

### B. Copied static fields — do not treat as independent wells

If **five or more owners** in one village share the same total depth **and**
the same “WT before,” the enumerator copied the header. Paktya / Halim Khil
is the example (−16 m “decline” across many owners). Flag as `form_clone`.
Keep the **current** tape reading; do not use the copied “before” for impact.

### C. Time-series outliers — on one well, not the country

On the 15 m well:

- |\Delta DTW| > **3 m** between visits ≤ 21 days apart → `dtw_jump`. Either
  two wells were merged, or the tape start-point changed.
- Recalled change (before − now) > **15 m** → review. Often the same clone.

Do **not** run IQR or z-scores on raw depth across Afghanistan. If you want a
statistical fence, compute it **inside one province** on **DTW change**, using
a modified z-score (median / MAD), and only after the rule flags above.

### D. What to keep for analysis

A well is usable for before/after tables when it has:

- valid GPS in Afghanistan
- current DTW ≤ depth
- no unit-confusion on “before”
- distance ≤ 5 km (for distance plots)
- not a form-clone for the recalled-before field

Hydrographs use every visit on the 15 m well except `dtw_jump` rows
you reject after a look.

## 3. Suggested cleaning order

1. Drop empty / no-consent rows.
2. Build 15 m complete-linkage GPS clusters → `well_id` / `site_id`. Split different owner/caretaker names inside that radius into `cluster_id`.
3. Apply rule flags (A).
4. Mark form clones (B) and DTW jumps (C).
5. Walk `nearby_other_wells.csv` and `same_owner_splits.csv` with the
   enumerator (names in `data/kobo/review_owners.csv`).
6. Only then repeat maps, boxplots, and hydrographs.

```bash
python3 tests/test_kobo_gw.py
python3 tools/kobo_gw.py --csv data/kobo/groundwater_monitoring.csv
```
