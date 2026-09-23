# Upload the cleaned JICA layers and build the Pulse dark dashboard

**Join already done?** Skip to [`AFTER_JOIN_BUILD.md`](AFTER_JOIN_BUILD.md).

Use this if you need to start over. The product is a **native ArcGIS Online Dashboard** that looks like MetroTel Pulse (dark navy panels, **seven** KPI tiles including physical works % (per project, also by site), map left, pie + bars + list right).

Open `design/pulse-jica-preview.html` in a browser to see the target layout. Open `design/metro-tel-pulse-reference.webp` to see the original Pulse template.

The GIS CSVs in this pack are **attribute checklists only**. They do not contain coordinates. Publish **from your geodatabase in ArcGIS Pro**. The 14-row `schemes_dashboard.csv` is the only file you upload as new features (scheme centroids for KPIs).

---

## Architecture (do this or every KPI is wrong)

| Layer | Geometry | Use for |
| --- | --- | --- |
| `JICA_Schemes` | 14 points from `schemes_dashboard.csv` | **All indicators, charts, selectors, lists** |
| `JICA_Areas` | polygons (command / incremental / catchment) | Map + legend only |
| `JICA_Lines` | polylines (canal / riverbank) | Map + legend only |
| `JICA_Points` | points (intake, check dam, pond, …) | Map + legend only |

Join extra scheme fields onto the three GIS layers on **`Scheme_UID`** if you want richer pop-ups. Never sum `COST_USD`, `HOUSEHOLDS`, or `CANAL_KM` on areas, lines, or structures — one scheme has many features.

**Households:** sum Irrigation only. IS and WSM at the same `Pair_ID` often list the same villages.

**Cost:** leave Not Awarded blank. Do not store `0`.

---

## Pulse dark colors (copy these)

Dashboard **Theme → Dark**, then override:

| Use | Hex |
| --- | --- |
| Background | `#070B14` |
| Panel / header | `#121B2C` |
| Text | `#E8EEF7` |
| Muted labels | `#8B9BB4` |
| Irrigation | `#2EE6D6` |
| Watershed | `#F5C15A` |
| Awarded / OK | `#3DDC97` |
| Not awarded | `#FF5C7A` |
| Accent / riverbank / households | `#5B8CFF` |

Use the **same** teal and gold on the map, pie, bars, and KPI numbers.

---

## Target layout (Pulse)

```
HEADER: JICA Irrigation & Watershed     [Program] [Status] [Province] [Site] [Asset]
+------------------------------------------------------------------------+
| Schemes | Awarded | Progress | Awarded cost | Area | Households | Canal km |
+----------------------------------+-------------------------------------+
| MAP (~58%)                       | Pie: Program mix                    |
| Areas + lines + points           | Bar: Awarded cost by province       |
| + always-on Map legend element   | List: schemes (click → zoom/flash)  |
+----------------------------------+-------------------------------------+
```

---

# Step 1 — Confirm the geodatabase (ArcGIS Pro)

Open the GDB you already cleaned. You should have three feature classes. Field names must match **exactly** (underscore, this spelling):

`Scheme_UID` · `Pair_ID` · `Program` · `Feature_Role` · `Feature_Name` · `Asset_Name`

Plus on lines: `Length_KM`. Plus on areas: `Area_HA`. Do **not** chart `Shape_Length` or `Shape_Area`.

### 1.1 Feature_Role values that should exist

| Layer | Feature_Role | Count in the cleaned export |
| --- | --- | --- |
| Lines | `Canal` | 11 |
| Lines | `Riverbank` | 4 |
| Areas | `Command_Area` | 11 |
| Areas | `Incremental_Area` | 5 |
| Areas | `Catchment` | 20 |
| Points | `Intake` | 11 |
| Points | `Check_Dam` | 17 |
| Points | `Social_Structure` | 3 |
| Points | `Footpath` | 3 |
| Points | `Spillway` | 2 |
| Points | `Culvert` | 1 |
| Points | `Pond` | 1 |

Compare attributes to the CSVs in `data/` if anything looks off. Geometry stays in the GDB.

### 1.2 SITE-03 reminder

