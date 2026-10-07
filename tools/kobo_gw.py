"""Clean FAO KOBO well visits and build inventory, QA, and impact tables.

Each KOBO row is one visit, not one well. Well identity is province + village
+ owner + phone (hashed in outputs). Depth-to-water (DTW): larger = deeper.

  python3 tools/kobo_gw.py --csv data/kobo/groundwater_monitoring.csv
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = ROOT / "data" / "kobo" / "groundwater_monitoring.csv"
OUT_TABLES = ROOT / "examples" / "kobo_gw"
OUT_FIGS = ROOT / "figures" / "kobo_gw"

COLMAP = {
    "region": "region",
    "province": "1. Province",
    "district": "2. District",
    "village": "3. Village Name",
    "lat": "Y",
    "lon": "X",
    "alt": "Z",
    "gps_prec": "GPS_Precision",
    "collect_date": "5. Date of data collection",
    "enumerator": "6. Enumerator name",
    "source_type": "7. Water source type (well/Kariz)",
    "owner": "8. Owner/caretaker name",
    "phone": "9. Phone number",
    "well_type": "10. Well Type",
    "other_well": "Other well",
    "year_dug": "11. Year of digging",
    "total_depth": "12. Total depth of well (m)",
    "diam_m": "13. Diameter of well (m)",
    "wt_digging": "14. Water table at time of digging (m)",
    "wt_before": "15. Typical water level before intervention (m)",
    "scarcity_months": "16. Months of water scarcity (before)",
    "main_use": "17. Main use of water",
    "intervention": "17. Type of intervention",
    "project": "18. Project code",
    "subproject": "19. Sub-project name/code",
    "interv_date": "20. Date of intervention completion (Month/Year)",
    "distance_m": "21. Distance from water source to intervention (m)",
    "rel_loc": "22. Relative location of intervention",
    "meas_date": "23. Date of water level measurement",
    "wt_now": "24. Current water table depth (m)",
    "method": "25. Method of measurement",
    "ever_dry": "26. Was the well/Kariz ever dry? (before)",
    "daily_use": "27. Average daily water use (lit/day or hr/day)",
    "hh": "28. Number of households using the well",
    "jerib": "29. Irrigated area in Jrib (if applicable)",
    "change": "30. Change in water level after intervention",
    "est_rise": "31. Estimated water level rise (m)",
    "perception": "32. Community perception of impact",
    "condition": "33. Condition of intervention structure",
    "remarks_add": "Additional remarks/observations (if any):",
    "remarks": "Remarks",
    "submission_id": "_id",
    "submit_time": "_submission_time",
}

NUM_COLS = [
    "lat",
    "lon",
    "alt",
    "gps_prec",
    "year_dug",
    "total_depth",
    "diam_m",
    "wt_digging",
    "wt_before",
    "distance_m",
    "wt_now",
    "est_rise",
    "jerib",
    "hh",
]
DATE_COLS = ["collect_date", "meas_date", "interv_date"]
AF_LAT = (29.0, 39.0)
AF_LON = (60.0, 75.5)
DISTANCE_BINS = [0, 200, 500, 1000, 2000, np.inf]
DISTANCE_LABELS = ["0-200", "200-500", "500-1000", "1000-2000", ">2000"]
DTW_SAME_M = 0.1


def _norm_text(value) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("\n", " ").strip().lower()
    return re.sub(r"\s+", " ", text)


def _digits(value) -> str:
    return re.sub(r"\D", "", str(value)) if not pd.isna(value) else ""


def well_id_hash(province, village, owner, phone) -> str:
    key = "|".join(
        [_norm_text(province), _norm_text(village), _norm_text(owner), _digits(phone)]
    )
    return hashlib.sha1(key.encode("utf-8")).hexdigest()[:12]


def read_kobo_csv(path: Path) -> pd.DataFrame:
    raw = Path(path).read_bytes()
    last_err: Exception | None = None
    for enc in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            return pd.read_csv(path, low_memory=False, encoding=enc)
        except UnicodeDecodeError as err:
            last_err = err
    # last resort: ignore undecodable bytes
    if last_err is not None:
        return pd.read_csv(path, low_memory=False, encoding="cp1252", encoding_errors="replace")
    raise last_err  # pragma: no cover


def rename_kobo_columns(df: pd.DataFrame) -> pd.DataFrame:
    present = {new: old for new, old in COLMAP.items() if old in df.columns}
    missing = [new for new, old in COLMAP.items() if old not in df.columns]
    if missing:
        raise ValueError(f"KOBO export missing expected columns: {missing}")
    out = df.loc[:, list(present.values())].copy()
    out.columns = list(present.keys())
    return out


def coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in NUM_COLS:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    for col in DATE_COLS:
        if col in out.columns:
            out[col] = pd.to_datetime(out[col], errors="coerce")
    for col in (
        "province",
        "district",
        "village",
        "enumerator",
        "source_type",
        "well_type",
        "main_use",
        "intervention",
        "project",
        "rel_loc",
        "method",
        "change",
        "perception",
        "condition",
        "ever_dry",
        "owner",
        "phone",
    ):
        if col in out.columns:
            out[col] = out[col].apply(lambda v: np.nan if _norm_text(v) in {"", "nan"} else v)
            if col == "enumerator":
                out[col] = out[col].map(lambda v: re.sub(r"\s+", " ", str(v).strip()) if pd.notna(v) else v)
    return out


def drop_empty_rows(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    empty = df["province"].isna() | df["lat"].isna() | df["lon"].isna()
    return df.loc[~empty].copy(), int(empty.sum())


def attach_well_id(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["well_id"] = [
        well_id_hash(p, v, o, ph)
        for p, v, o, ph in zip(out["province"], out["village"], out["owner"], out["phone"])
    ]
    return out


def parse_daily_use(value) -> tuple[float | None, float | None]:
    """Return (litres_per_day, hours_per_day); either may be None."""
    if pd.isna(value):
        return None, None
    text = str(value).strip().lower().replace(",", "")
    if text in {"", "nan", "no", "none", "."}:
        return None, None
    hours = None
    liters = None
    hr = re.search(r"(\d+(?:\.\d+)?)\s*(h|hr|hrs|hour|hours)\b", text)
    if hr:
        hours = float(hr.group(1))
    lit = re.search(r"(\d+(?:\.\d+)?)\s*(l|lt|lit|liter|litre|liters|litres)\b", text)
    if lit:
        liters = float(lit.group(1))
    if hours is None and liters is None:
        nums = re.findall(r"\d+(?:\.\d+)?", text)
        if len(nums) == 1:
            n = float(nums[0])
            if n <= 24:
                hours = n
            else:
                liters = n
    return liters, hours


def distance_bin(distance_m: pd.Series) -> pd.Series:
    return pd.cut(distance_m, bins=DISTANCE_BINS, labels=DISTANCE_LABELS, right=True, include_lowest=True)


def dtw_change_class(delta: pd.Series) -> pd.Series:
    return pd.cut(
        delta,
        bins=[-np.inf, -DTW_SAME_M, DTW_SAME_M, np.inf],
        labels=["deeper_now", "same_pm0.1", "shallower_now"],
    )


def flag_visits(df: pd.DataFrame) -> pd.DataFrame:
    """Add boolean QA columns on the visit table."""
    out = df.copy()
    phone_digits = out["phone"].map(_digits)
    hh_digits = out["hh"].map(_digits)
    out["flag_wt_now_gt_depth"] = out["wt_now"].notna() & out["total_depth"].notna() & (
        out["wt_now"] > out["total_depth"]
    )
    out["flag_wt_now_zero"] = out["wt_now"] == 0
    out["flag_wt_now_gt_100"] = out["wt_now"] > 100
    out["flag_diameter_outlier"] = out["diam_m"] >= 100
    out["flag_diameter_suspect"] = (out["diam_m"] > 5) & (out["diam_m"] < 100)
    out["flag_hh_looks_like_phone"] = (hh_digits.str.len() >= 8) & (hh_digits == phone_digits)
    out["flag_hh_implausible"] = out["hh"] > 200
    out["flag_unit_confusion"] = (out["wt_before"] < 1) & (out["total_depth"] > 5)
    out["flag_distance_gt_5000"] = out["distance_m"] > 5000
    out["flag_est_rise_gt_20"] = out["est_rise"] > 20
    out["flag_meas_before_interv"] = (
        out["meas_date"].notna() & out["interv_date"].notna() & (out["meas_date"] < out["interv_date"])
    )
    out["flag_gps_outside_af"] = (
        out["lat"].notna()
        & out["lon"].notna()
        & (
            (out["lat"] < AF_LAT[0])
            | (out["lat"] > AF_LAT[1])
            | (out["lon"] < AF_LON[0])
            | (out["lon"] > AF_LON[1])
        )
    )
    out["flag_diam_missing"] = out["diam_m"].isna()
    return out


FLAG_COLS = [
    "flag_wt_now_gt_depth",
    "flag_wt_now_zero",
    "flag_wt_now_gt_100",
    "flag_diameter_outlier",
    "flag_diameter_suspect",
    "flag_hh_looks_like_phone",
    "flag_hh_implausible",
    "flag_unit_confusion",
    "flag_distance_gt_5000",
    "flag_est_rise_gt_20",
    "flag_meas_before_interv",
    "flag_gps_outside_af",
]

IMPACT_EXCLUDE_FLAGS = [
    "flag_wt_now_gt_depth",
    "flag_unit_confusion",
    "flag_distance_gt_5000",
    "flag_wt_now_gt_100",
]


def qa_flags_long(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for flag in FLAG_COLS:
        hit = df.loc[df[flag], ["well_id", "submission_id", "province", "village", "meas_date"]].copy()
        if hit.empty:
            continue
        hit["flag"] = flag.replace("flag_", "")
        rows.append(hit)
    if not rows:
        return pd.DataFrame(columns=["well_id", "submission_id", "province", "village", "meas_date", "flag"])
    return pd.concat(rows, ignore_index=True)


def build_visits(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    parsed = out["daily_use"].map(parse_daily_use)
    out["use_lpd"] = parsed.map(lambda t: t[0])
    out["use_hpd"] = parsed.map(lambda t: t[1])
    out["distance_bin"] = distance_bin(out["distance_m"])
    out["dtw_change_recall_m"] = out["wt_before"] - out["wt_now"]
    out["hh_clean"] = out["hh"]
    out.loc[out["flag_hh_looks_like_phone"] | out["flag_hh_implausible"], "hh_clean"] = np.nan
    out["diam_m_clean"] = out["diam_m"]
    out.loc[out["flag_diameter_outlier"] | out["flag_diameter_suspect"], "diam_m_clean"] = np.nan
    return out


def _first_last(g: pd.DataFrame) -> pd.Series:
    g = g.sort_values(["meas_date", "collect_date"], kind="mergesort")
    first = g.iloc[0]
    last = g.iloc[-1]
    n_flags = int(g[FLAG_COLS].any(axis=1).sum())
    exclude = bool(last[IMPACT_EXCLUDE_FLAGS].any()) or bool(g["flag_unit_confusion"].any())
    return pd.Series(
        {
            "region": last["region"],
            "province": last["province"],
            "district": last["district"],
            "village": last["village"],
            "lat": g["lat"].median(),
            "lon": g["lon"].median(),
            "alt": g["alt"].median(),
            "gps_prec_m": g["gps_prec"].median(),
            "source_type": last["source_type"],
            "well_type": last["well_type"],
            "year_dug": last["year_dug"],
            "total_depth_m": last["total_depth"],
            "diam_m": last["diam_m_clean"],
            "wt_digging_m": last["wt_digging"],
            "wt_before_m": last["wt_before"],
            "scarcity_months": last["scarcity_months"],
            "main_use": last["main_use"],
            "intervention": last["intervention"],
            "project": last["project"],
            "subproject": last["subproject"],
            "interv_date": last["interv_date"],
            "distance_m": last["distance_m"],
            "distance_bin": last["distance_bin"],
            "rel_loc": last["rel_loc"],
            "n_visits": int(len(g)),
            "n_unique_dates": int(g["meas_date"].nunique(dropna=True)),
            "first_meas_date": first["meas_date"],
            "last_meas_date": last["meas_date"],
            "span_days": (
                (last["meas_date"] - first["meas_date"]).days
                if pd.notna(last["meas_date"]) and pd.notna(first["meas_date"])
                else np.nan
            ),
            "first_wt_now_m": first["wt_now"],
            "last_wt_now_m": last["wt_now"],
            "dtw_change_recall_m": last["wt_before"] - last["wt_now"]
            if pd.notna(last["wt_before"]) and pd.notna(last["wt_now"])
            else np.nan,
            "dtw_change_measured_m": first["wt_now"] - last["wt_now"]
            if pd.notna(first["wt_now"]) and pd.notna(last["wt_now"])
            else np.nan,
            "method_last": last["method"],
            "ever_dry": last["ever_dry"],
            "hh": last["hh_clean"],
            "jerib": last["jerib"],
            "use_lpd": last["use_lpd"],
            "use_hpd": last["use_hpd"],
            "change_reported": last["change"],
            "est_rise_m": last["est_rise"],
            "perception": last["perception"],
            "condition": last["condition"],
            "n_flagged_visits": n_flags,
            "exclude_from_impact": exclude,
        }
    )


def build_wells(visits: pd.DataFrame) -> pd.DataFrame:
    wells = visits.groupby("well_id", sort=False).apply(_first_last, include_groups=False)
    wells = wells.reset_index()
    wells["measured_class"] = dtw_change_class(wells["dtw_change_recall_m"])
    return wells


def perception_crosstab(wells: pd.DataFrame) -> pd.DataFrame:
    use = wells.loc[~wells["exclude_from_impact"]].copy()
    tab = pd.crosstab(
        use["change_reported"].fillna("(blank)"),
        use["measured_class"].astype("object").fillna("(no DTW)"),
        dropna=False,
        margins=True,
    )
    return tab.reset_index()


def perception_vs_perception(wells: pd.DataFrame) -> pd.DataFrame:
    use = wells.loc[~wells["exclude_from_impact"]].copy()
    tab = pd.crosstab(
        use["change_reported"].fillna("(blank)"),
        use["perception"].fillna("(blank)"),
        dropna=False,
        margins=True,
    )
    return tab.reset_index()


def _safe_mkdir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_tables(visits: pd.DataFrame, wells: pd.DataFrame, qa: pd.DataFrame, out_dir: Path) -> dict[str, Path]:
    _safe_mkdir(out_dir)
    visit_cols = [
        "well_id",
        "submission_id",
        "province",
        "district",
        "village",
        "meas_date",
        "collect_date",
        "wt_now",
        "wt_before",
        "dtw_change_recall_m",
        "method",
        "lat",
        "lon",
        "intervention",
        "rel_loc",
        "distance_m",
        "distance_bin",
        "project",
    ]
    well_path = out_dir / "wells_unique.csv"
    visit_path = out_dir / "visits.csv"
    qa_path = out_dir / "qa_flags.csv"
    perc_path = out_dir / "perception_vs_measured.csv"
    perc2_path = out_dir / "perception_vs_reported_change.csv"
    visits.loc[:, visit_cols].sort_values(["province", "well_id", "meas_date"]).to_csv(visit_path, index=False)
    wells.sort_values(["province", "village", "well_id"]).to_csv(well_path, index=False)
    qa.sort_values(["flag", "province", "well_id"]).to_csv(qa_path, index=False)
    perception_crosstab(wells).to_csv(perc_path, index=False)
    perception_vs_perception(wells).to_csv(perc2_path, index=False)
    return {
        "wells_unique": well_path,
        "visits": visit_path,
        "qa_flags": qa_path,
        "perception_vs_measured": perc_path,
        "perception_vs_reported_change": perc2_path,
    }


def summarize(visits: pd.DataFrame, wells: pd.DataFrame, qa: pd.DataFrame, n_empty: int) -> dict:
    usable = wells.loc[~wells["exclude_from_impact"]]
    long8 = wells.loc[wells["n_unique_dates"] >= 8]
    return {
        "n_raw_empty_dropped": n_empty,
        "n_visits": int(len(visits)),
        "n_wells": int(len(wells)),
        "n_wells_impact": int(len(usable)),
        "n_wells_excluded_impact": int(wells["exclude_from_impact"].sum()),
        "n_provinces": int(wells["province"].nunique()),
        "n_districts": int(wells["district"].nunique()),
        "n_villages": int(wells["village"].nunique()),
        "meas_date_min": str(visits["meas_date"].min()),
        "meas_date_max": str(visits["meas_date"].max()),
        "visits_1": int((wells["n_visits"] == 1).sum()),
        "visits_2plus": int((wells["n_visits"] >= 2).sum()),
        "visits_4plus": int((wells["n_visits"] >= 4).sum()),
        "visits_8plus_dates": int((wells["n_unique_dates"] >= 8).sum()),
        "visits_12plus_dates": int((wells["n_unique_dates"] >= 12).sum()),
        "source_type": wells["source_type"].value_counts(dropna=False).to_dict(),
        "well_type": wells["well_type"].value_counts(dropna=False).to_dict(),
        "intervention": wells["intervention"].value_counts(dropna=False).to_dict(),
        "rel_loc": wells["rel_loc"].value_counts(dropna=False).to_dict(),
        "qa_flag_counts": qa["flag"].value_counts().to_dict() if len(qa) else {},
        "dtw_change_recall_median_m": _finite_median(usable["dtw_change_recall_m"]),
        "dtw_change_measured_median_m_4plus": _finite_median(
            wells.loc[(wells["n_visits"] >= 4) & ~wells["exclude_from_impact"], "dtw_change_measured_m"]
        ),
        "by_intervention_median_recall_m": _group_median(usable, "intervention", "dtw_change_recall_m"),
        "by_distance_median_recall_m": _group_median(usable, "distance_bin", "dtw_change_recall_m"),
        "by_rel_loc_median_recall_m": _group_median(usable, "rel_loc", "dtw_change_recall_m"),
        "wells_by_province": wells["province"].value_counts().to_dict(),
        "long_series_wells": int(len(long8)),
        "check_dam_wells_by_province": wells.loc[wells["intervention"] == "Check dam", "province"]
        .value_counts()
        .to_dict(),
    }


def _finite_median(s: pd.Series) -> float | None:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if s.empty:
        return None
    return float(s.median())


def _group_median(df: pd.DataFrame, by: str, col: str) -> dict:
    out = {}
    for key, part in df.groupby(by, dropna=False, observed=False):
        out[str(key)] = _finite_median(part[col])
    return out


def write_summary_md(summary: dict, wells: pd.DataFrame, out_path: Path) -> None:
    usable = wells.loc[~wells["exclude_from_impact"]]
    lines = [
        "# KOBO groundwater monitoring — analysis summary",
        "",
        "DTW change = typical water level before − latest measured depth. "
        "**Positive = shallower now (water rose).** Wells with unit-confusion, "
        "DTW deeper than well depth, DTW > 100 m, or distance > 5 km are excluded "
        "from impact medians.",
        "",
        "## Counts",
        "",
        f"- Visits kept: **{summary['n_visits']}** (dropped {summary['n_raw_empty_dropped']} empty rows)",
        f"- Unique wells: **{summary['n_wells']}** in {summary['n_provinces']} provinces, "
        f"{summary['n_districts']} districts, {summary['n_villages']} villages",
        f"- Wells used for impact tables: **{summary['n_wells_impact']}** "
        f"({summary['n_wells_excluded_impact']} excluded by QA)",
        f"- Measurement dates: {summary['meas_date_min'][:10]} to {summary['meas_date_max'][:10]}",
        f"- Repeat visits: {summary['visits_1']} wells with 1 visit; "
        f"{summary['visits_2plus']} with 2+; {summary['visits_4plus']} with 4+; "
        f"{summary['visits_8plus_dates']} with ≥8 unique dates",
        "",
        "## Median recalled DTW change (m)",
        "",
        f"- All usable wells: **{summary['dtw_change_recall_median_m']}**",
        f"- First-to-last measured DTW, wells with ≥4 visits: "
        f"**{summary['dtw_change_measured_median_m_4plus']}**",
        "",
        "By intervention:",
        "",
    ]
    for k, v in summary["by_intervention_median_recall_m"].items():
        lines.append(f"- {k}: {v}")
    lines += ["", "By distance (m):", ""]
    for k, v in summary["by_distance_median_recall_m"].items():
        lines.append(f"- {k}: {v}")
    lines += ["", "By relative location:", ""]
    for k, v in summary["by_rel_loc_median_recall_m"].items():
        lines.append(f"- {k}: {v}")
    lines += ["", "## QA flag counts (visit-level)", ""]
    for k, v in summary["qa_flag_counts"].items():
        lines.append(f"- {k}: {v}")
    lines += ["", "## Usable wells by province (median recalled DTW change)", "",
              "| Province | Wells | Median change (m) |",
              "|---|---:|---:|"]
    prov = (
        usable.groupby("province")["dtw_change_recall_m"]
        .agg(["count", "median"])
        .sort_values("count", ascending=False)
    )
    for name, row in prov.iterrows():
        med = "" if pd.isna(row["median"]) else f"{row['median']:.2f}"
        lines.append(f"| {name} | {int(row['count'])} | {med} |")
    lines += [
        "",
        "## How to read this",
        "",
        "- Recalled before vs now is a **snapshot + memory**, not a designed before/after.",
        "- First-to-last measured DTW on short series is mostly **season**, not dam impact.",
        "- Do not run Mann–Kendall / Sen on the full file; series are at most about one year.",
        "- Check-dam wells are concentrated in Kapisa and Kunar; do not generalise that mix "
        "as a national check-dam effect.",
        "",
    ]
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _style() -> None:
    import matplotlib.pyplot as plt

    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.grid": True,
            "grid.alpha": 0.25,
            "font.size": 9,
            "axes.titlesize": 11,
            "figure.dpi": 120,
        }
    )


def plot_map(wells: pd.DataFrame, path: Path) -> None:
    import matplotlib.pyplot as plt

    _style()
    fig, ax = plt.subplots(figsize=(8.2, 7.2))
    colors = {"Check dam": "#1f4e79", "Trench": "#b86b00", "Both": "#2e7d4f"}
    for kind, color in colors.items():
        part = wells.loc[wells["intervention"] == kind]
        ax.scatter(
            part["lon"],
            part["lat"],
            s=np.clip(part["n_visits"] * 6, 10, 80),
            c=color,
            alpha=0.75,
            edgecolors="none",
            label=f"{kind} (n={len(part)})",
        )
    other = wells.loc[~wells["intervention"].isin(colors)]
    if len(other):
        ax.scatter(other["lon"], other["lat"], s=12, c="#888888", alpha=0.6, label=f"Other (n={len(other)})")
    ax.set_xlim(60.5, 75.0)
    ax.set_ylim(29.2, 38.7)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Unique wells (size = number of visits)")
    ax.legend(loc="lower left", framealpha=0.9)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def _boxplot(ax, data: dict[str, np.ndarray], ylabel: str, title: str, hline: bool = True) -> None:
    labels = list(data.keys())
    values = [data[k] for k in labels]
    ax.boxplot(values, tick_labels=labels, showfliers=False, medianprops={"color": "#1f4e79", "linewidth": 2})
    if hline:
        ax.axhline(0, color="#666666", linewidth=0.8)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=35)


def plot_box_change(wells: pd.DataFrame, by: str, path: Path, title: str) -> None:
    import matplotlib.pyplot as plt

    _style()
    use = wells.loc[~wells["exclude_from_impact"]].copy()
    use = use.dropna(subset=["dtw_change_recall_m", by])
    order = list(use[by].value_counts().index)
    data = {
        f"{k}\n(n={int((use[by] == k).sum())})": use.loc[use[by] == k, "dtw_change_recall_m"].to_numpy()
        for k in order
    }
    fig, ax = plt.subplots(figsize=(max(7.5, 0.55 * len(order) + 3), 5.2))
    _boxplot(ax, data, "Recalled DTW change (m)\npositive = water rose", title)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_perception(wells: pd.DataFrame, path: Path) -> None:
    import matplotlib.pyplot as plt

    _style()
    use = wells.loc[~wells["exclude_from_impact"]].copy()
    tab = pd.crosstab(use["change_reported"].fillna("(blank)"), use["measured_class"].astype("object"))
    desired_rows = [r for r in ("Increase", "Same", "Decrease") if r in tab.index]
    desired_cols = [c for c in ("shallower_now", "same_pm0.1", "deeper_now") if c in tab.columns]
    tab = tab.loc[desired_rows, desired_cols]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    im = ax.imshow(tab.to_numpy(), cmap="YlGnBu")
    ax.set_xticks(range(len(tab.columns)), tab.columns, rotation=20)
    ax.set_yticks(range(len(tab.index)), tab.index)
    for i in range(tab.shape[0]):
        for j in range(tab.shape[1]):
            ax.text(j, i, int(tab.iloc[i, j]), ha="center", va="center", color="black")
    ax.set_xlabel("Measured recalled DTW class")
    ax.set_ylabel("Reported change (Q30)")
    ax.set_title("Perception label vs tape/rope (usable wells)")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_qa_bars(qa: pd.DataFrame, path: Path) -> None:
    import matplotlib.pyplot as plt

    _style()
    counts = qa["flag"].value_counts().sort_values()
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    ax.barh(counts.index, counts.values, color="#1f4e79")
    ax.set_xlabel("Visit rows flagged")
    ax.set_title("QA flags")
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def plot_hydrographs_sample(visits: pd.DataFrame, wells: pd.DataFrame, path: Path, n: int = 12) -> None:
    import matplotlib.pyplot as plt

    _style()
    pick = wells.sort_values(["n_unique_dates", "span_days"], ascending=False).head(n)
    fig, axes = plt.subplots(4, 3, figsize=(10.5, 9.5), sharex=False)
    for ax, (_, well) in zip(axes.ravel(), pick.iterrows()):
        series = visits.loc[visits["well_id"] == well["well_id"]].sort_values("meas_date")
        ax.plot(series["meas_date"], series["wt_now"], marker="o", ms=3, color="#1f4e79")
        ax.invert_yaxis()
        ax.set_title(f"{well['province']} / {well['village']}\n{well['n_unique_dates']} dates", fontsize=8)
        ax.tick_params(axis="x", labelsize=7, rotation=30)
        ax.tick_params(axis="y", labelsize=7)
    fig.suptitle("Depth to water (m), inverted y — 12 longest series", y=1.01)
    fig.tight_layout()
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_hydrographs_pdf(visits: pd.DataFrame, wells: pd.DataFrame, path: Path) -> int:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    _style()
    long = wells.loc[wells["n_unique_dates"] >= 8].sort_values(["province", "village"])
    if long.empty:
        return 0
    per_page = 6
    pages = math.ceil(len(long) / per_page)
    with PdfPages(path) as pdf:
        for p in range(pages):
            chunk = long.iloc[p * per_page : (p + 1) * per_page]
            fig, axes = plt.subplots(3, 2, figsize=(11, 8.5))
            axes = axes.ravel()
            for i, ax in enumerate(axes):
                if i >= len(chunk):
                    ax.axis("off")
                    continue
                well = chunk.iloc[i]
                series = visits.loc[visits["well_id"] == well["well_id"]].sort_values("meas_date")
                ax.plot(series["meas_date"], series["wt_now"], marker="o", ms=3, color="#1f4e79")
                ax.invert_yaxis()
                ax.set_title(
                    f"{well['province']} / {well['village']} / {well['well_id']} "
                    f"({int(well['n_unique_dates'])} dates)",
                    fontsize=8,
                )
                ax.set_ylabel("DTW (m)", fontsize=8)
                ax.tick_params(labelsize=7, axis="x", rotation=25)
            fig.suptitle(f"Wells with ≥8 unique dates — page {p + 1}/{pages}")
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)
    return int(len(long))


def plot_all(visits: pd.DataFrame, wells: pd.DataFrame, qa: pd.DataFrame, fig_dir: Path) -> dict[str, Path]:
    _safe_mkdir(fig_dir)
    paths = {
        "map": fig_dir / "map_wells.png",
        "box_province": fig_dir / "box_dtw_change_by_province.png",
        "box_distance": fig_dir / "box_dtw_change_by_distance.png",
        "box_intervention": fig_dir / "box_dtw_change_by_intervention.png",
        "perception": fig_dir / "perception_vs_measured.png",
        "qa": fig_dir / "qa_flag_counts.png",
        "hydro_sample": fig_dir / "hydrographs_longest12.png",
        "hydro_pdf": fig_dir / "hydrographs_8plus.pdf",
    }
    plot_map(wells, paths["map"])
    plot_box_change(wells, "province", paths["box_province"], "Recalled DTW change by province")
    plot_box_change(wells, "distance_bin", paths["box_distance"], "Recalled DTW change by distance to intervention")
    plot_box_change(wells, "intervention", paths["box_intervention"], "Recalled DTW change by intervention type")
    plot_perception(wells, paths["perception"])
    plot_qa_bars(qa, paths["qa"])
    plot_hydrographs_sample(visits, wells, paths["hydro_sample"])
    plot_hydrographs_pdf(visits, wells, paths["hydro_pdf"])
    return paths


def process(csv_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, int]:
    raw = read_kobo_csv(csv_path)
    named = coerce_types(rename_kobo_columns(raw))
    kept, n_empty = drop_empty_rows(named)
    flagged = flag_visits(attach_well_id(kept))
    visits = build_visits(flagged)
    wells = build_wells(visits)
    qa = qa_flags_long(visits)
    return visits, wells, qa, n_empty


def run(csv_path: Path, table_dir: Path, fig_dir: Path, plots: bool = True) -> dict:
    visits, wells, qa, n_empty = process(csv_path)
    paths = write_tables(visits, wells, qa, table_dir)
    summary = summarize(visits, wells, qa, n_empty)
    (table_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    write_summary_md(summary, wells, table_dir / "SUMMARY.md")
    if plots:
        paths.update(plot_all(visits, wells, qa, fig_dir))
    return {"summary": summary, "paths": {k: str(v) for k, v in paths.items()}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyse FAO KOBO groundwater monitoring export")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="Path to cleaned KOBO CSV")
    parser.add_argument("--tables", type=Path, default=OUT_TABLES)
    parser.add_argument("--figures", type=Path, default=OUT_FIGS)
    parser.add_argument("--no-plots", action="store_true")
    args = parser.parse_args(argv)
    if not args.csv.exists():
        raise SystemExit(f"CSV not found: {args.csv}")
    result = run(args.csv, args.tables, args.figures, plots=not args.no_plots)
    print(json.dumps(result["summary"], indent=2, default=str))
    print("wrote", result["paths"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
