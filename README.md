# Check-dam groundwater assessment toolkit

Field methods to measure whether small check dams on **Kandahar and Zabul alluvial fans** actually recharge the wells and karez that people use.

This is a simple, low-cost protocol copied from farmer-run check-dam studies in Rajasthan (MARVI / Dashora), karez geometry in Afghanistan, and cascade-dam work in Yemen. It does not start with a groundwater model.

## Documents

| File | Use |
|------|-----|
| [`docs/FIELD_PROTOCOL_Kandahar_Zabul.md`](docs/FIELD_PROTOCOL_Kandahar_Zabul.md) |  Print this first (about six pages). How to site gauges, sample wells and karez, calculate I1–I5. |
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
