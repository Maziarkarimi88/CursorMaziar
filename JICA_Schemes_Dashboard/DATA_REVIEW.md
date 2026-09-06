# JICA IS + WSM schemes — data review

Latest source: `data/raw_Both_Jica_Irrigation_and_WSM_Schemes_72ae.csv`  
Rows on the map: **14** (7 irrigation + 7 watershed). **All scheme codes are unique.**

Upload attributes: `data/schemes_dashboard.csv`. Join to your existing polygon and line layers on `SCHEME_UID`. Do not use the district-centroid XY as the scheme extent — zoom to the union of that scheme’s polygon and line.

## Version 72ae vs 092e

| UID | Change |
|---|---|
| IS-06 Yakawlang | `KDZ-BGN-A2-01` → `KDZ-BGN-A1-01` (no longer clashes with WSM-06) |
| IS-06 name | `Chsrbagh-2` → `Charbagh-2` in the scheme name |
| WSM-07 package | “Ety Orugh Check dams” → “Ety Aregh Check dams” |

## Non-GPS checklist (72ae)

| Item | Status |
|---|---|
| Unique IDs and unique `SCHEME_CODE` | **Pass — 14 of 14** |
| Shawaroz IS / WSM | Pass — `KDR-ZBL-A1-01` / `A2-01` |
| Yakawlang IS / WSM | Pass — `KDZ-BGN-A1-01` / `A2-01` |
| WSM costs are real USD | Pass |
| Yakawlang IS end date | Pass — `2027-06-24` |
| Female-headed HH | Still blank on WSM-03 and WSM-05 |
| Site GPS / surveyed polygon + line | Deferred — placeholders in use |
| Village spelling | Cosmetic — villages still say Chsrbagh; WSM name still Ety Orugh |

## Totals (awarded costs)

- 9 awarded / 5 not awarded
- Awarded cost **$2,294,514** (irrigation $2,053,275 + WSM $241,239)

## Clean flags

- `MISSING_FHH` on WSM-03 and WSM-05
- `NO_CANAL_EXPECTED` on all seven WSM rows (correct)
