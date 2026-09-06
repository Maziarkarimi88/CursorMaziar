#!/usr/bin/env python3
"""Pack CSV + GeoJSON sample data into assets/embedded-data.js for file:// preview."""

from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "assets" / "embedded-data.js"


def read_csv(name: str) -> list[dict]:
    path = DATA / name
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def to_number(value: str | None):
    if value is None or value == "":
        return None
    try:
        if any(ch in value for ch in ".eE"):
            return float(value)
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def numerify(rows: list[dict], fields: list[str]) -> list[dict]:
    out = []
    for row in rows:
        item = dict(row)
        for field in fields:
            if field in item:
                item[field] = to_number(item[field])
        out.append(item)
    return out


def main() -> None:
    zones = json.loads((DATA / "MarketingZones.geojson").read_text(encoding="utf-8"))
    kpis = numerify(
        read_csv("ExecZone_KPI_Dashboard.csv"),
        [
            "POPULATION",
            "AFFLUENCE",
            "SUBSCRIBERS",
            "AVG_ARPU",
            "AVG_CHURN",
            "COV_4G_PCT",
            "COV_GAP_POP",
            "SUITABILITY",
            "CENTROID_LON",
            "CENTROID_LAT",
        ],
    )
    monthly = numerify(
        read_csv("Monthly_Executive_KPI_Timeseries.csv"),
        ["SUBSCRIBERS", "ARPU_USD", "CHURN_PCT", "DROPPED_CALLS_PCT", "FIBER_HP_PASSED", "MW_LINKS_ONAIR", "NPS"],
    )
    sites = numerify(
        read_csv("Capstone_CellSites.csv"),
        ["LON", "LAT", "RSRP_MEAN"],
    )
    competitors = numerify(read_csv("CompetitorSites.csv"), ["LON", "LAT"])
    decisions = read_csv("Capstone_Decisions.csv")
    subscribers = numerify(
        read_csv("Subscribers_with_XY.csv"),
        ["TENURE_MONTHS", "ARPU_USD", "CHURN_RISK", "DROP_RATE_PCT", "THROUGHPUT_MBPS", "COMPLAINTS_90D", "LON", "LAT"],
    )

    payload = {
        "generated_from": "MetroTel Day 3 + Day 5 training tables",
        "zones": zones,
        "kpis": kpis,
        "monthly": monthly,
        "sites": sites,
        "competitors": competitors,
        "decisions": decisions,
        "subscribers": subscribers,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "/* Auto-generated. Re-run scripts/build_embedded_data.py after editing data/. */\n"
        "window.PULSE_DATA = "
        + json.dumps(payload, ensure_ascii=False)
        + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes)")
    print(f"  zones={len(zones['features'])} kpis={len(kpis)} sites={len(sites)} "
          f"subscribers={len(subscribers)} decisions={len(decisions)}")


if __name__ == "__main__":
    main()
