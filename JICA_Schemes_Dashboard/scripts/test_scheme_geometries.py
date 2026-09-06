#!/usr/bin/env python3
"""Check that every scheme has a unique code plus one polygon and one line."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def bounds(geom: dict) -> tuple[float, float, float, float]:
    xs: list[float] = []
    ys: list[float] = []

    def walk(node):
        if not isinstance(node, list) or not node:
            return
        if isinstance(node[0], (int, float)):
            xs.append(float(node[0]))
            ys.append(float(node[1]))
            return
        for item in node:
            walk(item)

    walk(geom["coordinates"])
    return min(xs), min(ys), max(xs), max(ys)


def main() -> None:
    rows = list(csv.DictReader((ROOT / "data" / "schemes_dashboard.csv").open(encoding="utf-8")))
    areas = json.loads((ROOT / "data" / "schemes_areas.geojson").read_text(encoding="utf-8"))
    lines = json.loads((ROOT / "data" / "schemes_lines.geojson").read_text(encoding="utf-8"))
    embed = (ROOT / "assets" / "embedded-data.js").read_text(encoding="utf-8")

    assert len(rows) == 14, len(rows)
    codes = [row["SCHEME_CODE"] for row in rows]
    assert len(set(codes)) == 14, Counter(codes)
    uids = [row["SCHEME_UID"] for row in rows]
    assert len(set(uids)) == 14

    area_ids = [feat["properties"]["SCHEME_UID"] for feat in areas["features"]]
    line_ids = [feat["properties"]["SCHEME_UID"] for feat in lines["features"]]
    assert sorted(area_ids) == sorted(uids)
    assert sorted(line_ids) == sorted(uids)

    for feat in areas["features"]:
        assert feat["geometry"]["type"] == "Polygon"
        west, south, east, north = bounds(feat["geometry"])
        assert east > west and north > south
        assert all(math.isfinite(v) for v in (west, south, east, north))
    for feat in lines["features"]:
        assert feat["geometry"]["type"] == "LineString"
        west, south, east, north = bounds(feat["geometry"])
        assert east > west or north > south
        assert all(math.isfinite(v) for v in (west, south, east, north))

    # Combined extent for a scheme must be larger than either part alone
    # (or at least cover both). Yakawlang irrigation is a typical case.
    sample = "JICA-IS-06"
    area = next(f for f in areas["features"] if f["properties"]["SCHEME_UID"] == sample)
    line = next(f for f in lines["features"] if f["properties"]["SCHEME_UID"] == sample)
    aw, as_, ae, an = bounds(area["geometry"])
    lw, ls, le, ln = bounds(line["geometry"])
    cw, cs, ce, cn = min(aw, lw), min(as_, ls), max(ae, le), max(an, ln)
    assert cw <= aw and cw <= lw
    assert ce >= ae and ce >= le
    assert cs <= as_ and cs <= ls
    assert cn >= an and cn >= ln

    assert "window.JICA_DATA" in embed
    assert sample in embed
    print("ok", len(rows), "schemes, unique codes, polygon+line extents")


if __name__ == "__main__":
    main()
