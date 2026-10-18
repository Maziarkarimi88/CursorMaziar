# Teaching example: 10 wells, weekly levels, Mann–Kendall + Sen’s slope

Not real Kandahar measurements. Seed-built series so you can **practice** MK, p-value, and Sen’s slope on the same table as the field layout (near dam, mid, far, karez *sarchah*, control).

- `mk_sen_10wells_weekly.csv` — 104 Sundays, 2024-01-07 to 2025-12-28. Values are **water level (m)**; **higher = more water**.
- `run_mk_sen_weekly.py` — prints MK trend, p-value, Sen m/year, and Hamed–Rao modified MK (better for weekly autocorrelation).

```bash
pip install pandas pymannkendall
python3 examples/run_mk_sen_weekly.py
```

Interpret with **modified p-value** on weekly data. Original p can look “significant” only because each week looks like last week.
