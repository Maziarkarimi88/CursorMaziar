# START HERE — MetroTel Pulse download pack

Unzip this folder on your computer. You do **not** need ArcGIS Online to open the dashboard.

## 1. Open the dashboard (2 minutes)

**Windows:** double-click `index.html`  
If the map is blank, the browser blocked local files. Use a tiny server instead:

```text
1. Open Command Prompt or Terminal in this folder
2. python -m http.server 8765
3. Open http://localhost:8765
```

**Mac / Linux:** same Python command, then open http://localhost:8765

You should see **526** subscribers, **$32.0** ARPU, colored districts on a dark map.

## 2. Put your own data in

Keep these column names (or rename yours):

```text
DIST_ID, DIST_NAME, SUBSCRIBERS, AVG_ARPU, AVG_CHURN, COV_4G_PCT, PRIORITY, POPULATION, FIBER_STATUS
```

Then either:

- Click **Load my CSV** on the dashboard, or
- Drag the CSV onto the page, or
- Replace files in `data/` and run:

```text
python scripts/build_embedded_data.py
```

For another city, replace `data/MarketingZones.geojson`. Each polygon needs a `DIST_ID` that matches the CSV.

Full field list: `agol/field_map.json`

## 3. Upload to ArcGIS Online

```text
pip install arcgis pandas
python scripts/publish_to_agol.py --dry-run
python scripts/publish_to_agol.py --user YOUR_AGOL_USER
```

That publishes hosted layers, a web map, and a Dashboard item. Open the dashboard in ArcGIS Dashboards and click **Save** once.

Native widget colors and actions: `agol/NATIVE_DASHBOARD.md`

## 4. What each folder is

| Path | What it is |
|---|---|
| `index.html` | The designed dashboard |
| `assets/` | CSS, JavaScript, sample data pack |
| `data/` | CSV + GeoJSON you can replace |
| `scripts/publish_to_agol.py` | Upload script |
| `scripts/build_embedded_data.py` | Rebuilds the sample data into the HTML |
| `agol/` | Field map + ArcGIS Dashboards recipe + JSON template |
| `tests/` | Checks that KPIs still equal 526 / 3 P1 zones |
| `README.md` | Full documentation |

## 5. Quick test

```text
python -m unittest tests.test_kpis
```

Must print `OK`.
