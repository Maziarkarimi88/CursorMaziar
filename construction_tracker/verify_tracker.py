#!/usr/bin/env python3
"""Structural checks for the generated construction tracker workbook."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook

from generate_tracker import (
    DATA_START,
    HEADER_ROW,
    Layout,
    SHEET_DASH,
    SHEET_DOMAINS,
    SHEET_EXAMPLE,
    SHEET_GEO,
    SHEET_HOWTO,
    SHEET_LOOKUPS,
    SHEET_PIPELINE,
    SHEET_TRACKER,
    duration_formula,
)
from tracker_config import EXAMPLE_SCHEMES, SCHEMES, STATUS_PIPELINE

ROOT = Path(__file__).resolve().parent
XLSX = ROOT / "WBK_AF2_Construction_Works_Tracker.xlsx"


def days_between(a: str, b: str) -> int:
    d0 = datetime.strptime(a, "%Y-%m-%d")
    d1 = datetime.strptime(b, "%Y-%m-%d")
    return (d1 - d0).days


def expected_demo_durations(scheme: dict) -> list[tuple[str, str, int]]:
    """Mirror the Excel rule: days from last previous filled date into this date."""
    names = [s["name"] for s in STATUS_PIPELINE]
    dates = scheme["status_dates"]
    filled: list[tuple[str, str]] = []
    result = []
    for name in names:
        if name not in dates:
            continue
        if filled:
            prev_name, prev_date = filled[-1]
            result.append((prev_name, name, days_between(prev_date, dates[name])))
        filled.append((name, dates[name]))
    first = filled[0][1]
    last = filled[-1][1]
    total = days_between(first, last)
    return result, total, filled[-1][0]


def main() -> None:
    assert XLSX.exists(), f"missing {XLSX}"
    wb = load_workbook(XLSX)
    expected_sheets = [
        SHEET_HOWTO,
        SHEET_TRACKER,
        SHEET_DASH,
        SHEET_EXAMPLE,
        SHEET_PIPELINE,
        SHEET_DOMAINS,
        SHEET_GEO,
        SHEET_LOOKUPS,
    ]
    assert wb.sheetnames == expected_sheets, wb.sheetnames

    layout = Layout()
    tracker = wb[SHEET_TRACKER]
    example = wb[SHEET_EXAMPLE]

    # Pre-loaded live schemes
    live_ids = [tracker.cell(DATA_START + i, layout.idx["scheme_id"]).value for i in range(len(SCHEMES))]
    assert live_ids == [s["scheme_id"] for s in SCHEMES], live_ids[:5]

    # Awarded / completed rows carry those dates from the master file
    awarded_dates = 0
    for i in range(len(SCHEMES)):
        row = DATA_START + i
        if any(tracker.cell(row, col).value not in (None, "") for col in layout.status_date_cols):
            awarded_dates += 1
    assert awarded_dates > 0, "expected awarded/completed dates from the master file"
    assert "schedule_health" in layout.idx

    # Example dates present
    demo = EXAMPLE_SCHEMES[0]
    for i, slot in enumerate(layout.slots):
        name = slot["name"]
        col = layout.status_date_cols[i]
        value = example.cell(DATA_START, col).value
        if name in demo["status_dates"]:
            assert value is not None, f"missing demo date for {name}"
            assert value.strftime("%Y-%m-%d") == demo["status_dates"][name]
        else:
            assert value in (None, "")

    transitions, total, last_status = expected_demo_durations(demo)
    print("DEMO-01 expected transitions:")
    for a, b, d in transitions:
        print(f"  {a} → {b}: {d} days")
    print(f"  total first→last: {total} days")
    print(f"  last status: {last_status}")

    assert transitions[0] == ("Under Design", "Under Review of WRI", 25)
    assert transitions[1][2] == 14
    assert total == 263
    assert last_status == "Completed / Handover"

    # Formulas exist on data rows
    row = DATA_START
    assert str(tracker.cell(row, layout.idx["current_status"]).value).startswith("IF(")
    assert "TODAY()" in str(tracker.cell(row, layout.idx["days_in_current"]).value)
    assert "EDATE(" in str(tracker.cell(row, layout.idx["planned_end_date"]).value)
    awarded_f = str(tracker.cell(row, layout.idx["awarded_date"]).value)
    assert awarded_f.startswith("IF("), awarded_f
    dur_f = str(tracker.cell(row, layout.duration_cols[0]).value)
    assert "LOOKUP(2,1/" in dur_f
    assert dur_f == duration_formula(layout, row, 1)

    # Headers pull from the pipeline sheet
    date0 = tracker.cell(HEADER_ROW, layout.status_date_cols[0]).value
    assert "04_Status_Pipeline" in str(date0)
    dur0 = tracker.cell(HEADER_ROW, layout.duration_cols[0]).value
    assert "Days:" in str(dur0) or "04_Status_Pipeline" in str(dur0)

    # Named ranges
    names = set(wb.defined_names.keys())
    for required in (
        "Interventions",
        "Donors",
        "Projects",
        "Regions",
        "Statuses",
        "All_Provinces",
        "All_Districts",
        "Prov_West_Herat",
        "Dist_Badghis",
        "Dist_Kunar",
    ):
        assert required in names, f"missing named range {required}"

    # Data validations on tracker
    dv_formulas = [str(dv.formula1) for dv in tracker.data_validations.dataValidation]
    joined = " | ".join(dv_formulas)
    for token in ("Projects", "Interventions", "Regions", "Donors", "Statuses", "DATE("):
        assert token in joined, f"missing validation {token} in {joined}"

    # Domain lists
    domains = wb[SHEET_DOMAINS]
    assert domains.cell(2, 1).value == "Interventions"
    assert domains.cell(3, 1).value == "Check Dam"

    pipeline = wb[SHEET_PIPELINE]
    assert pipeline.cell(3, 2).value == "Under Design"
    names = [pipeline.cell(r, 2).value for r in range(3, 16)]
    assert "Under Awarding" in names
    assert "Completed / Handover" in names
    assert "PR to be Raised" in names

    # Dashboard formulas reference the tracker
    dash = wb[SHEET_DASH]
    assert "COUNTA" in str(dash["A5"].value)
    assert "COUNTIF" in str(dash["B9"].value)

    # Spare slots exist after the named pipeline steps
    spare_rows = [r for r in range(3, 20) if pipeline.cell(r, 2).value in (None, "")]
    assert spare_rows, "expected spare pipeline slots"
    assert "(spare" in str(tracker.cell(HEADER_ROW, layout.status_date_cols[-1]).value) or "04_Status_Pipeline" in str(
        tracker.cell(HEADER_ROW, layout.status_date_cols[-1]).value
    )

    demo2 = EXAMPLE_SCHEMES[1]
    t2, total2, last2 = expected_demo_durations(demo2)
    assert last2 == "Under Technical Evaluation"
    assert total2 == 75  # 2025-08-15 minus 2025-06-01
    assert t2[0][2] == 19  # 1 Jun → 20 Jun

    print(f"OK  sheets={wb.sheetnames}")
    print(f"OK  live schemes={len(SCHEMES)}  named ranges={len(names)}  tracker DVs={len(dv_formulas)}")
    print(f"OK  file size={XLSX.stat().st_size} bytes")
    print(f"OK  DEMO-02 total={total2} last={last2}")


if __name__ == "__main__":
    main()
