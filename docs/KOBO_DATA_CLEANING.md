# How to clean the KOBO well file (before more analysis)

Each row is a **visit**. The same physical well is resubmitted with a new GPS
each week. GPS precision in this export is about **4.6–5 m**, so 10–12 m is
the right “same standing point” window. That is **not** the same as “every
well in the hamlet.”

## 1. Identify the well (12 m + owner)

**Do this**

1. Normalize owner name (trim, lower case, ignore extra spaces and punctuation).
2. Treat the same **phone** in the same village as the same caretaker, even if
   the name spelling drifted (`Malik Mohammad Rasikh` / `malik Muhammad rasikh`).
3. Treat fuzzy-equal names as the same person **only if phones do not conflict**
   (edit distance ≤ 2, or one name contains the other). Different phones stay
   apart — often father and son.
4. Inside that owner group, cluster GPS points within **12 m**. Those visits
   are one well with repeat monitoring.
5. If the same owner has two clusters **more than 12 m** apart, keep them as
   two wells until you check. 12–50 m is usually leftover GPS jitter (same
   depth → you may merge). More than 200 m is either a second well or an
   office GPS.

**Do not do this**

Do not cluster GPS alone. Home-dug wells sit close together. A 12 m
connected-component in Kunduz / Yaamchi glued **40 owners** and 23 different
depths into one “well.” Owner is the cross-check that stops that.

| Pattern | Meaning |
|---------|---------|
| Same owner, GPS ≤ 12 m | One well, several visits. Merge. |
| Same owner, GPS 12–50 m, same depth | Probably jitter. Review, then merge. |
| Same owner, GPS > 200 m | Two wells, or field GPS vs office GPS. |
| Different owners, GPS ≤ 12 m | Neighbours, a shared/public well, or one GPS used for many interviews. Keep separate unless the enumerator confirms one well. |

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
2. Build owner groups, then 12 m clusters → `well_id`.
3. Apply rule flags (A).
4. Mark form clones (B) and DTW jumps (C).
5. Walk `nearby_other_wells.csv` and `same_owner_splits.csv` with the
   enumerator (names in `data/kobo/review_owners.csv`).
6. Only then repeat maps, boxplots, and hydrographs.

```bash
python3 tests/test_kobo_gw.py
python3 tools/kobo_gw.py --csv data/kobo/groundwater_monitoring.csv
```
