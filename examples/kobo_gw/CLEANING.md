# KOBO cleaning review

Well identity is **distance first**: a complete-linkage GPS cluster (every pair ≤ **12 m**). Owner name is a **cross-check** only. The same personal name appears in many provinces and is not used as the well key.

## Identity counts

- Visits: **3354**
- Wells (12 m GPS clusters): **1224**
- Owner check agree / mixed / missing: 1078 / 143 / 3
- Wells with 2+ visits: **606**
- Median GPS spread on multi-visit wells: **8.75 m** (complete linkage keeps this ≤ 12 m)
- Nearby different wells (centroids ≤ 12 m): **182** pairs.
- Same owner name in the same village on several 12 m wells: **297** (203 within 200 m; 94 farther than 200 m).

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
| Mixed owner names at one 12 m site | Shared well, or one GPS for many interviews | Keep as one site; review names |
| Same owner name, several 12 m sites in one village | Two wells, or office vs field GPS | Review; do not merge by name across provinces |

Owner names for follow-up (not in git): `data/kobo/review_owners.csv`.
