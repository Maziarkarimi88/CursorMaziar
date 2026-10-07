# How to clean the KOBO well file (before more analysis)

Each row is a **visit**. The same physical well is resubmitted with a new GPS
each week. GPS precision in this export is about **4.6–5 m**, so 10–12 m is
the right “same standing point” window. That is **not** the same as “every
well in the hamlet.”

## 1. Identify the well (distance first, then owner check)

Personal names repeat across Afghanistan (`Gul Ahmad`, `Mohammad`). Do **not**
use owner name as the well key. Cluster **GPS first**. Then read the names
on that cluster.

**Do this**

1. Group visits whose GPS points are all within **12 m** of each other
   (complete linkage: every pair ≤ 12 m). That is one monitoring site / well.
   GPS precision in this export is about 4.6–5 m, so 12 m is two-to-three
   fixes of jitter, not a whole street.
2. Do **not** use single-linkage (A near B, B near C…). That chains a hamlet.
   Complete linkage keeps A and C at 22 m as two wells.
3. Cluster inside each **province** so a common name in Kapisa never touches
   the same name in Kunduz.
4. **Cross-check owner names** on the cluster:
   - `agree` — one caretaker (spelling drift allowed). Repeat visits to one well.
   - `mixed` — several distinct names at the same spot. Shared/public well, or
     the enumerator stood in one courtyard and entered many households.
   - `missing` — no name.
5. If the **same name in the same village** appears on two 12 m sites more
   than 200 m apart, treat them as two wells (or office vs field GPS). Do not
   merge that name nationwide.

| Pattern | Meaning |
|---------|---------|
| GPS ≤ 12 m (all pairs) | One well. Merge visits. Then check the owner name. |
| Owner names agree | Confident repeat monitoring. |
| Owner names mixed | Keep as one site; review. Do not split on name. |
| Same name, other province | Different well. Distance already kept them apart. |
| Same name, same village, GPS > 200 m | Two wells or office GPS. |

The script writes:

- `examples/kobo_gw/nearby_other_wells.csv` — different wells whose centroids are ≤ 12 m
- `examples/kobo_gw/same_owner_splits.csv` — one owner, several 12 m sites
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

On the 12 m + owner well:

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

Hydrographs use every visit on the 12 m + owner well except `dtw_jump` rows
you reject after a look.

## 3. Suggested cleaning order

1. Drop empty / no-consent rows.
2. Build 12 m complete-linkage GPS clusters → `well_id`. Cross-check owner names on each cluster.
3. Apply rule flags (A).
4. Mark form clones (B) and DTW jumps (C).
5. Walk `nearby_other_wells.csv` and `same_owner_splits.csv` with the
   enumerator (names in `data/kobo/review_owners.csv`).
6. Only then repeat maps, boxplots, and hydrographs.

```bash
python3 tests/test_kobo_gw.py
python3 tools/kobo_gw.py --csv data/kobo/groundwater_monitoring.csv
```
