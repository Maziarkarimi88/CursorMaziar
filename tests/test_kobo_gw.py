"""Unit tests for KOBO well-visit cleaning and well identity."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pandas as pd  # noqa: E402

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
    assert (tables / "kobo_monitoring_clusters.csv").exists()
    assert (tables / "visits_clusters.csv").exists()
    assert (figs / "cluster_monitorings.png").exists()
    assert (tables / "wells_clusters.csv").exists()
    assert (tables / "owner_split_sites.csv").exists()
    assert (tables / "qa_flags.csv").exists()
    assert (tables / "CLUSTER_COMPARE.md").exists()
    assert (tables / "dbscan_chains_review.csv").exists()
    assert (tables / "dbscan_chain_visits.csv").exists()
    compare = (tables / "CLUSTER_COMPARE.md").read_text(encoding="utf-8")
    assert "1,041" in compare and "2,339" in compare
    assert result["summary"]["n_wells"] == 4
    assert result["summary"]["n_visits"] == 6
    wells = (tables / "wells_unique.csv").read_text(encoding="utf-8")
    assert "hydro_class" in wells
    visits = (tables / "visits.csv").read_text(encoding="utf-8")
    assert "split_review" in visits and "dbscan_id" in visits
    assert "cluster_id" in visits
    final = pd.read_csv(tables / "kobo_monitoring_clusters.csv", dtype={"cluster_id": str})
    assert len(final) == 6
    assert "n_monitorings" in final.columns
    assert "gps_group" in final.columns
    assert "1. Province" in final.columns
    assert "Y" in final.columns and "X" in final.columns
    assert "8. Owner/caretaker name" in final.columns
    assert "9. Phone number" in final.columns
    assert "6. Enumerator name" in final.columns
    assert final["cluster_id"].min() == "01"
    assert set(final["cluster_id"].str.len()) == {2}
    kapisa = final.loc[final["1. Province"] == "Kapisa"]
    assert kapisa["cluster_id"].nunique() == 1
    assert int(kapisa["n_monitorings"].iloc[0]) == 3
    clusters = pd.read_csv(tables / "wells_clusters.csv")
    assert "cluster_id" in clusters.columns and "site_id" in clusters.columns
    assert len(clusters) == 4
    # owner/phone must not leak into committed-style outputs
    text = (
        wells
        + visits
        + (tables / "dbscan_chains_review.csv").read_text(encoding="utf-8")
        + (tables / "visits_clusters.csv").read_text(encoding="utf-8")
        + (tables / "wells_clusters.csv").read_text(encoding="utf-8")
        + (tables / "owner_split_sites.csv").read_text(encoding="utf-8")
        + (tables / "same_owner_splits.csv").read_text(encoding="utf-8")
    )
    assert "Good Owner" not in text
    assert "0701111111" not in text
    assert "owner_n" not in (tables / "same_owner_splits.csv").read_text(encoding="utf-8").splitlines()[0]


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
