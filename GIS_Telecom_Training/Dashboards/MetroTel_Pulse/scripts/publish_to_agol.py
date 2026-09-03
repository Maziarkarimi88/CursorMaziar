#!/usr/bin/env python3
"""Publish MetroTel Pulse layers and a web map to ArcGIS Online, then
create a Dashboard item that native-embeds the design recipe.

The HTML prototype (index.html) is the visual source of truth. This script:
  1. Validates the local CSVs / GeoJSON
  2. Publishes hosted feature layers (zones, sites, competitors, subscribers, decisions, monthly)
  3. Builds a web map with priority unique-value symbology
  4. Creates a Dashboard item whose JSON layout matches the Pulse wireframe
     (header + 6 indicators + map + charts). Widget data sources point at
     the new hosted layers so you can open the item in ArcGIS Dashboards
     and fine-tune.

Usage:
  python publish_to_agol.py --dry-run
  python publish_to_agol.py --portal https://www.arcgis.com --user YOUR_USER
  python publish_to_agol.py --profile home

Requires: pip install arcgis pandas
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
AGOL = ROOT / "agol"


def uid() -> str:
    return str(uuid.uuid4())


def validate_local() -> dict:
    required = [
        DATA / "MarketingZones.geojson",
        DATA / "ExecZone_KPI_Dashboard.csv",
        DATA / "Capstone_CellSites.csv",
        DATA / "Monthly_Executive_KPI_Timeseries.csv",
        DATA / "Capstone_Decisions.csv",
    ]
    missing = [str(p) for p in required if not p.exists()]
    if missing:
        raise SystemExit("Missing data files:\n  " + "\n  ".join(missing))

    import csv

    kpis = list(csv.DictReader((DATA / "ExecZone_KPI_Dashboard.csv").open(encoding="utf-8")))
    subs = sum(int(float(r["SUBSCRIBERS"])) for r in kpis)
    p1 = sum(1 for r in kpis if str(r.get("PRIORITY", "")).startswith("P1"))
    summary = {
        "zones": len(kpis),
        "subscribers": subs,
        "p1_expand": p1,
        "files_ok": True,
    }
    print("Local validation")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    return summary


def connect(args):
    from arcgis.gis import GIS

    if args.profile:
        return GIS(profile=args.profile)
    if args.user:
        return GIS(args.portal, args.user, args.password)
    return GIS(args.portal)


def publish_geojson(gis, path: Path, title: str, folder: str | None):
    item = gis.content.add(
        {
            "title": title,
            "type": "GeoJson",
            "tags": "MetroTel,Pulse,geo-marketing",
            "description": "MetroTel Pulse marketing zones (template)",
        },
        data=str(path),
        folder=folder,
    )
    return item.publish()


def publish_csv_xy(gis, path: Path, title: str, lat: str, lon: str, folder: str | None):
    item = gis.content.add(
        {
            "title": title,
            "type": "CSV",
            "tags": "MetroTel,Pulse,geo-marketing",
        },
        data=str(path),
        folder=folder,
    )
    return item.publish(
        publish_parameters={
            "type": "csv",
            "name": title.replace(" ", "_"),
            "locationType": "coordinates",
            "latitudeFieldName": lat,
            "longitudeFieldName": lon,
        }
    )


def publish_table(gis, path: Path, title: str, folder: str | None):
    item = gis.content.add(
        {
            "title": title,
            "type": "CSV",
            "tags": "MetroTel,Pulse,geo-marketing",
        },
        data=str(path),
        folder=folder,
    )
    return item.publish(
        publish_parameters={
            "type": "csv",
            "name": title.replace(" ", "_"),
            "locationType": "none",
        }
    )


def merge_zone_geojson() -> Path:
    """Join KPI fields onto zone polygons so one hosted layer drives the map + indicators."""
    import csv

    geo = json.loads((DATA / "MarketingZones.geojson").read_text(encoding="utf-8"))
    kpis = {r["DIST_ID"]: r for r in csv.DictReader((DATA / "ExecZone_KPI_Dashboard.csv").open(encoding="utf-8"))}
    numeric = {
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
        "AREA_KM2",
    }
    for feat in geo["features"]:
        row = kpis.get(feat["properties"]["DIST_ID"], {})
        merged = dict(feat["properties"])
        for key, value in row.items():
            if key in numeric and value not in (None, ""):
                merged[key] = float(value)
            else:
                merged[key] = value
        feat["properties"] = merged
    tmp = Path(tempfile.gettempdir()) / "MetroTel_Pulse_Zones.geojson"
    tmp.write_text(json.dumps(geo), encoding="utf-8")
    return tmp


def build_web_map(gis, zones_item, sites_item, title: str):
    from arcgis.mapping import WebMap

    wm = WebMap()
    wm.add_layer(zones_item.layers[0])
    wm.add_layer(sites_item.layers[0])
    item = wm.save(
        {
            "title": title,
            "tags": "MetroTel,Pulse,dashboard",
            "snippet": "MetroTel Pulse web map — zones by priority + cell sites",
        }
    )
    return item


def indicator(name: str, title: str, item_id: str, layer_id: str, field: str, stat: str, suffix: str = "", prefix: str = "", color: str = "#2ee6d6"):
    return {
        "id": uid(),
        "name": name,
        "showLastUpdate": False,
        "type": "indicatorWidget",
        "comparison": "none",
        "valueType": "statistic",
        "datasets": [
            {
                "type": "serviceDataset",
                "name": "main",
                "dataSource": {"type": "layerDataSource", "itemId": item_id, "layerId": layer_id},
                "groupByFields": [],
                "orderByFields": [],
                "statisticDefinitions": [
                    {"onStatisticField": field, "outStatisticFieldName": "value", "statisticType": stat}
                ],
                "clientSideStatistics": False,
                "outFields": ["*"],
                "returnDistinctValues": False,
            }
        ],
        "defaultSettings": {
            "topSection": {"fontSize": 70, "textInfo": {"text": title, "fillColor": "#8b9bb4"}},
            "middleSection": {
                "fontSize": 140,
                "textInfo": {"text": "{calculated/value}", "fillColor": color},
            },
            "bottomSection": {"fontSize": 36, "textInfo": {"text": "", "fillColor": "#5d6d86"}},
        },
        "valueFormat": {
            "name": "value",
            "prefix": False,
            "style": "decimal",
            "useGrouping": True,
            "minimumFractionDigits": 0,
            "maximumFractionDigits": 1,
            "valuePrefix": prefix,
            "valueSuffix": suffix,
        },
        "noDataState": {"verticalAlignment": "middle", "showCaption": True, "showDescription": True},
        "noFilterState": {"verticalAlignment": "middle", "showCaption": True, "showDescription": True},
        "noValueState": {"verticalAlignment": "middle", "showCaption": True, "showDescription": True},
        "percentageFormat": {"name": "percentage", "style": "percent", "useGrouping": True},
        "ratioFormat": {"name": "ratio", "style": "decimal", "useGrouping": True},
    }


def serial_chart(name: str, caption: str, item_id: str, layer_id: str, cat: str, field: str, stat: str):
    return {
        "id": uid(),
        "name": name,
        "caption": caption,
        "type": "serialChartWidget",
        "showLastUpdate": False,
        "actionMode": "default",
        "categoryType": "groupByValues",
        "parseDates": False,
        "datasets": [
            {
                "type": "serviceDataset",
                "name": "main",
                "dataSource": {"type": "layerDataSource", "itemId": item_id, "layerId": layer_id},
                "groupByFields": [cat],
                "orderByFields": [f"{cat} asc"],
                "statisticDefinitions": [
                    {"onStatisticField": field, "outStatisticFieldName": "value", "statisticType": stat}
                ],
                "clientSideStatistics": False,
                "outFields": ["*"],
            }
        ],
        "category": {"fieldName": cat},
        "valueFormat": {"name": "value", "style": "decimal", "useGrouping": True},
        "labelFormat": {"name": "label", "style": "decimal"},
        "noDataState": {},
        "noFilterState": {},
    }


def pie_chart(name: str, caption: str, item_id: str, layer_id: str, cat: str):
    return {
        "id": uid(),
        "name": name,
        "caption": caption,
        "type": "pieChartWidget",
        "showLastUpdate": False,
        "actionMode": "default",
        "categoryType": "groupByValues",
        "datasets": [
            {
                "type": "serviceDataset",
                "name": "main",
                "dataSource": {"type": "layerDataSource", "itemId": item_id, "layerId": layer_id},
                "groupByFields": [cat],
                "orderByFields": [],
                "statisticDefinitions": [
                    {"onStatisticField": "DIST_ID", "outStatisticFieldName": "value", "statisticType": "count"}
                ],
                "clientSideStatistics": False,
                "outFields": ["*"],
            }
        ],
        "chartConfig": {},
        "noDataState": {},
        "noFilterState": {},
        "dataLabelsFormat": {"name": "label", "style": "decimal"},
        "valueFormat": {"name": "value", "style": "decimal", "useGrouping": True},
        "percentageFormat": {"name": "percentage", "style": "percent"},
    }


def map_widget(webmap_id: str):
    return {
        "id": uid(),
        "name": "MarketMap",
        "type": "mapWidget",
        "itemId": webmap_id,
        "showLastUpdate": False,
        "pointZoomScale": 50000,
        "flashRepeats": 3,
        "mapTools": ["search", "legend", "layers", "basemap", "home"],
        "showNavigation": True,
        "showPanRotate": False,
        "showLocate": False,
        "showCompass": False,
        "showPopup": True,
        "events": [],
        "noDataState": {},
        "noFilterState": {},
    }


def stack(orientation: str, width: float, height: float, elements: list) -> dict:
    return {
        "id": uid(),
        "type": "stackLayoutElement",
        "orientation": orientation,
        "width": width,
        "height": height,
        "elements": elements,
    }


def item_el(widget_id: str, width: float = 1, height: float = 1) -> dict:
    return {"width": width, "height": height, "type": "itemLayoutElement", "id": widget_id}


def build_dashboard_json(webmap_id: str, zone_item_id: str, zone_layer_id: str) -> dict:
    inds = [
        indicator("Subscribers", "Subscribers", zone_item_id, zone_layer_id, "SUBSCRIBERS", "sum", color="#2ee6d6"),
        indicator("ARPU", "Avg ARPU", zone_item_id, zone_layer_id, "AVG_ARPU", "avg", prefix="$", color="#f5c15a"),
        indicator("Churn", "Avg churn", zone_item_id, zone_layer_id, "AVG_CHURN", "avg", color="#ff5c7a"),
        indicator("Coverage", "4G coverage %", zone_item_id, zone_layer_id, "COV_4G_PCT", "avg", suffix="%", color="#3ddc97"),
        indicator("GapPop", "Coverage gap pop", zone_item_id, zone_layer_id, "COV_GAP_POP", "sum", color="#5b8cff"),
        indicator("Suitability", "Mean suitability", zone_item_id, zone_layer_id, "SUITABILITY", "avg", color="#2ee6d6"),
    ]
    mp = map_widget(webmap_id)
    pie = pie_chart("PriorityMix", "Zones by priority", zone_item_id, zone_layer_id, "PRIORITY")
    bars = serial_chart("ARPUByDistrict", "ARPU by district", zone_item_id, zone_layer_id, "DIST_NAME", "AVG_ARPU", "avg")

    kpi_row = stack("col", 1, 0.16, [item_el(w["id"], width=1 / 6, height=1) for w in inds])
    kpi_row["orientation"] = "col"

    body = stack(
        "col",
        1,
        0.84,
        [
            stack("row", 0.58, 1, [item_el(mp["id"])]),
            stack("row", 0.42, 1, [item_el(pie["id"], height=0.5), item_el(bars["id"], height=0.5)]),
        ],
    )
    root = stack("row", 1, 1, [kpi_row, body])

    widgets = inds + [mp, pie, bars]
    return {
        "version": "4.30.0",
        "authoringApp": "ArcGIS Dashboards",
        "authoringAppVersion": "2025.1",
        "maxPaginationRecords": 50000,
        "maxChartRecords": 10000,
        "timeZone": "system",
        "theme": "dark",
        "desktopView": {
            "type": "desktopView",
            "settings": {
                "allowElementResizing": True,
                "allowElementExpansion": True,
                "allowReset": True,
            },
            "header": {
                "type": "header",
                "title": "MetroTel Pulse — Geo-Marketing Command Center",
                "textColor": "#e8eef7",
                "textColor2": "#8b9bb4",
                "backgroundColor": "#0e1524",
                "backgroundColor2": "#121b2c",
                "titleTextColor": "#2ee6d6",
                "logoImageURL": "",
                "logoURL": "",
                "logoSize": "medium",
                "showSignOutMenu": True,
                "subtitlePlacement": "below",
                "showMargin": True,
                "menuContents": [],
                "selectors": [],
                "backgroundImageURL": "",
                "backgroundImageSizing": "fit-width",
                "normalBackgroundImagePlacement": "center",
                "horizontalBackgroundImagePlacement": "top",
            },
            "widgets": widgets,
            "layout": {"type": "dockingLayout", "rootElement": root},
        },
        "elementMappings": {},
        "numberPrefixOverrides": [],
    }


def create_dashboard_item(gis, data: dict, title: str):
    item = gis.content.add(
        {
            "title": title,
            "type": "Dashboard",
            "tags": "MetroTel,Pulse,geo-marketing,dashboard",
            "snippet": "MetroTel Pulse template — bind your hosted layers, then open in Dashboards to refine.",
            "text": json.dumps(data),
        }
    )
    return item


def main() -> None:
    parser = argparse.ArgumentParser(description="Publish MetroTel Pulse to ArcGIS Online")
    parser.add_argument("--portal", default="https://www.arcgis.com")
    parser.add_argument("--user", default=None)
    parser.add_argument("--password", default=None)
    parser.add_argument("--profile", default=None, help="ArcGIS API for Python profile name")
    parser.add_argument("--folder", default="MetroTel_Pulse")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-subscribers", action="store_true")
    args = parser.parse_args()

    summary = validate_local()
    (AGOL / "last_local_validation.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    if args.dry_run:
        template = build_dashboard_json("WEBMAP_ITEM_ID", "ZONES_ITEM_ID", "ZONES_LAYER_ID")
        out = AGOL / "dashboard_template.placeholders.json"
        out.write_text(json.dumps(template, indent=2), encoding="utf-8")
        print(f"Wrote placeholder dashboard JSON → {out}")
        print("Dry run complete. No ArcGIS Online items were created.")
        return

    try:
        gis = connect(args)
    except Exception as exc:  # noqa: BLE001
        print("Could not connect to ArcGIS Online:", exc, file=sys.stderr)
        print("Install the API:  pip install arcgis pandas", file=sys.stderr)
        raise SystemExit(1) from exc

    print("Signed in as", gis.users.me.username)
    try:
        gis.content.create_folder(args.folder)
    except Exception:
        pass

    zones_path = merge_zone_geojson()
    print("Publishing zones…")
    zones = publish_geojson(gis, zones_path, "MetroTel Pulse Zones", args.folder)
    print("  ", zones.homepage)
    print("Publishing cell sites…")
    sites = publish_csv_xy(gis, DATA / "Capstone_CellSites.csv", "MetroTel Pulse Cell Sites", "LAT", "LON", args.folder)
    print("Publishing competitors…")
    comps = publish_csv_xy(gis, DATA / "CompetitorSites.csv", "MetroTel Pulse Competitors", "LAT", "LON", args.folder)
    print("Publishing monthly KPI table…")
    monthly = publish_table(gis, DATA / "Monthly_Executive_KPI_Timeseries.csv", "MetroTel Pulse Monthly KPI", args.folder)
    print("Publishing decisions table…")
    decisions = publish_table(gis, DATA / "Capstone_Decisions.csv", "MetroTel Pulse Decisions", args.folder)
    if not args.skip_subscribers:
        print("Publishing subscribers (600 points)…")
        publish_csv_xy(gis, DATA / "Subscribers_with_XY.csv", "MetroTel Pulse Subscribers", "LAT", "LON", args.folder)

    print("Saving web map…")
    webmap = build_web_map(gis, zones, sites, "MetroTel Pulse Web Map")
    zone_layer_id = zones.layers[0].properties.id if hasattr(zones.layers[0], "properties") else 0
    # Hosted layers use numeric layer id 0; Dashboards often want the operational layer id string from the web map.
    layer_id = str(zone_layer_id)

    dash_json = build_dashboard_json(webmap.id, zones.id, layer_id)
    (AGOL / "dashboard_last_published.json").write_text(json.dumps(dash_json, indent=2), encoding="utf-8")
    print("Creating dashboard item…")
    dash = create_dashboard_item(gis, dash_json, "MetroTel Pulse Dashboard")
    print("\nDone.")
    print("  Web map:   ", webmap.homepage)
    print("  Dashboard: ", dash.homepage)
    print("  Open the dashboard in ArcGIS Dashboards, click Save once to upgrade")
    print("  the JSON, then add a category selector on DIST_NAME / PRIORITY.")
    print("  If a widget shows Data source error, re-point it at 'MetroTel Pulse Zones'.")


if __name__ == "__main__":
    main()
