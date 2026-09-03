# Check-dam groundwater assessment toolkit

Field methods to measure whether small **rainfall-fed check dams** (design hold **about 1–3 months when full**) actually recharge the wells and karez that people use. The worked setting is Kandahar and Zabul fans; the hold-time and fill calculations apply in other Afghan provinces too.

This is a simple, low-cost protocol copied from farmer-run check-dam studies in Rajasthan (MARVI / Dashora), karez geometry in Afghanistan, and cascade-dam work in Yemen. It does not start with a groundwater model.

## Documents

| File | Use |
|------|-----|
| [`docs/FIELD_PROTOCOL_Kandahar_Zabul.md`](docs/FIELD_PROTOCOL_Kandahar_Zabul.md) | Print this first (about six pages). How to site gauges, sample wells and karez, calculate I1–I5. |
| [`docs/STORAGE_DURATION_AND_FILLING.md`](docs/STORAGE_DURATION_AND_FILLING.md) | What controls 1–3 month hold; rainfall (SCS-CN) to fill the **pond** to crest (not the catchment). |
| [`docs/ARCGIS_STORAGE_FROM_DEM.md`](docs/ARCGIS_STORAGE_FROM_DEM.md) | ArcGIS Surface Volume / Storage Capacity: \(A(h), V(h)\) from DEM at 2–6 m crest. |
| [`docs/ANNEX_A_Flood_Detention_Check_Dams.md`](docs/ANNEX_A_Flood_Detention_Check_Dams.md) | Only if a dam actually empties in hours (gabion/leaky outlier). |
| [`docs/COUNTRY_STORIES_AND_METHODS.md`](docs/COUNTRY_STORIES_AND_METHODS.md) | Methods and field stories from Pakistan, Tunisia, Ethiopia, Arizona, Oman, Spain, Cyprus, Morocco, Yemen, India, China, Kenya — similar dry climates. |
| [`docs/WAPOR_SUITABILITY.md`](docs/WAPOR_SUITABILITY.md) | Why FAO WaPOR is basin ET/biomass context only — not a substitute for I4/I5 on these dams. |
| [`docs/forms/`](docs/forms/) |  Form A setup, Form B daily pond, Form C wells/karez, Form D scorecard, observer card. |
| [`figures/sampling_layout.png`](figures/sampling_layout.png) |  Where to put W-N, W-M, W-F, control wells, *sarchah* and *owkura*. |
| [`templates/CheckDam_Recharge_Calculator.xlsx`](templates/CheckDam_Recharge_Calculator.xlsx) |  Yellow = type field data. Blue = formulas. An example spring filling is already entered. |
| [`templates/README.md`](templates/README.md) |  Spreadsheet layout and the Dashora dry-day rule. |

## Verify

```bash
pip install -r requirements.txt
python3 tools/build_protocol_assets.py
python3 tests/test_water_balance.py
python3 tests/test_workbook.py
```

## What you get after one wet season

- **I1** infiltration volume from the pond (m³)
- **I2** fillings per year
- **I3** mean dry-weather infiltration rate (desilting trigger)
- **I4** extra water-table rise versus a control fan
- **I5** extra karez-flow days

## License of the method

Cite the papers listed in section 9 of the protocol. The forms and workbook in this repository are for project use.
