"""Unit tests for KOBO well-visit cleaning and well identity."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from kobo_gw import (  # noqa: E402
    build_wells,
    parse_daily_use,
    process,
    run,
    well_id_hash,
)

FIXTURE = ROOT / "tests" / "fixtures" / "kobo_mini.csv"


def test_well_id_ignores_case_and_spaces():
    a = well_id_hash("Kapisa", "Test Village", "Good Owner", "0701111111")
    b = well_id_hash("kapisa", " test  village ", "good owner", "070-111-1111")
    assert a == b
    assert len(a) == 12


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

    good_id = well_id_hash("Kapisa", "Test Village", "Good Owner", "0701111111")
    good = wells.set_index("well_id").loc[good_id]
    assert int(good["n_visits"]) == 3
    assert abs(float(good["dtw_change_recall_m"]) - 3.0) < 1e-9  # 12 - 9
    assert abs(float(good["dtw_change_measured_m"]) - 1.0) < 1e-9  # 10 - 9
    assert good["exclude_from_impact"] is False or good["exclude_from_impact"] == False

    flags = set(qa["flag"])
    assert "wt_now_gt_depth" in flags
    assert "diameter_outlier" in flags
    assert "hh_looks_like_phone" in flags
    assert "distance_gt_5000" in flags
    assert "unit_confusion" in flags

    deep_id = well_id_hash("Kandahar", "Deep Village", "Deep Owner", "0702222222")
    assert bool(wells.set_index("well_id").loc[deep_id, "exclude_from_impact"])


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
    assert result["summary"]["n_wells"] == 4
    assert result["summary"]["n_visits"] == 6
    # owner/phone must not leak into committed-style outputs
    text = (tables / "wells_unique.csv").read_text(encoding="utf-8")
    assert "Good Owner" not in text
    assert "0701111111" not in text


if __name__ == "__main__":
    test_well_id_ignores_case_and_spaces()
    print("ok test_well_id_ignores_case_and_spaces")
    test_parse_daily_use_liters_hours_and_bare_number()
    print("ok test_parse_daily_use_liters_hours_and_bare_number")
    test_process_fixture_counts_and_flags()
    print("ok test_process_fixture_counts_and_flags")
    test_run_writes_tables()
    print("ok test_run_writes_tables")
