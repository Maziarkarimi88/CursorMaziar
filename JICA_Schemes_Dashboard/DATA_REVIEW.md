# JICA IS + WSM schemes — data review

Latest source: `data/raw_Both_Jica_Irrigation_and_WSM_Schemes_19a6.csv`  
Rows that can go on a map: **14** (7 irrigation + 7 watershed). Trailing blank row dropped.

## Version 19a6 vs first upload

Fixed: WSM 01–03 now have real USD (`51,075` / `61,696` / `128,468`) instead of Excel dates. Yakawlang IS end date is `24-Jun-27` (395 days). Shah Joy codes split to `KBL-WRK-JCA-A1-01` / `A1-02`. `Awarding_Status` is its own column.

Still wrong in the raw 19a6 file: the `UNID` column is **shifted down one row**. Row 1001 (Sorkh Joy IS) has `UNID=SCHEME_UID`. Package 2 IS is labeled `JICA-IS-01`. Sorkh Joy WSM is labeled `JICA-IS-07`. Ignore `UNID` — we rebuild `SCHEME_UID` from package number + program.

`Contract_Cost_USD` still uses thousands commas. No `LON`/`LAT`. Shawaroz WSM still has no scheme code. `Cosntrution_Company` typo remains.

This is a **program tracker**, not the MetroTel telecom sample. The Pulse/Atlas dashboards can still be reused, but the fields must change to cost, households, area, status, and program type.

## Can we upload it as-is?

No. The raw sheet will break a dashboard in four ways:

1. **No coordinates.** ArcGIS cannot place points from Province/District text alone.
2. **Numbers are text.** `428,787` and `1,260` will not Sum/Average until commas are removed.
3. **Three WSM “costs” are dates.** `31-Oct-39`, `29-Nov-68`, `23-Sep-51` are almost certainly Excel cells that were formatted as dates. They must not be summed.
4. **No unique ID / no status field.** Package 4 irrigation and WSM both use `KBL-WRK-JCA-01`. “Not Awarded” is sitting in the cost column.

## What we cleaned (use this file)

`data/schemes_dashboard.csv` — 14 rows, 30 dashboard fields.

| New field | Role on the dashboard |
|---|---|
| `SCHEME_UID` | Unique id (`JICA-IS-01` … `JICA-WSM-07`) |
| `PAIR_ID` | Links the irrigation + WSM works at the same site (`SITE-01` … `07`) |
| `PROGRAM` | Irrigation / Watershed (pie + filter) |
| `STATUS` | Awarded / Not Awarded (KPI + list) |
| `REGION`, `REGION_HUB`, `PROVINCE`, `DISTRICT`, `VILLAGE` | Geography filters |
| `CONTRACT_START`, `CONTRACT_END` | ISO dates `YYYY-MM-DD` |
| `DURATION_DAYS` | Contract length |
| `COST_USD` | Integer USD (blank if unknown / not awarded) |
| `AREA_HA`, `HOUSEHOLDS`, `FEMALE_HEADED_HH`, `FHH_PCT` | Benefit KPIs |
| `CANAL_KM` | Irrigation only |
| `COST_PER_HA`, `COST_PER_HH` | Efficiency |
| `LON`, `LAT` | Map (district centroid — **approximate**) |
| `DATA_FLAGS` | QA notes for you, hide from the public view |

Rebuild anytime: `python scripts/clean_schemes.py`

## Please confirm / fix before we treat this as final

| Row | Issue | Suggested action |
|---|---|---|
| WSM 01–03 | Cost exported as a date | Paste the real USD from the contract |
| IS-06 Yakawlang | End date `2026-06-24` is 30 days after start | Likely `2027-06-24`? |
| WSM-05 Shawaroz | Empty `SCHEME_CODE` | Add the official code |
| IS-04 and WSM-04 | Same raw code `KBL-WRK-JCA-01` | Keep our `SCHEME_UID`; fix source codes |
| All rows | XY is **district** centroid, not the canal/check-dam | Replace with site GPS when you have it |
| Names | Shir Abd / Shir Abad, Ety Aregh / Ety Orugh, Chsrbagh | Pick one spelling |

Households at the same site are **not always equal** (e.g. Shir Abad IS 1,056 vs WSM 426). That may be correct (different beneficiary lists). Do not blindly copy IS households onto WSM.

## Dashboard widgets this table can drive

- Indicators: schemes (14), awarded, not awarded, sum `COST_USD` (irrigation only until WSM costs are fixed), sum `HOUSEHOLDS`, sum `AREA_HA`, sum `CANAL_KM`
- Map: points by `PROGRAM` color; pop-up = name, status, cost, households
- Pie: `PROGRAM`; pie or donut: `STATUS`
- Bar: `COST_USD` by `PROVINCE` or `SCHEME_NAME` (awarded only)
- List: not-awarded packages
- Selectors: `PROGRAM`, `STATUS`, `PROVINCE`, `REGION`

Do **not** put `COST_USD` on a total if `DATA_FLAGS` contains `COST_LOOKS_LIKE_EXCEL_DATE`. The clean file already blanks those cells.

## Next step

If you accept `schemes_dashboard.csv` (and send the three missing WSM costs + GPS if you have them), we will bind it as the **main upload layer** for a JICA schemes dashboard — same publish path as Pulse/Atlas, new widgets for this program.
