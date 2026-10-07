# KOBO cleaning review

Well identity: same **owner/phone group** and GPS within **12 m**. GPS-only clustering is not used — that chains neighbouring household wells (example: 40 owners in Kunduz / Yaamchi inside one 12 m component).

## Identity counts

- Visits: **3354**
- Wells after 12 m + owner: **1352**
- Wells with 2+ visits: **394**
- Median GPS spread on multi-visit wells: **10.85 m** (should stay ≤ 12 m)
- Nearby different wells (centroids ≤ 12 m): **501** pairs — dense village or GPS copied for several owners. See `nearby_other_wells.csv`.
- Same owner, several 12 m wells: **215** groups (135 within 200 m to review; 80 farther than 200 m).

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
| Nearby other owners ≤ 12 m | Neighbours, or one GPS for many wells | Keep separate unless owner confirms one well |

Owner names for follow-up (not in git): `data/kobo/review_owners.csv`.