- `JICA-IS-03`: both canals, command + incremental, Joi Ulya riverbanks, both intakes.
- `JICA-WSM-03`: Joi Ulya catchments / check dams / pond, plus Yarokhan riverbanks.
- `Pair_ID` `SITE-03` still filters **both** schemes.

### 1.3 Optional coded domain

Add a coded domain on `Feature_Role` only (the values in the table above). Do not put a domain on `Scheme_UID`.

---

# Step 2 — Add the 14-row scheme KPI layer

1. In Pro, **Catalog → right-click the GDB → Import → Table** (or Add Data) and add `data/schemes_dashboard.csv`.
2. **File → XY Table To Point**
   - X Field: `LON`
   - Y Field: `LAT`
   - Coordinate system: **WGS 1984** (`GCS_WGS_1984`)
   - Output: `JICA_Schemes`
3. `JICA-WSM-03` has a **blank `LON`** (the raw file stored a latitude in the longitude column). After areas are in the map:
   - Select the four `JICA-WSM-03` catchments.
   - **Calculate Geometry** centroid (or use the Joi Ulya pond/check-dam cluster).
   - Copy that X/Y onto the `JICA_Schemes` point for `JICA-WSM-03`.
   - Temporary fallback if you must publish now: use the IS-03 point `63.233673, 34.355257` (same site, Obe).

Confirm **14 points**. If you see 15, you imported the header as a row.

---

# Step 3 — Join scheme fields onto the map layers (pop-ups)

Do this on areas, lines, and points. KPIs still read `JICA_Schemes` only.

1. **Data Management → Join Field**
   - Input: `JICA_Areas` (then repeat for Lines and Points)
   - Input join field: `Scheme_UID`
   - Join table: `schemes_dashboard.csv` (or `JICA_Schemes`)
   - Join table field: `Scheme_UID`
   - Transfer: `STATUS`, `PROGRESS_PCT`, `Scheme_Name`, `COST_USD`, `AREA_HA`, `HOUSEHOLDS`, `CANAL_KM`, `Province`, `District`, `CONTRACTOR`
2. Do **not** transfer fields that already exist (`Program`, `Pair_ID`) unless you want `_1` duplicates. Delete any `*_1` fields if they appear.

---

# Step 4 — Pulse symbology in Pro (or later in Map Viewer)

**Draw order (bottom → top):** `JICA_Areas` → `JICA_Lines` → `JICA_Points`. Keep `JICA_Schemes` in the map but **unchecked** (data source for widgets, not map clutter).

### Areas — Unique values on `Feature_Role`

| Value | Fill | Outline | Transparency |
| --- | --- | --- | --- |
| `Command_Area` | `#2EE6D6` | `#2EE6D6` | 70% |
| `Incremental_Area` | `#2EE6D6` | `#2EE6D6` | 88% |
| `Catchment` | `#F5C15A` | `#F5C15A` | 70% |

### Lines — Unique values on `Feature_Role`

| Value | Color | Width |
| --- | --- | --- |
| `Canal` | `#2EE6D6` | 2.5 pt |
| `Riverbank` | `#5B8CFF` | 2 pt |

### Points — Unique values on `Feature_Role`

| Value | Color | Shape |
| --- | --- | --- |
| `Intake` | `#2EE6D6` | circle |
| `Check_Dam` | `#F5C15A` | square |
| `Pond` | `#5B8CFF` | circle |
| `Spillway` | `#5B8CFF` | triangle |
| `Social_Structure` | `#8B9BB4` | diamond |
| `Footpath` | `#8B9BB4` | small circle |
| `Culvert` | `#8B9BB4` | square |

Turn **Show in legend** on for all three operational layers.

### Pop-up (all three GIS layers)

Title: `{Feature_Name}`

```
{Scheme_Name}
{Program} · {STATUS} · {Asset_Name}
Role: {Feature_Role}
Site: {Pair_ID} · {Scheme_UID}
```

Optional last line on areas: `Area: {Area_HA} ha`. On lines: `Length: {Length_KM} km`.

### Basemap

**Human Geography Dark Map** or **Dark Gray Canvas**. Imagery Hybrid is acceptable if you need village context; keep panel colors Pulse-dark either way.

