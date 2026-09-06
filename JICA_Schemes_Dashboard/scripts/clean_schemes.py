#!/usr/bin/env python3
"""Clean the JICA IS + WSM tracker into a dashboard-ready table."""

from __future__ import annotations

import csv
import re
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "schemes_dashboard.csv"

ALIASES = {
    "package": ("Package_Name", "Contract package ", "Contract package"),
    "scheme_name": ("Scheme_Name", "Name of Scheme"),
    "start": ("Contract_Signed_date", "Contract Signed date"),
    "end": ("Contract_End_Date", "Contract End Date"),
    "status": ("Awarding_Status",),
    "cost": ("Contract_Cost_USD", "Contract Cost (USD)"),
    "contractor": ("Cosntrution_Company", "Cosntrution Company"),
    "area": ("Intervention_Area (Ha)", "Area after intervention (Ha)"),
    "hh": ("Households", "NumberOfHousehold"),
    "fhh": ("Female_Headed_HH", "Female_Headed_Household"),
    "canal": ("Canal_Length_Km", "CanalLength(Km)"),
    "source_id": ("Unique_ID", "#"),
}


def latest_raw() -> Path:
    files = list((ROOT / "data").glob("raw_Both_Jica*.csv"))
    if not files:
        raise SystemExit("No raw_Both_Jica*.csv in data/")
    return max(files, key=lambda p: p.stat().st_mtime)


def pick(row: dict, *names: str) -> str:
    for name in names:
        if name in row and row[name] not in (None, ""):
            return row[name]
    return ""

# District-level centroids (approximate). Not village GPS.
CENTROIDS = {
    ("Bamyan", "Bamyan City"): (67.83, 34.82),
    ("Ghazni", "Qarabagh"): (67.99, 33.22),
    ("Herat", "Obe"): (63.18, 34.37),
    ("Maidan Wardak", "Sayed Abad"): (68.72, 34.00),
    ("Zabul", "Kakar"): (67.25, 32.22),
    ("Baghlan", "Khenjan"): (68.90, 35.58),
    ("Faryab", "Almar"): (64.28, 35.96),
}

REGION_SPLIT = re.compile(r"\s*/\s*")


