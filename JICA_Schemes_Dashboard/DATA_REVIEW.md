# JICA IS + WSM schemes — data review

Latest source: `data/raw_Both_Jica_Irrigation_and_WSM_Schemes_6106.csv`  
Rows that can go on a map: **14** (7 irrigation + 7 watershed).

This is a **program tracker**, not the MetroTel telecom sample. Use `data/schemes_dashboard.csv` as the upload layer.

## Version history

| File | What changed |
|---|---|
| `4930` | First export. No XY. WSM 01–03 costs were Excel dates. “Not Awarded” sat in the cost column. Shah Joy IS/WSM shared one code. Yakawlang IS end date was 30 days. |
| `19a6` | Real WSM USD (`51,075` / `61,696` / `128,468`). Yakawlang IS end `24-Jun-27`. `Awarding_Status` split out. Shah Joy codes `A1-01` / `A1-02`. Raw `UNID` shifted down one row. |
| `a35a` | `UNID` aligned. Contractor column renamed `Construction_Company`. Shawaroz WSM code was `GDZ-GZI-Shir-Abad-01` (Ghazni family, wrong site). |
| **`6106` (current)** | `UNID` still aligned. Shawaroz WSM code changed to `KDR-ZBL-A1-01` (correct Zabul family) **but it is now identical to Shawaroz irrigation**. Shawaroz IS code shortened from `KDR-ZBL-JICA-A1-01` to `KDR-ZBL-A1-01`. |

## What 6106 still needs

| Row | Issue | Suggested action |
|---|---|---|
| IS-05 + WSM-05 Shawaroz | Same `SCHEME_CODE` `KDR-ZBL-A1-01` | Give WSM its own code, e.g. `KDR-ZBL-A1-02` or `KDR-ZBL-B1-01`. Keep our `SCHEME_UID` (`JICA-IS-05` / `JICA-WSM-05`) either way. |
| WSM-06 Yakawlang | Space in `KDZ-BGN-134-B1- 01` | Drop the space: `KDZ-BGN-134-B1-01` |
| WSM-03 | Empty female-headed HH; “Rehabilitation fo” in the package name | Fill FHH if known; fix typo |
| All rows | XY is **district** centroid, not the canal / check dam | Replace with site GPS when you have it |
| Names | Shir Abd / Shir Abad, Ety Aregh / Ety Orugh, Chsrbagh | Pick one spelling |

Households at the same site are **not always equal** (Shir Abad IS 1,056 vs WSM 426; Shawaroz IS 3,250 vs WSM 260). That may be correct (different beneficiary lists). Do not copy IS households onto WSM.

## Clean file (use this)

`data/schemes_dashboard.csv` — 14 rows, 31 dashboard fields. Rebuild: `python3 scripts/clean_schemes.py` (picks the newest `raw_Both_Jica*.csv`).

| New field | Role on the dashboard |
|---|---|
| `SCHEME_UID` | Unique id (`JICA-IS-01` … `JICA-WSM-07`) |
| `PAIR_ID` | Links the irrigation + WSM works at the same site (`SITE-01` … `07`) |
| `PROGRAM` | Irrigation / Watershed (pie + filter) |
| `STATUS` | Awarded / Not Awarded (KPI + list) |
| `REGION`, `REGION_HUB`, `PROVINCE`, `DISTRICT`, `VILLAGE` | Geography filters |
| `CONTRACT_START`, `CONTRACT_END` | ISO dates `YYYY-MM-DD` |
| `DURATION_DAYS` | Contract length |
| `COST_USD` | Integer USD (blank if not awarded) |
| `AREA_HA`, `HOUSEHOLDS`, `FEMALE_HEADED_HH`, `FHH_PCT` | Benefit KPIs |
| `CANAL_KM` | Irrigation only |
| `COST_PER_HA`, `COST_PER_HH` | Efficiency |
| `LON`, `LAT` | Map (district centroid — **approximate**) |
| `DATA_FLAGS` | QA notes; hide from the public view |

Current flags: `DUPLICATE_SCHEME_CODE` on IS-05 and WSM-05; `NO_CANAL_EXPECTED` on all seven WSM rows.

## Totals (6106, awarded costs only)

- Schemes: 14
- Awarded: 9 / Not awarded: 5 (Shawaroz IS+WSM, Shah Joy WSM, Yakawlang WSM, Ety Orugh WSM)
- Awarded cost: **$2,294,514** (irrigation $2,053,275 + WSM $241,239)
- Households: do **not** sum IS + WSM at the same site without a rule — they are different lists

## Dashboard widgets this table can drive

- Indicators: schemes (14), awarded, not awarded, sum `COST_USD` (awarded only), sum `AREA_HA`, sum `CANAL_KM`
- Map: points by `PROGRAM` color; pop-up = name, status, cost, households
- Pie: `PROGRAM`; donut: `STATUS`
- Bar: `COST_USD` by `PROVINCE` or `SCHEME_NAME` (awarded only)
- List: not-awarded packages
- Selectors: `PROGRAM`, `STATUS`, `PROVINCE`, `REGION`

Do **not** put `COST_USD` on a total if `DATA_FLAGS` contains `COST_LOOKS_LIKE_EXCEL_DATE`. The clean file already blanks those cells.

## Next step

Confirm the Shawaroz WSM code (or send site GPS). After that we bind `schemes_dashboard.csv` as the **main upload layer** for a JICA schemes dashboard — same publish path as Pulse/Atlas, new widgets for this program.
