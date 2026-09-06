# JICA IS + WSM schemes — data review

Latest source: `data/raw_Both_Jica_Irrigation_and_WSM_Schemes_3313.csv`  
Rows that can go on a map: **14** (7 irrigation + 7 watershed). Site GPS will come later; points stay on **district centroids**.

Upload file: `data/schemes_dashboard.csv`. Rebuild: `python3 scripts/clean_schemes.py`.

## Version 3313 vs 6106

Only `SchemeCode` changed. Costs, dates, status, households, and contractors are the same.

| UID | 6106 | 3313 |
|---|---|---|
| IS-04 Shah Joy | `KBL-WRK-JCA-A1-01` | `KBL-WRK-A1-01` |
| IS-06 Yakawlang | `KDZ-BGN-JICA-A1-01` | `KDZ-BGN-A1-01` |
| WSM-01 Sorkh Joy | `BMN-BMN-02` | `BMN-BMN-A1-02` |
| WSM-02 Shir Abad | `GDZ-GZI-Shir-Abad-02` | `GDZ-GZI-A2-01` |
| WSM-03 Yar Mohammad | `HRT-HRT-JCA` | `HRT-HRT-A2-01` |
| WSM-04 Shah Joy | `KBL-WRK-JCA-A1-02` | `KBL-WRK-A2-01` |
| WSM-06 Yakawlang | `KDZ-BGN-134-B1- 01` | `KDZ-BGN-A2-01` |
| WSM-07 Ety Orugh | `MZR-FRB-B-01` | `MZR-FRB-A2-01` |

## Non-GPS checklist (3313)

| Item | Status |
|---|---|
| Unique IDs (`UNID` / `SCHEME_UID`) | Pass — 14 aligned |
| WSM costs are real USD (not Excel dates) | Pass — $51,075 / $61,696 / $128,468 |
| Yakawlang IS end date | Pass — `2027-06-24` (395 days) |
| Yakawlang WSM space in code | **Fixed** — now `KDZ-BGN-A2-01` |
| Shah Joy / Shir Abad / most WSM codes unique | **Fixed** — A1 / A2 pattern |
| Shawaroz IS + WSM code | **Still open** — both `KDR-ZBL-A1-01` |
| Female-headed HH | **Still open** on WSM-03 (2,250 HH) and WSM-05 (260 HH) |
| Package typo “Rehabilitation fo” | **Still open** on WSM-03 |
| Site GPS | Deferred — district centroids in use |
| Name spelling | Cosmetic — Shir Abd vs Shir Abad; Ety Aregh vs Ety Orugh; Chsrbagh |

Sorkh Joy WSM is `BMN-BMN-A1-02` while other watershed codes use `A2-01`. Not a clash, just a different pattern. Herat irrigation stays `HRT-HRT-A1-22`.

Suggested Shawaroz WSM code to match the new pattern: `KDR-ZBL-A2-01`.

## Totals (awarded costs)

- 9 awarded / 5 not awarded
- Awarded cost **$2,294,514** (irrigation $2,053,275 + WSM $241,239)
- Do not sum IS + WSM households at the same site — the lists differ

## Clean flags

- `DUPLICATE_SCHEME_CODE` on IS-05 and WSM-05
- `MISSING_FHH` on WSM-03 and WSM-05
- `NO_CANAL_EXPECTED` on all seven WSM rows (correct)

## Next step

The table is usable for a first dashboard on district centroids. The only code clash left is Shawaroz. Confirm `KDR-ZBL-A2-01` (or send your official code) and we bind this as the main JICA layer.
