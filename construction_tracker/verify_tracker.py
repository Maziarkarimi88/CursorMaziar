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
    SHEET_DATES,
    SHEET_DOMAINS,
    SHEET_EXAMPLE,
    SHEET_GEO,
    SHEET_HOWTO,
    SHEET_LOOKUPS,
    SHEET_CONTRACTORS,
    SHEET_PACKAGES,
    SHEET_PKG_STATUS,
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
        SHEET_PACKAGES,
        SHEET_CONTRACTORS,
        SHEET_PKG_STATUS,
        SHEET_DATES,
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
    assert SHEET_PIPELINE in str(date0)
    dur0 = tracker.cell(HEADER_ROW, layout.duration_cols[0]).value
    assert "Days:" in str(dur0) or SHEET_PIPELINE in str(dur0)

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
        "AwardGroups",
        "Families",
        "Contractors",
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
    assert domains.cell(3, 1).value == "Irrigation Canal"
    family_col = next(c for c in range(1, 12) if domains.cell(2, c).value == "Families")
    assert domains.cell(3, family_col).value == "Irrigation Scheme"
    award_col = next(c for c in range(1, 12) if domains.cell(2, c).value == "AwardGroups")
    assert [domains.cell(r, award_col).value for r in (3, 4)] == ["Awarded", "Not awarded"]

    # Package grouping: Package #8-AF2 IS = 2 rows; Package #10-AF2 IS = 4 rows
    from collections import defaultdict

    pkg_rows = defaultdict(list)
    majors = set()
    groups = set()
    for i, scheme in enumerate(SCHEMES):
        row = DATA_START + i
        pid = tracker.cell(row, layout.idx["package_id"]).value
        assert pid == scheme["package_id"], (pid, scheme["package_id"])
        assert tracker.cell(row, layout.idx["award_group"]).value in ("Awarded", "Not awarded")
        assert tracker.cell(row, layout.idx["award_group"]).value != "Remaining"
        majors.add(tracker.cell(row, layout.idx["intervention_major"]).value)
        groups.add(tracker.cell(row, layout.idx["award_group"]).value)
        pkg_rows[pid].append(row)
    assert majors == set(s["intervention_major"] for s in SCHEMES)
    assert groups == {"Awarded", "Not awarded"}
    from collections import Counter

    major_counts = Counter(s["intervention_major"] for s in SCHEMES)
    subtype_counts = Counter(s["intervention_type"] for s in SCHEMES)
    assert major_counts["Laser Land Leveler (LLL)"] == 50
    assert subtype_counts["LLL unit"] == 50
    assert major_counts["Drip Irrigation"] == 100
    assert subtype_counts["Drip Irrigation Plot"] == 100
    assert major_counts["Agroforestry saplings / seeds"] == 39
    assert "Remaining" not in {s["award_group"] for s in SCHEMES}
    pkg8 = [s for s in SCHEMES if s.get("package_name", "").startswith("Package #8-AF2 IS")]
    pkg10 = [s for s in SCHEMES if s.get("package_name", "").startswith("Package #10-AF2 IS")]
    assert len(pkg8) == 2, [s["scheme_name"] for s in pkg8]
    assert len({s["package_id"] for s in pkg8}) == 1
    assert {s["scheme_name"] for s in pkg8} == {
        "Khas Kunar Lower Canal irrigation Scheme",
        "Bahrabad Canal irrigation Scheme",
    }
    assert len(pkg10) == 4, [s["scheme_name"] for s in pkg10]
    assert len({s["package_id"] for s in pkg10}) == 1
    assert tracker.row_dimensions[pkg_rows[pkg8[0]["package_id"]][1]].outlineLevel == 1
    assert tracker.row_dimensions[pkg_rows[pkg10[0]["package_id"]][1]].outlineLevel == 1

    packages = wb[SHEET_PACKAGES]
    pkg_ids = [packages.cell(r, 1).value for r in range(4, packages.max_row + 1) if packages.cell(r, 1).value]
    assert pkg8[0]["package_id"] in pkg_ids
    assert pkg10[0]["package_id"] in pkg_ids
    assert packages.cell(3, 5).value == "Package status"
    assert packages.cell(3, 14).value == "Contractor Name"
    zscc_pkg_rows = [
        r
        for r in range(4, packages.max_row + 1)
        if packages.cell(r, 14).value and "ZSCC" in str(packages.cell(r, 14).value)
    ]
    assert len(zscc_pkg_rows) == 1, zscc_pkg_rows
    assert packages.cell(zscc_pkg_rows[0], 1).value == pkg10[0]["package_id"]
    assert "057/2025" in str(packages.cell(zscc_pkg_rows[0], 15).value)
    from generate_tracker import package_current_status, collect_packages

    pkg10_members = [s for s in SCHEMES if s["package_id"] == pkg10[0]["package_id"]]
    expected_pkg10, mixed10, _ = package_current_status(pkg10_members)
    assert packages.cell(zscc_pkg_rows[0], 5).value == expected_pkg10
    assert packages.cell(zscc_pkg_rows[0], 6).value == ("Yes" if mixed10 else "No")

    pkg_status = wb[SHEET_PKG_STATUS]
    assert "Package status" in str(pkg_status.cell(1, 1).value)
    assert pkg_status.cell(8, 1).value == "Major intervention"
    assert pkg_status.cell(9, 1).value == "Irrigation Scheme"
    assert pkg_status.cell(10, 1).value == "Watershed Management"
    assert "COUNTIFS" in str(pkg_status.cell(9, 3).value)
    assert "Awarded" in str(pkg_status.cell(9, 3).value)
    pkgs = collect_packages()
    is_awarded = sum(1 for _p, first, _m in pkgs if first.get("intervention_major") == "Irrigation Scheme" and first.get("award_group") == "Awarded")
    is_not = sum(1 for _p, first, _m in pkgs if first.get("intervention_major") == "Irrigation Scheme" and first.get("award_group") == "Not awarded")
    wsm_awarded = sum(1 for _p, first, _m in pkgs if first.get("intervention_major") == "Watershed Management" and first.get("award_group") == "Awarded")
    wsm_not = sum(1 for _p, first, _m in pkgs if first.get("intervention_major") == "Watershed Management" and first.get("award_group") == "Not awarded")
    assert is_awarded == 18, is_awarded
    assert is_awarded + is_not == 46, (is_awarded, is_not)
    assert wsm_awarded == 23, wsm_awarded
    status_title_row = next(
        r for r in range(1, 30) if str(pkg_status.cell(r, 1).value or "").startswith("Packages by pipeline status")
    )
    status_header = status_title_row + 1
    status_first = status_title_row + 2
    status_labels = [pkg_status.cell(r, 1).value for r in range(status_first, status_first + 14)]
    assert "Under Awarding" in status_labels
    assert "Under Review of WRI" in status_labels
    awarding_row = status_first + status_labels.index("Under Awarding")
    assert "COUNTIF" in str(pkg_status.cell(awarding_row, 2).value)
    n_packages = len(pkgs)
    awarding_schemes = sum(1 for s in SCHEMES if s.get("reported_status") == "Under Awarding")
    awarding_pkgs = sum(1 for _pid, _first, members in pkgs if package_current_status(members)[0] == "Under Awarding")
    assert awarding_pkgs < awarding_schemes
    assert awarding_pkgs >= 2
    assert pkg_status.cell(status_header, 7).value == "Irrigation Scheme"
    assert "Share of this status" in str(pkg_status.cell(status_header, 8).value)
    awarded_row = status_first + status_labels.index("Awarded")
    assert "COUNTIFS" in str(pkg_status.cell(awarded_row, 7).value)
    assert f"$B{awarded_row}" in str(pkg_status.cell(awarded_row, 8).value)

    contractors = wb[SHEET_CONTRACTORS]
    assert "Contracts by contractor" in str(contractors.cell(1, 1).value)
    zscc_rows = [
        r
        for r in range(4, contractors.max_row + 1)
        if contractors.cell(r, 1).value and "ZSCC" in str(contractors.cell(r, 1).value)
    ]
    assert len(zscc_rows) == 1, zscc_rows
    awarded_contractors = {
        (s.get("contractor_name") or "").strip()
        for s in SCHEMES
        if s.get("award_group") == "Awarded" and (s.get("contractor_name") or "").strip()
    }
    listed = [contractors.cell(r, 1).value for r in range(4, contractors.max_row + 1) if contractors.cell(r, 1).value]
    assert set(listed) == awarded_contractors
    assert contractors.cell(zscc_rows[0], 2).value == 1
    assert pkg10[0]["package_id"] in str(contractors.cell(zscc_rows[0], 5).value)
    assert "057/2025" in str(contractors.cell(zscc_rows[0], 6).value)
    dates = wb[SHEET_DATES]
    assert "Date conditions" in str(dates["B1"].value)
    health_f = str(tracker.cell(DATA_START, layout.idx["schedule_health"]).value)
    assert '="Not awarded"' in health_f
    assert "Remaining" not in health_f
    assert "Families" in joined

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
    assert "(spare" in str(tracker.cell(HEADER_ROW, layout.status_date_cols[-1]).value) or SHEET_PIPELINE in str(
        tracker.cell(HEADER_ROW, layout.status_date_cols[-1]).value
    )

    demo2 = EXAMPLE_SCHEMES[1]
    t2, total2, last2 = expected_demo_durations(demo2)
    assert last2 == "Under Technical Evaluation"
    assert total2 == 75  # 2025-08-15 minus 2025-06-01
    assert t2[0][2] == 19  # 1 Jun → 20 Jun

    print(f"OK  sheets={wb.sheetnames}")
    print(f"OK  live schemes={len(SCHEMES)}  named ranges={len(names)}  tracker DVs={len(dv_formulas)}")
    assert tracker.freeze_panes == f"A{DATA_START}", tracker.freeze_panes
    print(f"OK  file size={XLSX.stat().st_size} bytes")
    print(f"OK  freeze={tracker.freeze_panes}")
    print(f"OK  DEMO-02 total={total2} last={last2}")


if __name__ == "__main__":
    main()
