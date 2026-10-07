# KOBO groundwater monitoring — analysis summary

DTW change = typical water level before − latest measured depth. **Positive = shallower now (water rose).** Wells with unit-confusion, DTW deeper than well depth, DTW > 100 m, or distance > 5 km are excluded from impact medians.

## Counts

- Visits kept: **3354** (dropped 26 empty rows)
- Unique wells: **1081** in 30 provinces, 85 districts, 321 villages
- Wells used for impact tables: **1016** (65 excluded by QA)
- Measurement dates: 2024-12-30 to 2026-09-16
- Repeat visits: 533 wells with 1 visit; 548 with 2+; 298 with 4+; 99 with ≥8 unique dates

## Median recalled DTW change (m)

- All usable wells: **0.15**
- First-to-last measured DTW, wells with ≥4 visits: **0.0**

By intervention:

- Both: 0.2
- Check dam: 0.3
- Trench: -0.5

By distance (m):

- 0-200: 0.8
- 1000-2000: 0.15
- 200-500: 0.0
- 500-1000: 0.0
- >2000: -1.0

By relative location:

- Downstream: 0.0
- Upstream: 0.5

## QA flag counts (visit-level)

- owner_mixed: 813
- dtw_jump: 298
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
| Kapisa | 216 | 1.00 |
| Parwan | 148 | 0.20 |
| Panjsher | 105 | 0.50 |
| Kunduz | 88 | -0.10 |
| Kunar | 46 | 0.00 |
| Daykundi | 41 | 1.00 |
| Kabul | 36 | -3.25 |
| Balkh | 34 | 1.50 |
| Faryab | 31 | -0.20 |
| Logar | 27 | 0.10 |
| Jawzjan | 24 | -0.80 |
| Maidan Wardak | 24 | -0.22 |
| Bamyan | 22 | 0.30 |
| Khost | 21 | 6.20 |
| Paktya | 15 | -16.00 |
| Laghman | 15 | 0.25 |
| Farah | 15 | -3.40 |
| Helmand | 15 | 0.00 |
| Paktika | 14 | -1.30 |
| Nangarhar | 13 | 0.00 |
| Zabul | 12 | 4.43 |
| Nimroz | 11 | 0.00 |
| Sar-e-Pul | 11 | -0.30 |
| Kandahar | 8 | -1.00 |
| Ghazni | 7 | 1.35 |
| Badghis | 6 | -0.50 |
| Ghor | 6 | 0.00 |
| Uruzgan | 5 | 0.20 |

## How to read this

- Recalled before vs now is a **snapshot + memory**, not a designed before/after.
- First-to-last measured DTW on short series is mostly **season**, not dam impact.
- Do not run Mann–Kendall / Sen on the full file; series are at most about one year.
- Check-dam wells are concentrated in Kapisa and Kunar; do not generalise that mix as a national check-dam effect.
- Paktya’s large negative median is a few villages with the same well depth and the same “before” DTW copied across many owners — treat as enumerator cloning, not 49 independent declines.
- Some long hydrographs (for example Logar / Bala deh) jump several metres between visits; that is a measurement or well-ID problem, not a real weekly water-table swing.
