# KOBO groundwater monitoring — analysis summary

DTW change = typical water level before − latest measured depth. **Positive = shallower now (water rose).** Wells with unit-confusion, DTW deeper than well depth, DTW > 100 m, or distance > 5 km are excluded from impact medians.

## Counts

- Visits kept: **3354** (dropped 26 empty rows)
- Unique wells: **1015** in 30 provinces, 84 districts, 406 villages
- Wells used for impact tables: **933** (82 excluded by QA)
- Measurement dates: 2024-12-30 to 2026-09-16
- Repeat visits: 638 wells with 1 visit; 377 with 2+; 257 with 4+; 137 with ≥8 unique dates

## Median recalled DTW change (m)

- All usable wells: **0.2**
- First-to-last measured DTW, wells with ≥4 visits: **0.0**

By intervention:

- Both: 0.1
- Check dam: 0.5
- Trench: 0.01

By distance (m):

- 0-200: 0.6
- 1000-2000: -0.2
- 200-500: 0.0
- 500-1000: 0.15
- >2000: -1.2

By relative location:

- Downstream: 0.0
- Upstream: 0.5

## QA flag counts (visit-level)

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
| Panjsher | 166 | 0.50 |
| Kapisa | 118 | 1.00 |
| Parwan | 87 | 0.23 |
| Kunduz | 82 | 0.20 |
| Daykundi | 60 | 1.00 |
| Paktya | 49 | -16.00 |
| Kunar | 47 | 0.00 |
| Kabul | 32 | -2.51 |
| Jawzjan | 31 | -0.80 |
| Sar-e-Pul | 30 | -0.05 |
| Maidan Wardak | 29 | -0.07 |
| Bamyan | 24 | 0.30 |
| Faryab | 21 | -0.50 |
| Balkh | 19 | 2.30 |
| Paktika | 18 | -0.85 |
| Laghman | 17 | 0.25 |
| Farah | 17 | -3.20 |
| Helmand | 15 | 0.00 |
| Nangarhar | 12 | 0.00 |
| Khost | 10 | 6.15 |
| Uruzgan | 10 | 6.00 |
| Nimroz | 9 | 0.00 |
| Badghis | 8 | 0.12 |
| Ghor | 6 | 0.00 |
| Logar | 5 | -0.15 |
| Ghazni | 5 | 3.10 |
| Zabul | 4 | 2.27 |
| Kandahar | 2 | -0.50 |

## How to read this

- Recalled before vs now is a **snapshot + memory**, not a designed before/after.
- First-to-last measured DTW on short series is mostly **season**, not dam impact.
- Do not run Mann–Kendall / Sen on the full file; series are at most about one year.
- Check-dam wells are concentrated in Kapisa and Kunar; do not generalise that mix as a national check-dam effect.
- Paktya’s large negative median is a few villages with the same well depth and the same “before” DTW copied across many owners — treat as enumerator cloning, not 49 independent declines.
- Some long hydrographs (for example Logar / Bala deh) jump several metres between visits; that is a measurement or well-ID problem, not a real weekly water-table swing.
