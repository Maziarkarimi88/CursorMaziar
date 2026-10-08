"""Mann-Kendall, p-value and Sen's slope on 10 weekly wells (teaching example).

Higher water level (m) = more water in the well.
Sen's slope from pymannkendall is per week; multiply by 52 for m/year.

  python3 examples/run_mk_sen_weekly.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pymannkendall as mk

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "mk_sen_10wells_weekly.csv"


def main() -> None:
    df = pd.read_csv(CSV, parse_dates=["date"])
    wells = [c for c in df.columns if c != "date"]
    rows = []
    for name in wells:
        y = df[name].to_numpy()
        orig = mk.original_test(y, alpha=0.05)
        hamed = mk.hamed_rao_modification_test(y, alpha=0.05)
        rows.append(
            {
                "well": name,
                "n_weeks": len(y),
                "first_m": round(float(y[0]), 3),
                "last_m": round(float(y[-1]), 3),
                "mk_trend": orig.trend,
                "p_value": orig.p,
                "sen_m_per_year": orig.slope * 52,
                "modified_mk_trend": hamed.trend,
                "modified_p_value": hamed.p,
            }
        )
    out = pd.DataFrame(rows)
    print(out.to_string(index=False, float_format=lambda v: f"{v:.4g}"))
    print()
    print("Rule: p < 0.05 means we treat the trend as real (not luck).")
    print("Weekly data can fake a small p-value; trust modified_p_value more.")
    print("Sen m/year: + rising water, − falling water.")


if __name__ == "__main__":
    main()