---

# Step 5 — Publish to ArcGIS Online

1. Sign in to the org that will own the dashboard.
2. **Share → Share As → Web Layer → Publish Web Layer**
   - Name: `JICA_IS_WSM_Schemes`
   - Layer type: **Feature**
   - Include all four layers (`JICA_Areas`, `JICA_Lines`, `JICA_Points`, `JICA_Schemes`)
   - Sharing: your group / org (add **Everyone** only if the dashboard is public)
3. Wait until the item shows **Published**.
4. Open the feature layer item → **Visualization** and confirm 14 scheme points, polygons, lines, and structures draw.

**Do not** publish the canal / coverage / structure CSVs as hosted layers. Those files have no shape.

Alternative if the GDB is already a hosted layer: skip republish. Add `schemes_dashboard.csv` as a hosted table or XY layer and join in Map Viewer (**Add → Add layer from file**, then **Join features** on `Scheme_UID`).

---

# Step 6 — Build the web map

1. From the hosted layer item: **Open in Map Viewer**.
2. Re-apply Pulse colors if publishing reset them (Step 4).
3. Layer list, top to bottom: Points, Lines, Areas, Schemes (Schemes visibility **off**).
4. Each operational layer → **Properties → Symbology → Options → Show in map legend** = on.
5. Save map title: `JICA IS WSM Schemes (Pulse)`
6. Share the **same** people as the hosted layer. The dashboard cannot see a private layer.

---

# Step 7 — Create the dashboard shell

1. In the web map: **Create app → Dashboards**.
2. Title: `JICA Irrigation and Watershed Schemes`
3. **Theme → Dark**
4. Theme colors:
   - Background `#070B14`
   - Element background `#121B2C`
   - Text `#E8EEF7`
   - Tab / selection `#5B8CFF`
5. **View → Header → Add header**
   - Title: `JICA Irrigation & Watershed`
   - Subtitle: `14 schemes · 7 sites · IS + WSM`
6. Save.

Set the theme **before** adding widgets. Recoloring later is slow.

---

# Step 8 — Map + always-on legend

1. **Add element → Map** → choose `JICA IS WSM Schemes (Pulse)`.
2. Map tools: **Search**, **Layer visibility**, **Home**, **Zoom in/out**, **Pop-ups** on.
3. You may leave the map’s Legend **tool** off. It is a button and does not stay open.
4. **Add element → Map legend** → this map.
5. Dock the Map legend as a **panel on the map** (left or bottom of the map card), not as a header button.
6. Size the map to about **58% width**, left side, under the KPI row.

If the legend is empty: the web map does not have “Show in map legend” on (Step 6). Fix the map, save, then refresh the dashboard.

---

# Step 9 — Seven KPI indicators (`JICA_Schemes` only)

**Add element → Indicator**, seven times. Data source = `JICA_Schemes` (the 14-point layer or table).

| Tile | Statistic | Field | Filter | Value color |
| --- | --- | --- | --- | --- |
| Schemes | Count | `Scheme_UID` | none | `#E8EEF7` |
| Awarded | Count | `Scheme_UID` | `STATUS` = `Awarded` | `#3DDC97` |
| Physical works | Average | `PROGRESS_PCT` | `STATUS` = `Awarded` | `#3DDC97` |
| Awarded cost | Sum | `COST_USD` | `STATUS` = `Awarded` | `#F5C15A` |
| Area | Sum | `AREA_HA` | none | `#2EE6D6` |
| Households | Sum | `HOUSEHOLDS` | `Program` = `Irrigation` | `#5B8CFF` |
| Canal km | Sum | `CANAL_KM` | `Program` = `Irrigation` | `#2EE6D6` |

**Value formatting**

- Schemes / Awarded: grouping on, 0 decimals
- Awarded cost: grouping on, 0 decimals, prefix `$`
- Area / Households: grouping on, 0 decimals
- Canal km: 1 decimal
- Physical works: 1 decimal, suffix ` %`

**Layout of each indicator:** top = title in `#8B9BB4`, middle = `{value}` large, bottom = unit (`schemes`, `%`, `USD`, `ha`, `HH`, `km`).

