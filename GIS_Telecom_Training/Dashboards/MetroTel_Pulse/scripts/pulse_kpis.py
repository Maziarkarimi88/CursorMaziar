"""KPI math used by the Pulse dashboard (must match assets/dashboard.js)."""

from __future__ import annotations

from typing import Iterable


def num(value) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def weighted_mean(rows: Iterable[dict], value_field: str, weight_field: str) -> float:
    rows = list(rows)
    weight = sum(num(r.get(weight_field)) for r in rows)
    if weight == 0:
        return 0.0
    return sum(num(r.get(value_field)) * num(r.get(weight_field)) for r in rows) / weight


def summarize_zones(rows: Iterable[dict]) -> dict:
    rows = list(rows)
    subscribers = sum(num(r.get("SUBSCRIBERS")) for r in rows)
    return {
        "zone_count": len(rows),
        "subscribers": subscribers,
        "arpu_weighted": weighted_mean(rows, "AVG_ARPU", "SUBSCRIBERS"),
        "churn_weighted": weighted_mean(rows, "AVG_CHURN", "SUBSCRIBERS"),
        "coverage_pop_weighted": weighted_mean(rows, "COV_4G_PCT", "POPULATION"),
        "p1_expand": sum(1 for r in rows if str(r.get("PRIORITY", "")).startswith("P1")),
        "population": sum(num(r.get("POPULATION")) for r in rows),
    }
