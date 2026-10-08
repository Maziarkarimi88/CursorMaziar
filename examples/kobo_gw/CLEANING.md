# KOBO cleaning review

Well identity is **distance first**: a complete-linkage GPS cluster (every pair ≤ **15 m**) → `well_id` / `site_id`. Different owner/caretaker names inside that radius get different `cluster_id`s (spelling drift stays one cluster). The same personal name is not used as a nationwide well key.

## Identity counts

- Visits: **3354**
- GPS sites (`well_id`, 15 m complete linkage): **1081**
- Monitoring wells (`cluster_id` = GPS + owner/caretaker split): **1244**
- GPS sites split because owners differ inside 15 m: **135**
- Owner check agree / mixed / missing: 938 / 140 / 3
- Wells with 2+ visits: **548**
- Median GPS spread on multi-visit wells: **10.7 m** (complete linkage keeps this ≤ 15 m)
- Nearby different wells (centroids ≤ 15 m): **161** pairs.
- DBSCAN 15 m groups that mixed two or more wells (split_review): **1966** visits. See `dbscan_chains_review.csv`.
- Same owner name in the same village on several 15 m wells: **272** (177 within 200 m; 95 farther than 200 m).

## How to treat outliers

Do **not** drop wells with IQR on total depth. A 100 m well in Paktya is not an error.
Use rule flags first, then look at the review lists.

| Flag | Why it is an outlier | Action |
|---|---|---|
| Current DTW > well depth | Impossible | Exclude from impact; ask enumerator |
| WT before < 1 m in a well > 5 m | Likely water-column, not DTW | Exclude; recode if confirmed |
| Diameter ≥ 100 m or 5–100 m | Year or centimetres | Blank diameter |
| Households = phone or > 200 | Field mix-up | Blank households |
| Distance > 5 km | Office GPS or wrong structure | Exclude from distance plots |
| Recalled change > 15 m | Memory or unit error | Review; often form clone |
| Form clone (≥5 owners, same depth+before) | Copied static fields | Do not treat as independent wells |
| DTW jump > 3 m in ≤21 days | Two wells merged, or bad tape | Split well or drop those visits |
| Same owner, GPS > 200 m apart | Two wells, or office vs field GPS | Keep as two wells until checked |
| Mixed owner names at one 15 m site | Two wells in one courtyard, or one GPS for many interviews | Split into `cluster_id`s; `well_id` stays the GPS site |
| Same owner name, several 15 m sites in one village | Two wells, or office vs field GPS | Review; do not merge by name across provinces |

Owner names for follow-up (not in git): `data/kobo/review_owners.csv`.