Dock all **seven** in **one row** under the header (~16% height), equal widths.

### Unfiltered totals you must see

| Tile | Value |
| --- | --- |
| Schemes | **14** |
| Awarded | **9** |
| Physical works | **27.7%** (site filter changes this) |
| Awarded cost | **$2,294,514** |
| Area | **12,225** ha |
| Households | **15,887** |
| Canal km | **97.3** |

If cost is many times larger, the indicator is pointed at structures or canals. Switch the data source to `JICA_Schemes`.

---

# Step 10 — Pie, bar, and scheme list

Dock these in a **right column** (~42% width), stacked.

## Pie — Program mix

1. **Add element → Pie chart**
2. Layer: `JICA_Schemes`
3. Categories from **Grouped values** → `Program`
4. Statistic: Count
5. Slices: Irrigation `#2EE6D6`, Watershed `#F5C15A`
6. Legend on
7. Title: `Program mix`

## Bar — Awarded cost by province

1. **Add element → Serial chart**
2. Layer: `JICA_Schemes`
3. Categories from **Grouped values** → `Province`
4. Series: Sum `COST_USD`
5. Filter: `STATUS` = `Awarded`
6. Horizontal or vertical bars, color `#F5C15A`
7. Title: `Awarded cost by province`

Expected bars (USD): Herat 778,395 · Bamyan 479,862 · Ghazni 400,087 · Faryab 236,870 · Baghlan 229,571 · Maidan Wardak 169,729. Zabul has no awarded cost.

## List — Schemes

1. **Add element → List**
2. Layer: `JICA_Schemes`
3. Sort: `Scheme_UID`
4. Line 1: `{Scheme_Name}`
5. Line 2: `{Pair_ID} · {Program} · physical works {PROGRESS_PCT}%`
6. Line 3 (optional): `{Province} · {Pair_ID}`
7. Advanced formatting: Awarded name `#3DDC97`, Not Awarded `#FF5C7A`
8. Caption: `Select a scheme to zoom the map`
9. Selection: single
10. **Actions**
    - Filter `JICA_Areas`, `JICA_Lines`, `JICA_Points` by `Scheme_UID`
    - Zoom the map
    - Flash the map

Zoom uses the **union** of that scheme’s polygons + lines + points, not the CSV centroid.

---

# Step 11 — Header selectors (Pulse filters)

**View → Header → Add selector → Category selector** five times.

All five: **Grouped values**, **Multiple** selection, **None option** on (first view = everything).

| Caption | Field | Actions |
| --- | --- | --- |
| Program | `Program` | Filter `JICA_Schemes` + Areas + Lines + Points + every KPI/chart/list |
| Status | `STATUS` | same |
| Province | `Province` | same |
| Site | `Pair_ID` | Filter all **and Zoom** the map (IS + WSM at one site) |
| Asset | `Asset_Name` | Filter all **and Zoom** (Yakawlang cluster, Joi Ulya vs Yarokhan, …) |

`Asset_Name` lives on the GIS layers. If it is missing on `JICA_Schemes`, either:

- Join / calculate it (Sorkh Joy, Shir Abad, Joi Ulya Bazar, Yar Mohammad Khan, Shah Joy, Shawaroz, Yakawlang, Ety Aregh), or
- Point the Asset selector at `JICA_Areas` and **field-map** filters to the other layers on `Asset_Name`.

`Province` is on the scheme table. If a map layer does not have `Province`, field-map that selector through `Scheme_UID` (filter schemes first, then filter geometries by the selected `Scheme_UID` values). The reliable pattern:

1. Selectors filter **`JICA_Schemes`**.
2. The scheme list (or a hidden indicator) **forwards** the selected `Scheme_UID` to Areas / Lines / Points.

Simpler pattern that works if you completed Step 3: every layer has `Program`, `STATUS`, `Province`, `Pair_ID`, `Scheme_UID`, `Asset_Name`. Then each selector can target all four layers directly. **Field names must match.** No field map needed.

Do **not** use **Features** for Program or Status. Those are repeated values. Use **Grouped values**.

---

# Step 12 — Extra actions, splash, share

