# Rebuild this design as a native ArcGIS Online Dashboard

Use this when you want **ArcGIS Dashboards widgets** (not the HTML prototype) but the same layout, colors, and questions.

The visual source of truth is `index.html`. Recreate it in [ArcGIS Dashboards](https://www.arcgis.com/apps/dashboards/index.html) after `scripts/publish_to_agol.py` has published the layers and web map.

## Theme

Create a **dark** dashboard. If you use a user theme, paste:

| Token | Hex |
|---|---|
| Background | `#070B14` |
| Panel | `#121B2C` |
| Text | `#E8EEF7` |
| Muted | `#8B9BB4` |
| Accent (high-value / P2) | `#2EE6D6` |
| Revenue / P1 | `#F5C15A` |
| Churn / P3 | `#FF5C7A` |
| Coverage / OK | `#3DDC97` |
| Monitor / P4 | `#5B8CFF` |

Header title: `MetroTel Pulse — Geo-Marketing Command Center`  
Subtitle: `Capital Region · bind DIST_ID to your own zones`

## Layout (desktop)

1. Header on.
2. Add a **row** on top (~16% height) with **six Indicator** widgets.
3. Remaining body: **two columns** — map 58% / charts 42%.
4. Right column: **Priority pie** on top, **ARPU serial chart** below.
5. Optional second row: monthly serial chart (from the monthly table) + list of decisions.

This matches the HTML prototype.

## Widgets

All spatial widgets use the **MetroTel Pulse Web Map**. Indicators and charts use the **MetroTel Pulse Zones** layer (polygons with KPI fields already joined).

| Widget | Data | Statistic | Notes |
|---|---|---|---|
| Indicator: Subscribers | Zones | Sum `SUBSCRIBERS` | Cyan value |
| Indicator: ARPU | Zones | Average `AVG_ARPU` | Prefix `$` |
| Indicator: Churn | Zones | Average `AVG_CHURN` | Format percent if stored 0–1 |
| Indicator: P1 zones | Zones | Count, filter `PRIORITY` starts with `P1` | Or a view |
| Indicator: 4G coverage | Zones | Average `COV_4G_PCT` | Suffix `%` |
| Indicator: Coverage gap | Zones | Sum `COV_GAP_POP` | |
| Map | Pulse web map | — | Legend, search, layer list, pop-ups |
| Pie | Zones | Count grouped by `PRIORITY` | Colors from the table above |
| Serial (bar) | Zones | Average `AVG_ARPU` grouped by `DIST_NAME` | Sort descending |
| Serial (line) | Monthly KPI table | `SUBSCRIBERS` + `ARPU_USD` by `MONTH` | Parse dates |
| List | Decisions table | — | Line 1 `TITLE`, line 2 `ZONE · OWNER · STATUS` |
| Category selector (header) | Zones | `DIST_NAME` | Action: filter all widgets + filter map |
| Category selector | Zones | `PRIORITY` | Same |

## Actions (this is what makes it a dashboard, not a poster)

1. Header **zone** selector → Filter **zones, sites, decisions, all indicators and charts**.
2. Header **priority** selector → Filter zones (and therefore the map).
3. Map extent → Filter charts (optional).
4. List click → **Zoom / flash** the matching zone (`ZONE` = `DIST_ID`).
5. Pie slice click → Filter the map to that priority.

## Bind your own data

Keep the **field names** in `agol/field_map.json`. Two options:

1. Rename your CSV columns to `DIST_ID`, `DIST_NAME`, `SUBSCRIBERS`, `AVG_ARPU`, `AVG_CHURN`, `COV_4G_PCT`, `PRIORITY`, then re-run the publish script.
2. Publish your layer as-is, then in ArcGIS Assistant / Python `DashboardManager.replace_dependencies` map old item IDs to new ones. Field mapping works on dashboard version `4.30.0+`.

If your churn is stored as 18.4 (percent) instead of 0.184, either divide in a hosted view or change the indicator format.

## Embed the HTML prototype inside a native dashboard

If you prefer the HTML design as-is:

1. Host `index.html` + `assets/` + `data/` on any HTTPS site (GitHub Pages, org web server, or an ArcGIS Hub page).
2. In Dashboards, add **Embedded content** → URL of that page.
3. Keep a native **map widget** next to it if you need ArcGIS identify / bookmarks.

The HTML file also accepts a zone KPI CSV via **Load my CSV** or drag-and-drop, so you can demo your data before publishing.
