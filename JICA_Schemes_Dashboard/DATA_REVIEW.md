# JICA IS + WSM schemes — data review

Latest source: `data/raw_Both_Jica_Irrigation_and_WSM_Schemes_092e.csv`  
Rows that can go on a map: **14** (7 irrigation + 7 watershed). Site GPS will come later; points stay on **district centroids**.

Upload file: `data/schemes_dashboard.csv`. Rebuild: `python3 scripts/clean_schemes.py`.

## Version 092e vs 3313

| UID | Change |
|---|---|
| IS-06 Yakawlang | `KDZ-BGN-A1-01` → `KDZ-BGN-A2-01` (now clashes with WSM-06) |
| WSM-01 Sorkh Joy | `BMN-BMN-A1-02` → `BMN-BMN-A2-01` (matches A2 pattern) |
| WSM-03 Yar Mohammad | “Rehabilitation fo” → “Rehabilitation for” |
| WSM-05 Shawaroz | `KDR-ZBL-A1-01` → `KDR-ZBL-A2-01` (no longer clashes with IS-05) |

Costs, dates, status, households, and contractors are unchanged.

## Non-GPS checklist (092e)

| Item | Status |
|---|---|
| Unique IDs | Pass |
| WSM costs are real USD | Pass |
| Yakawlang IS end date | Pass — `2027-06-24` |
| Shawaroz IS + WSM codes | **Fixed** — `KDR-ZBL-A1-01` / `KDR-ZBL-A2-01` |
| Sorkh Joy WSM pattern | **Fixed** — `BMN-BMN-A2-01` |
| “Rehabilitation fo” typo | **Fixed** |
| Yakawlang IS + WSM code | **New clash** — both `KDZ-BGN-A2-01` |
| Female-headed HH | Still blank on WSM-03 and WSM-05 |
| Site GPS | Deferred — district centroids |
| Name spelling | Cosmetic — Shir Abd / Shir Abad; Ety Aregh / Ety Orugh; Chsrbagh |

Put Yakawlang irrigation back to `KDZ-BGN-A1-01` (as in 3313). Leave WSM as `KDZ-BGN-A2-01`.

## Totals (awarded costs)

- 9 awarded / 5 not awarded
- Awarded cost **$2,294,514** (irrigation $2,053,275 + WSM $241,239)

## Clean flags

- `DUPLICATE_SCHEME_CODE` on IS-06 and WSM-06
- `MISSING_FHH` on WSM-03 and WSM-05
- `NO_CANAL_EXPECTED` on all seven WSM rows (correct)
