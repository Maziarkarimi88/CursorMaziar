# KOBO groundwater monitoring — analysis summary

DTW change = typical water level before − latest measured depth. **Positive = shallower now (water rose).** Wells with unit-confusion, DTW deeper than well depth, DTW > 100 m, or distance > 5 km are excluded from impact medians.

## Counts

- Visits kept: **3354** (dropped 26 empty rows)
- Unique wells: **1352** in 30 provinces, 85 districts, 426 villages
- Wells used for impact tables: **1267** (85 excluded by QA)
- Measurement dates: 2024-12-30 to 2026-09-16
- Repeat visits: 958 wells with 1 visit; 394 with 2+; 230 with 4+; 117 with ≥8 unique dates

## Median recalled DTW change (m)

- All usable wells: **0.19**
- First-to-last measured DTW, wells with ≥4 visits: **0.0**

By intervention:

- Both: 0.1
- Check dam: 0.5
- Trench: 0.0

By distance (m):

- 0-200: 0.7
- 1000-2000: 0.0
- 200-500: 0.14
- 500-1000: 0.0
- >2000: -1.0

By relative location:

- Downstream: 0.0
- Upstream: 0.5

## QA flag counts (visit-level)

- dtw_jump: 179
- recall_extreme: 166
- form_clone: 88
- wt_now_gt_depth: 72
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
| Kapisa | 263 | 0.90 |
| Panjsher | 172 | 0.48 |
| Parwan | 143 | 0.23 |
| Kunduz | 118 | -0.11 |
| Daykundi | 63 | 1.00 |
| Paktya | 54 | -16.00 |
| Kunar | 48 | 0.00 |
| Faryab | 46 | 0.60 |
| Kabul | 35 | -2.77 |
| Maidan Wardak | 35 | 0.05 |
| Jawzjan | 29 | -0.80 |
| Bamyan | 27 | 0.30 |
| Sar-e-Pul | 25 | -0.30 |
| Farah | 23 | -3.10 |
| Khost | 22 | 5.60 |
| Paktika | 21 | -1.00 |
| Balkh | 21 | 1.00 |
| Helmand | 19 | 0.00 |
| Logar | 19 | -0.15 |
| Laghman | 17 | 0.25 |
| Nangarhar | 16 | 0.00 |
| Nimroz | 10 | 0.00 |
| Uruzgan | 8 | 3.83 |
| Badghis | 8 | 0.38 |
| Ghazni | 7 | 2.00 |
| Kandahar | 7 | -1.00 |
| Ghor | 6 | 0.00 |
| Zabul | 5 | 5.35 |

## How to read this

- Recalled before vs now is a **snapshot + memory**, not a designed before/after.
- First-to-last measured DTW on short series is mostly **season**, not dam impact.
- Do not run Mann–Kendall / Sen on the full file; series are at most about one year.
- Check-dam wells are concentrated in Kapisa and Kunar; do not generalise that mix as a national check-dam effect.
- Paktya’s large negative median is a few villages with the same well depth and the same “before” DTW copied across many owners — treat as enumerator cloning, not 49 independent declines.
- Some long hydrographs (for example Logar / Bala deh) jump several metres between visits; that is a measurement or well-ID problem, not a real weekly water-table swing.
