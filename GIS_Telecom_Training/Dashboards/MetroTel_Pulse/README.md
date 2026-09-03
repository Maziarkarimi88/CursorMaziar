# MetroTel Pulse — ArcGIS Online dashboard template

A designed **Geo-Marketing & Customer Analytics** command center for the GIS-in-telecom course (Day 3 labs → Day 5 capstone).

**Download pack:** `GIS_Telecom_Training/Dashboards/MetroTel_Pulse_Dashboard_Template.zip`  
Unzip and open `START_HERE.md` (or `START_HERE.txt`). Rebuild the pack with `python scripts/pack_download.py` (writes `/tmp/metrotel-pulse-site` plus the zip).

You can use it in three ways:

1. **Open the HTML prototype now** (this folder). Sample MetroTel data is already embedded.
2. **Drop in your own zone KPI CSV** — same layout, your numbers.
3. **Publish to ArcGIS Online** with the Python script, then finish the widgets in ArcGIS Dashboards (or embed the HTML page).

```
index.html          ← open this (visual template)
assets/             ← theme, charts, map, embedded sample data
data/               ← CSV + GeoJSON you can replace
scripts/            ← build embed file + publish to AGOL
agol/               ← field map + native Dashboards rebuild recipe
tests/              ← KPI totals that the header must show
```

## What the screen is for

One sentence: **commercial and RF staff need to know where subscribers, ARPU, churn, and 4G gaps sit, by district, so they can defend, expand, or fix QoS.**

| KPI | How it is calculated | Why it is on the header |
|---|---|---|
| Subscribers | Sum of `SUBSCRIBERS` | Market volume |
| ARPU | Subscriber-weighted `AVG_ARPU` | Where the money is (not a simple district average) |
| Churn risk | Subscriber-weighted `AVG_CHURN` | At-risk clusters from Lab 3 |
| P1 expand | Count of `PRIORITY` starting with `P1` | Lab 4 suitability → sales/site list |
| 4G coverage | Population-weighted `COV_4G_PCT` | Day 2 coverage vs Day 3 demand |
| Open actions | Decisions not `Approved` | Capstone tracking |

Click a **zone on the map** or a **decision row** to isolate that district. Header filters (zone / priority / fiber) drive every widget. That is the same action model ArcGIS Dashboards uses.

## Path A — Preview locally (no ArcGIS login)

```bash
cd GIS_Telecom_Training/Dashboards/MetroTel_Pulse
python scripts/build_embedded_data.py   # already run in this package
python -m http.server 8765
```

Open [http://localhost:8765](http://localhost:8765).

### Load your data

Keep these column names (see `agol/field_map.json`):

`DIST_ID, DIST_NAME, SUBSCRIBERS, AVG_ARPU, AVG_CHURN, COV_4G_PCT, PRIORITY, POPULATION, FIBER_STATUS`

Then either:

- Click **Load my CSV**, or
- Drag the CSV onto the page.

The map polygons stay as Capital Region sample geometry until you replace `data/MarketingZones.geojson` and re-run `build_embedded_data.py`. For a different city, put your polygons in that GeoJSON with a `DIST_ID` property that matches the CSV.

## Path B — Publish layers + web map + dashboard item to ArcGIS Online

```bash
pip install arcgis pandas
python scripts/publish_to_agol.py --dry-run          # validates files, writes placeholder JSON
python scripts/publish_to_agol.py --user YOUR_USER   # prompts / uses GIS()
# or
python scripts/publish_to_agol.py --profile home
```

The script publishes:

| Item | Source |
|---|---|
| MetroTel Pulse Zones | GeoJSON polygons **joined** to zone KPIs |
| MetroTel Pulse Cell Sites | XY from `Capstone_CellSites.csv` |
| MetroTel Pulse Competitors | XY from `CompetitorSites.csv` |
| MetroTel Pulse Subscribers | XY from `Subscribers_with_XY.csv` (skip with `--skip-subscribers`) |
| MetroTel Pulse Monthly KPI | table |
| MetroTel Pulse Decisions | table |
| MetroTel Pulse Web Map | zones + sites |
| MetroTel Pulse Dashboard | dark layout, six indicators, map, pie, ARPU bar chart |

After it prints the dashboard URL:

1. Open the item in **ArcGIS Dashboards**.
2. Click **Save** once so AGOL upgrades the JSON.
3. If a widget says *Data source error*, set its layer to **MetroTel Pulse Zones**.
4. Add header **category selectors** on `DIST_NAME` and `PRIORITY` (actions are listed in `agol/NATIVE_DASHBOARD.md`).

Native JSON is a template. Esri’s editor is the authority — always save once in the UI.

### Swap in your hosted layers later

Once you like the layout, point it at production layers without rebuilding widgets:

```python
from arcgis.gis import GIS
from arcgis.apps.dashboards import DashboardManager, ItemMapping

gis = GIS("home")
mgr = DashboardManager(item="YOUR_DASHBOARD_ITEM_ID", gis=gis)
mgr.copy(
    title="MetroTel Pulse — Production",
    item_mapping=[
        ItemMapping(
            sourceItemId="TEMPLATE_ZONES_ITEM_ID",
            targetItemId="YOUR_ZONES_ITEM_ID",
        )
    ],
)
```

Requires ArcGIS API for Python **2.4.3+** (`arcgis.apps.dashboards`). Field names should match `agol/field_map.json`. If they differ, pass `FieldMapping` objects (dashboard version 4.30.0+).

You can also paste JSON in [ArcGIS Assistant](https://assistant.esri-ps.com/) and replace `itemId` values.

## Path C — Embed the HTML design inside ArcGIS Dashboards

1. Host this folder on HTTPS (GitHub Pages, intranet, or a Hub site).
2. New dashboard → add **Embedded content** → that URL.
3. Optionally keep a native map widget beside it for ArcGIS pop-ups and bookmarks.

This is the fastest way to keep the custom visual design.

## Sample numbers (seeded MetroTel training data)

These are what the header should show with the CSV in `data/` (all zones):

- **526** subscribers  
- **~$32.0** weighted ARPU  
- **~29%** weighted churn risk  
- **3** P1-Expand zones (West Expansion, New Town, Tech Park)  
- **Peri-Urban North (DZ-12)** is P3-FixQoS — the coverage/churn story from Lab 3  

`python -m unittest tests/test_kpis.py` locks those totals.

## Design notes

- Dark operations theme (readable on a NOC wall and in a board pack).
- Priority colors are shared by the choropleth, pie, and ARPU bars so the eye does not learn two legends.
- Hexagon mark is a nod to tessellation / H3 work; it is branding, not a hex analysis layer.
- Weighted ARPU/churn avoids the trap of averaging 12 district means as if Tech Park (30 subs) and CBD (69) were equal.

Replace the sample rows — do not put live customer names, MSISDNs, or precise home addresses in a public dashboard. The training `CUSTOMER_NAME` field is synthetic.