### Pie slice

Actions → Filter `JICA_Schemes` + the three map layers (and the other widgets).

### Optional map extent

Map → Actions → Filter `JICA_Schemes` by geometry if you want KPIs to follow the visible extent. Skip this until the header filters feel right.

### Splash welcome

**View → Settings → Splash screen → Add**

Title: `JICA Irrigation & Watershed`

Body:

```
14 schemes at 7 sites. Teal is irrigation. Gold is watershed.

Use the header filters (Program, Status, Province, Site, Asset).
Click a row in the scheme list to zoom and flash the map.

Cost and household totals come from one row per scheme.
They are not summed from canals, catchments, or structures.
```

Add a header **information** window with the same text so users can reopen it.

### Share

Share **hosted feature layer + web map + dashboard** together (same group / org / public). If only the dashboard is public, the map goes blank.

---

# Step 13 — Click-test before you send the link

| Test | Pass |
| --- | --- |
| No filters | 14 · 9 · **27.7%** · $2,294,514 · 12,225 ha · 15,887 HH · 97.3 km |
| Program = Irrigation | 7 schemes, progress **19.7%**, households and canal km stay the same, area 4,112 |
| Program = Watershed | 7 schemes, progress **43.7%**, households **0**, canal km **0**, awarded cost $241,239 |
| Status = Not Awarded | 5 schemes, awarded cost $0 or empty |
| Site = SITE-03 | Map zooms to Obe; list shows IS-03 and WSM-03 |
| Asset = Yakawlang | IS-06 canals + intakes + WSM-06 dams |
| Asset = Joi Ulya Bazar | IS-03 Joi Ulya canal/area/intake + WSM-03 catchments/dams/pond |
| Click Shah Joy in the list | Map zooms, features flash, other schemes hide |
| Legend | Stays on the map; shows Canal, Catchment, Check_Dam, … |
| Public / group user (incognito) | Map and KPIs load (sharing aligned) |

---

## What not to do

1. Do not publish the three GIS CSVs as new feature layers.
2. Do not point indicators at `JICA_Points` or `JICA_Lines`.
3. Do not sum `HOUSEHOLDS` on both Irrigation and Watershed.
4. Do not fill Not Awarded `COST_USD` with `0`.
5. Do not use `Shape_Area` / `Shape_Length` on KPIs (`Area_HA`, `Length_KM`, `AREA_HA`, `CANAL_KM` only).
6. Do not rely on the map Legend **tool** for a permanently visible legend.
7. Do not leave `JICA-WSM-03` at 0,0 — it will zoom the map to the Gulf of Guinea.

---

## Files in this pack

| File | Role |
| --- | --- |
| `data/schemes_dashboard.csv` | 14 scheme rows — KPIs, charts, list, XY points |
| `data/JICA_Lines_attributes.csv` | Attribute checklist for canals / riverbanks (15 rows) |
| `data/JICA_Areas_attributes.csv` | Attribute checklist for areas (36 rows) |
| `data/JICA_Points_attributes.csv` | Attribute checklist for structures (38 rows) |
| `docs/pulse-theme.json` | Hex tokens + expected totals |
| `design/pulse-jica-preview.html` | Open locally — Pulse layout with these numbers |
| `design/metro-tel-pulse-reference.webp` | Original MetroTel Pulse screenshot |

---

## One-sitting click path

1. Confirm GDB fields and `Feature_Role` counts (Step 1).
2. XY-event `schemes_dashboard.csv` → `JICA_Schemes`; fix WSM-03 (Step 2).
3. Join Field on `Scheme_UID` (Step 3).
4. Pulse symbology + pop-ups (Step 4).
5. Publish one feature service with four layers (Step 5).
6. Dark web map, legend visible, save (Step 6).
7. Dashboard from the map → Theme Dark + Pulse hex + header (Step 7).
8. Map + Map legend panel (Step 8).
9. Seven indicators on `JICA_Schemes`, including Physical works (Step 9). Add a site chart split by Program.
10. Pie, bar, list (Step 10).
11. Five header selectors + Filter / Zoom / Flash (Step 11).
12. Splash, share all three items, run the test table (Steps 12–13).
