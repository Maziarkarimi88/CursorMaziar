#!/usr/bin/env python3
"""Build one polygon + one line per scheme for the dashboard map.

These are stand-in shapes from district centroids, AREA_HA, and CANAL_KM
until surveyed GIS is swapped in. Keep SCHEME_UID on every feature so
the map can zoom to that scheme's combined extent.
"""

from __future__ import annotations

import csv
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "data" / "schemes_dashboard.csv"
AREAS = ROOT / "data" / "schemes_areas.geojson"
LINES = ROOT / "data" / "schemes_lines.geojson"
EMBED = ROOT / "assets" / "embedded-data.js"

GEOM_NOTE = (
    "Placeholder geometry from district centroid, AREA_HA, and CANAL_KM. "
    "Replace data/schemes_areas.geojson and data/schemes_lines.geojson "
    "with surveyed polygons and lines that keep SCHEME_UID."
)


def num(value):
    text = str(value or "").strip()
    if text == "":
        return None
    try:
        number = float(text)
    except ValueError:
        return None
    return number


def meters_per_degree(lat: float) -> tuple[float, float]:
    lat_m = 111_320.0
    lon_m = 111_320.0 * math.cos(math.radians(lat))
    return lon_m, lat_m


def offset(lon: float, lat: float, east_m: float, north_m: float) -> list[float]:
    lon_m, lat_m = meters_per_degree(lat)
    return [round(lon + east_m / lon_m, 6), round(lat + north_m / lat_m, 6)]


def area_radius_m(area_ha: float | None, program: str) -> float:
    hectares = area_ha if area_ha and area_ha > 0 else (80 if program == "Watershed" else 40)
    radius = math.sqrt((hectares * 10_000.0) / math.pi)
    return max(450.0, min(radius, 6_500.0))


def line_length_m(canal_km: float | None, program: str) -> float:
    if canal_km and canal_km > 0:
        return max(800.0, min(canal_km * 1_000.0, 14_000.0))
    return 1_400.0 if program == "Watershed" else 2_400.0


def polygon_ring(lon: float, lat: float, radius_m: float, seed: int, vertices: int = 9) -> list[list[float]]:
    rng = random.Random(seed)
    rot = rng.uniform(0, math.tau)
    coords = []
    for i in range(vertices):
        angle = rot + math.tau * i / vertices
        stretch = 1.18 if i % 3 == 0 else 0.86
        radius = radius_m * stretch * rng.uniform(0.88, 1.12)
        coords.append(offset(lon, lat, radius * math.cos(angle), radius * math.sin(angle)))
    coords.append(coords[0])
    return coords


def alignment_line(lon: float, lat: float, length_m: float, seed: int) -> list[list[float]]:
    rng = random.Random(seed + 17)
    azimuth = rng.uniform(0.15, math.pi - 0.15)
    half = length_m / 2
    points = []
    for t in (-1.0, -0.4, 0.15, 0.55, 1.0):
        wobble = math.sin((t + 1) * 2.1) * (length_m * 0.07)
        east = t * half * math.sin(azimuth) + wobble * math.cos(azimuth)
        north = t * half * math.cos(azimuth) - wobble * math.sin(azimuth)
        points.append(offset(lon, lat, east, north))
    return points


def feature_props(row: dict, extra: dict) -> dict:
    props = {
        "SCHEME_UID": row["SCHEME_UID"],
        "PAIR_ID": row["PAIR_ID"],
        "PROGRAM": row["PROGRAM"],
        "SCHEME_CODE": row["SCHEME_CODE"],
        "SCHEME_NAME": row["SCHEME_NAME"],
        "STATUS": row["STATUS"],
        "PROVINCE": row["PROVINCE"],
        "DISTRICT": row["DISTRICT"],
        "COST_USD": num(row["COST_USD"]),
        "AREA_HA": num(row["AREA_HA"]),
        "HOUSEHOLDS": num(row["HOUSEHOLDS"]),
        "CANAL_KM": num(row["CANAL_KM"]),
        "GEOM_SOURCE": GEOM_NOTE,
    }
    props.update(extra)
    return props


def collection(features: list[dict]) -> dict:
    return {"type": "FeatureCollection", "features": features}


def main() -> None:
    with TABLE.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    areas = []
    lines = []
    for row in rows:
        lon = num(row["LON"])
        lat = num(row["LAT"])
        if lon is None or lat is None:
            continue
        program = row["PROGRAM"]
        seed = sum(ord(ch) for ch in row["SCHEME_UID"])
        radius = area_radius_m(num(row["AREA_HA"]), program)
        length = line_length_m(num(row["CANAL_KM"]), program)
        area_kind = "command_area" if program == "Irrigation" else "watershed"
        line_kind = "canal" if program == "Irrigation" else "check_dam_alignment"

        areas.append(
            {
                "type": "Feature",
                "properties": feature_props(row, {"FEATURE_KIND": "polygon", "AREA_KIND": area_kind}),
                "geometry": {"type": "Polygon", "coordinates": [polygon_ring(lon, lat, radius, seed)]},
            }
        )
        lines.append(
            {
                "type": "Feature",
                "properties": feature_props(row, {"FEATURE_KIND": "line", "LINE_KIND": line_kind}),
                "geometry": {"type": "LineString", "coordinates": alignment_line(lon, lat, length, seed)},
            }
        )

    AREAS.write_text(json.dumps(collection(areas), indent=2), encoding="utf-8")
    LINES.write_text(json.dumps(collection(lines), indent=2), encoding="utf-8")

    EMBED.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "geomNote": GEOM_NOTE,
        "schemes": rows,
        "areas": collection(areas),
        "lines": collection(lines),
    }
    EMBED.write_text(
        "window.JICA_DATA = " + json.dumps(payload, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(areas)} polygons, {len(lines)} lines")


if __name__ == "__main__":
    main()
