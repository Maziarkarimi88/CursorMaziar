# KOBO groundwater monitoring — analysis summary

DTW change = typical water level before − latest measured depth. **Positive = shallower now (water rose).** Wells with unit-confusion, DTW deeper than well depth, DTW > 100 m, or distance > 5 km are excluded from impact medians.

## Counts

- Visits kept: **3354** (dropped 26 empty rows)
- Unique wells: **1224** in 30 provinces, 86 districts, 339 villages
- Wells used for impact tables: **1151** (73 excluded by QA)
- Measurement dates: 2024-12-30 to 2026-09-16
- Repeat visits: 618 wells with 1 visit; 606 with 2+; 282 with 4+; 78 with ≥8 unique dates

## Median recalled DTW change (m)

- All usable wells: **0.19**
- First-to-last measured DTW, wells with ≥4 visits: **-0.06**

By intervention:

- Both: 0.21
- Check dam: 0.39
- Trench: -0.54

By distance (m):

- 0-200: 0.77
- 1000-2000: 0.17
- 200-500: 0.0
- 500-1000: 0.0
- >2000: -1.0

By relative location:

- Downstream: 0.0
- Upstream: 0.5

## QA flag counts (visit-level)

- owner_mixed: 769
- dtw_jump: 274
- recall_extreme: 166
- wt_now_gt_depth: 72
- form_clone: 68
- diameter_suspect: 63
- unit_confusion: 59
- distance_gt_5000: 54
- hh_implausible: 23
- meas_before_interv: 14
- wt_now_zero: 5
- hh_looks_like_phone: 4
- est_rise_gt_20: 4
- diameter_outlier: 3
- wt_now_gt_100: 2

## Usable wells by province (median recalled DTW change)

| Province | Wells | Median change (m) |
|---|---:|---:|
| Kapisa | 235 | 0.90 |
| Parwan | 179 | 0.32 |
| Panjsher | 124 | 0.50 |
| Kunduz | 95 | -0.10 |
| Daykundi | 52 | 1.00 |
| Kunar | 46 | 0.00 |
| Kabul | 42 | -2.97 |
| Balkh | 40 | 1.55 |
| Faryab | 33 | 0.40 |
| Logar | 30 | 0.10 |
| Maidan Wardak | 29 | -0.20 |
| Jawzjan | 25 | -0.80 |
| Bamyan | 22 | 0.30 |
| Khost | 22 | 6.50 |
| Paktya | 18 | -16.50 |
| Laghman | 17 | 0.25 |
| Paktika | 17 | -1.20 |
| Helmand | 17 | 0.00 |
| Farah | 15 | -3.40 |
| Zabul | 15 | 3.70 |
| Sar-e-Pul | 15 | -0.50 |
| Nangarhar | 14 | 0.00 |
| Nimroz | 11 | 0.00 |
| Ghazni | 9 | 1.35 |
| Badghis | 8 | 0.05 |
| Kandahar | 8 | -1.00 |
| Uruzgan | 7 | 7.50 |
| Ghor | 6 | 0.00 |

## How to read this

- Recalled before vs now is a **snapshot + memory**, not a designed before/after.
- First-to-last measured DTW on short series is mostly **season**, not dam impact.
- Do not run Mann–Kendall / Sen on the full file; series are at most about one year.
- Check-dam wells are concentrated in Kapisa and Kunar; do not generalise that mix as a national check-dam effect.
- Paktya’s large negative median is a few villages with the same well depth and the same “before” DTW copied across many owners — treat as enumerator cloning, not 49 independent declines.
- Some long hydrographs (for example Logar / Bala deh) jump several metres between visits; that is a measurement or well-ID problem, not a real weekly water-table swing.
