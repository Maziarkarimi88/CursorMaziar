# KOBO groundwater monitoring export

Place the cleaned FAO KOBO export here as `groundwater_monitoring.csv`
(Windows-1252 or UTF-8). The raw file is gitignored because it contains
owner names and phone numbers.

```bash
python3 tools/kobo_gw.py --csv data/kobo/groundwater_monitoring.csv
```

Outputs go to `examples/kobo_gw/` (tables) and `figures/kobo_gw/` (plots).
See `docs/KOBO_GW_MONITORING_ANALYSIS.md`.
