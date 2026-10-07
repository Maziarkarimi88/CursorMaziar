"""Unit tests for KOBO well-visit cleaning and well identity."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from kobo_gw import (  # noqa: E402
    parse_daily_use,
    process,
    run,
    scan_radii,
    write_radius_choice,
)

FIXTURE = ROOT / "tests" / "fixtures" / "kobo_mini.csv"


def test_parse_daily_use_liters_hours_and_bare_number():
    assert parse_daily_use("500lit/day") == (500.0, None)
    assert parse_daily_use("8hr/day") == (None, 8.0)
    assert parse_daily_use("8") == (None, 8.0)
    assert parse_daily_use("340") == (340.0, None)
    assert parse_daily_use("") == (None, None)


def test_process_fixture_counts_and_flags():
    visits, wells, qa, n_empty = process(FIXTURE)
    assert n_empty == 1
    assert len(visits) == 6
    assert len(wells) == 4

    good = wells.loc[(wells["province"] == "Kapisa") & (wells["n_visits"] == 3)].iloc[0]
    assert abs(float(good["dtw_change_recall_m"]) - 3.0) < 1e-9  # 12 - 9
    assert abs(float(good["dtw_change_measured_m"]) - 1.0) < 1e-9  # 10 - 9
    assert not bool(good["exclude_from_impact"])

    flags = set(qa["flag"])
    assert "wt_now_gt_depth" in flags
    assert "diameter_outlier" in flags
    assert "hh_looks_like_phone" in flags
    assert "distance_gt_5000" in flags
    assert "unit_confusion" in flags

    deep = wells.loc[wells["province"] == "Kandahar"].iloc[0]
    assert bool(deep["exclude_from_impact"])


def test_run_writes_tables(tmp_path: Path | None = None):
    if tmp_path is None:
        import tempfile

        tmp = Path(tempfile.mkdtemp())
    else:
        tmp = tmp_path
    tables = tmp / "tables"
    figs = tmp / "figs"
    result = run(FIXTURE, tables, figs, plots=False)
    assert (tables / "wells_unique.csv").exists()
    assert (tables / "visits.csv").exists()
    assert (tables / "qa_flags.csv").exists()
    assert (tables / "CLUSTER_COMPARE.md").exists()
    compare = (tables / "CLUSTER_COMPARE.md").read_text(encoding="utf-8")
    assert "1,041" in compare and "2,339" in compare
    assert result["summary"]["n_wells"] == 4
    assert result["summary"]["n_visits"] == 6
    # owner/phone must not leak into committed-style outputs
    text = (tables / "wells_unique.csv").read_text(encoding="utf-8")
    assert "Good Owner" not in text
    assert "0701111111" not in text


def test_scan_radii_fixture_and_radius_choice(tmp_path: Path | None = None):
    rows = scan_radii(FIXTURE, radii=(5.0, 15.0))
    by = {rec["r"]: rec for rec in rows}
    assert by[5.0]["wells"] >= by[15.0]["wells"]
    if tmp_path is None:
        import tempfile

        tmp = Path(tempfile.mkdtemp())
    else:
        tmp = tmp_path
    visits, _wells, _qa, _n = process(FIXTURE)
    out = tmp / "RADIUS_CHOICE.md"
    write_radius_choice(visits, rows, out)
    text = out.read_text(encoding="utf-8")
    assert "15 m" in text
    assert "5 m" in text
    assert "Good Owner" not in text


if __name__ == "__main__":
    test_parse_daily_use_liters_hours_and_bare_number()
    print("ok test_parse_daily_use_liters_hours_and_bare_number")
    test_process_fixture_counts_and_flags()
    print("ok test_process_fixture_counts_and_flags")
    test_run_writes_tables()
    print("ok test_run_writes_tables")
    test_scan_radii_fixture_and_radius_choice()
    print("ok test_scan_radii_fixture_and_radius_choice")