def clean_text(value: str | None) -> str:
    text = (value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text.rstrip(",")


def parse_number(value: str | None):
    text = clean_text(value).replace(",", "")
    if text == "" or text.lower() == "not awarded":
        return None
    if re.search(r"[A-Za-z]", text):
        return None
    try:
        number = float(text)
        return int(number) if number.is_integer() else number
    except ValueError:
        return None


def parse_date(value: str | None):
    text = clean_text(value)
    if not text:
        return None
    for fmt in ("%d-%b-%y", "%d-%b-%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(text, fmt)
            if fmt == "%d-%b-%y" and dt.year < 2000:
                dt = dt.replace(year=dt.year + 100)
            return dt.date()
        except ValueError:
            continue
    return None


def looks_like_excel_date(value: str | None) -> bool:
    text = clean_text(value)
    return bool(re.match(r"^\d{1,2}-[A-Za-z]{3}-\d{2}$", text))


def program_from_type(intervention: str, package: str) -> str:
    blob = f"{intervention} {package}".lower()
    if "watershed" in blob or "wsm" in blob or "check dam" in blob:
        return "Watershed"
    return "Irrigation"


def package_no(package: str) -> int | None:
    match = re.search(r"Package\s*#\s*(\d+)", package, re.I)
    return int(match.group(1)) if match else None


def split_region(region: str) -> tuple[str, str]:
    parts = REGION_SPLIT.split(region, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return region, ""


def main() -> None:
    raw_path = latest_raw()
    print("Source", raw_path.name)
    with raw_path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))

    out_rows = []
    for raw in rows:
        package = clean_text(pick(raw, *ALIASES["package"]))
        if not package:
            continue

        intervention = clean_text(raw.get("InterventionType"))
        program = program_from_type(intervention, package)
        pkg = package_no(package) or 0
        pair_id = f"SITE-{pkg:02d}"
        scheme_uid = f"JICA-{'IS' if program == 'Irrigation' else 'WSM'}-{pkg:02d}"

        cost_raw = clean_text(pick(raw, *ALIASES["cost"]))
        start = parse_date(pick(raw, *ALIASES["start"]))
        end = parse_date(pick(raw, *ALIASES["end"]))
        flags = []

        status_raw = clean_text(pick(raw, *ALIASES["status"]))
        if status_raw:
            status = status_raw
        elif cost_raw.lower() == "not awarded" or not start:
            status = "Not Awarded"
        else:
            status = "Awarded"

        cost = parse_number(cost_raw)
        if status == "Awarded" and looks_like_excel_date(cost_raw):
            cost = None
            flags.append("COST_LOOKS_LIKE_EXCEL_DATE")
        if status == "Not Awarded":
            cost = None

        area = parse_number(pick(raw, *ALIASES["area"]))
        hh = parse_number(pick(raw, *ALIASES["hh"]))
        fhh = parse_number(pick(raw, *ALIASES["fhh"]))
        canal = parse_number(pick(raw, *ALIASES["canal"]))
        source_id = clean_text(pick(raw, *ALIASES["source_id"]))

        if program == "Watershed" and canal is None:
            flags.append("NO_CANAL_EXPECTED")
        if start and end and (end - start).days < 60:
            flags.append("SHORT_CONTRACT_CHECK")
        if not clean_text(raw.get("SchemeCode")):
            flags.append("MISSING_SCHEME_CODE")
        if hh and fhh and fhh > hh:
            flags.append("FHH_GT_HOUSEHOLDS")

        province = clean_text(raw.get("Province"))
        district = clean_text(raw.get("District"))
        lon, lat = CENTROIDS.get((province, district), (None, None))
        if lon is None:
            flags.append("NO_XY")
        elif program == "Watershed":
            lon = round(lon + 0.05, 5)
            lat = round(lat + 0.03, 5)

        duration = (end - start).days if start and end else None
        fhh_pct = round(100 * fhh / hh, 1) if hh and fhh is not None else None
        cost_per_ha = round(cost / area, 1) if cost and area else None
        cost_per_hh = round(cost / hh, 1) if cost and hh else None
        region, hub = split_region(clean_text(raw.get("Region")))

        out_rows.append(
            {
                "SCHEME_UID": scheme_uid,
                "PAIR_ID": pair_id,
                "PACKAGE_NO": pkg,
                "PROGRAM": program,
                "INTERVENTION_TYPE": intervention,
                "SCHEME_CODE": clean_text(raw.get("SchemeCode")),
                "SOURCE_ID": source_id,
                "SCHEME_NAME": clean_text(pick(raw, *ALIASES["scheme_name"])),
                "CONTRACT_PACKAGE": package,
                "REGION": region,
                "REGION_HUB": hub,
                "PROVINCE": province,
                "DISTRICT": district,
                "VILLAGE": clean_text(raw.get("Villages")),
                "STATUS": status,
                "CONTRACT_START": start.isoformat() if start else "",
                "CONTRACT_END": end.isoformat() if end else "",
                "DURATION_DAYS": duration if duration is not None else "",
                "COST_USD": cost if cost is not None else "",
                "CONTRACTOR": clean_text(pick(raw, *ALIASES["contractor"])),
                "AREA_HA": area if area is not None else "",
                "HOUSEHOLDS": hh if hh is not None else "",
                "FEMALE_HEADED_HH": fhh if fhh is not None else "",
                "FHH_PCT": fhh_pct if fhh_pct is not None else "",
                "CANAL_KM": canal if canal is not None else "",
                "COST_PER_HA": cost_per_ha if cost_per_ha is not None else "",
                "COST_PER_HH": cost_per_hh if cost_per_hh is not None else "",
                "LON": lon if lon is not None else "",
                "LAT": lat if lat is not None else "",
                "XY_SOURCE": "District centroid (approximate)" if lon else "",
                "DATA_FLAGS": ";".join(flags),
            }
        )

    fieldnames = list(out_rows[0].keys())
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    awarded = sum(1 for r in out_rows if r["STATUS"] == "Awarded")
    print(f"Wrote {OUT} rows={len(out_rows)} awarded={awarded}")
    for row in out_rows:
        if row["DATA_FLAGS"]:
            print(f"  {row['SCHEME_UID']}: {row['DATA_FLAGS']}")


if __name__ == "__main__":
    main()
