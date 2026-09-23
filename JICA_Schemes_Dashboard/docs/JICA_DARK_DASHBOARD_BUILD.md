# JICA irrigation + watershed dashboard (dark Pulse template)

**Join is done — continue here:** [`AFTER_JOIN_BUILD.md`](AFTER_JOIN_BUILD.md)

Full upload path (if you need to start over): [`UPLOAD_AND_VISUALIZE.md`](UPLOAD_AND_VISUALIZE.md)

Build this in **ArcGIS Dashboards** using the same dark MetroTel Pulse look. Your table is scheme-level. Your GIS has **points, lines, and polygons** that already store `Scheme_UID`, `Pair_ID`, `Program`, `Feature_Role`, `Feature_Name`, and `Asset_Name`.

Clean attribute table: `data/schemes_dashboard.csv` (14 rows: 7 Irrigation + 7 Watershed). GIS attribute checklists: `data/JICA_*_attributes.csv`.

---

## Architecture (do this or KPIs will be wrong)

| Layer | Geometry | What it is for |
| --- | --- | --- |
| `JICA_Schemes` | **Table or 14 points** | All **indicators, charts, selectors, lists** (one row per scheme) |
| `JICA_Areas` | Polygon | Command area + catchment on the map |
| `JICA_Lines` | Polyline | Canal alignment + WSM/check-dam lines on the map |
| `JICA_Points` | Point | Structures on the map |

Join `schemes_dashboard.csv` onto all three feature classes on **`Scheme_UID`**.

Do **not** sum `COST_USD` on `JICA_Points`. One scheme can have many structures, so the cost would be counted many times. KPIs always use `JICA_Schemes` (14 rows).

---

## Feature_Role values (on the cleaned GIS)

| Feature_Role | Geometry | Typical program |
| --- | --- | --- |
| `Command_Area` | polygon | Irrigation |
| `Incremental_Area` | polygon | Irrigation |
| `Catchment` | polygon | Watershed |
| `Canal` | line | Irrigation |
| `Riverbank` | line | Irrigation or Watershed |
| `Intake` | point | Irrigation |
| `Check_Dam` | point | Watershed |
| `Pond` | point | Watershed |
| `Social_Structure` / `Footpath` / `Spillway` / `Culvert` | point | Irrigation |

Keep `Feature_Name` and `Asset_Name` on the GIS. Do not explode them onto extra KPI rows.

---

## Pulse dark colors (copy these)

Dashboard **Theme → Dark**, then override:

| Use | Hex |
| --- | --- |
| Background | `#070B14` |
| Panel / header | `#121B2C` |
| Text | `#E8EEF7` |
| Muted labels | `#8B9BB4` |
| Irrigation (teal) | `#2EE6D6` |
| Watershed (gold) | `#F5C15A` |
| Awarded / OK | `#3DDC97` |
| Not awarded | `#FF5C7A` |
| Accent / links | `#5B8CFF` |

Map symbols must use the **same** teal and gold.

---

# Part A — Prepare GIS and join (ArcGIS Pro)

## A1. Three feature classes, one geodatabase

`JICA_Schemes.gdb`

- `JICA_Areas` (polygon)
- `JICA_Lines` (polyline)
- `JICA_Points` (point)

On every feature, these five fields must exist and match the CSV:

`Scheme_UID`, `Pair_ID`, `Program`, `Feature_Role`, `Feature_Name`, `Asset_Name`

`Scheme_UID` examples: `JICA-IS-01` … `JICA-IS-07`, `JICA-WSM-01` … `JICA-WSM-07`  
`Pair_ID` examples: `SITE-01` … `SITE-07` (IS and WSM at the same site share one Pair_ID)

## A2. Load geometry

Use **Append** into the three layers. Then **Calculate Field** if `Scheme_UID` / `Feature_Role` are missing.

## A3. Join the cleaned CSV

1. Add `schemes_dashboard.csv` to the map (table).
2. **Join Field** (or Add Join + Export):
   - Input: `JICA_Areas` / `JICA_Lines` / `JICA_Points`
   - Join table: `schemes_dashboard.csv`
   - Input join field = Join table field = **`Scheme_UID`**
3. Repeat for all three layers.

After join, each canal segment still has `Feature_Role = Canal` and `Feature_Name`, plus scheme fields (`STATUS`, `COST_USD`, `Province`, …).

## A4. Scheme KPI layer (14 features)

Create **one point per scheme** (scheme centroid or a representative structure):

- Copy unique `Scheme_UID` from the CSV, or
- **Dissolve** `JICA_Points` on `Scheme_UID` (do not use this for cost sums if dissolve keeps multipart junk — better: XY event layer from CSV `LON`/`LAT`).

Name it `JICA_Schemes`. This is the **only** layer for dashboard indicators.

Fix `JICA-WSM-03` coordinates before using CSV XY: current `Longitude` in the raw file is invalid (`34.42`, a latitude). Use the catchment polygon centroid instead.

## A5. Symbolize and publish

**Map Viewer or Pro symbology**

- Areas: unique values `Program` — Irrigation `#2EE6D6` fill 30% transparent, Watershed `#F5C15A` fill 30%
- Lines: unique values `Program` — same colors, thicker line
- Points: unique values `Feature_Role` or `Program`
- Optional definition queries: none at first (dashboard selectors will filter)

**Pop-up**

```
{Scheme_Name}
{Program} · {STATUS}
{Feature_Role}: {Feature_Name}
Cost: {COST_USD} USD
Area: {AREA_HA} ha
```

**Save web map:** `JICA IS WSM Schemes (Pulse)`  
Basemap: dark (Human Geography Dark or Imagery Hybrid).

Share as hosted feature layers + the web map.

Turn **Show in map legend** on for the three operational layers, then save. In the dashboard, add **Map legend** as a **panel** (not only the map-tool button) so it stays visible.

---

# Part B — Create the dark dashboard

## B1. Shell

1. Open the web map → **Create app → Dashboards**.
2. Title: `JICA Irrigation and Watershed Schemes`.
3. **Theme → Dark**. Set background `#070B14`, element/header `#121B2C`, text `#E8EEF7`.
4. **View → Header → Add header**
   - Title: `JICA Irrigation & Watershed`
   - Subtitle: `14 schemes · 7 sites · IS + WSM`
   - Logo optional
5. **Add element → Map** → this web map.
   - Tools: search, layer visibility, home, pop-ups **on**.
   - Legend **tool** optional; prefer a **Map legend** element docked beside the map (always on).
6. **Add element → Map legend** → choose this map → dock left or right of the map.

## B2. Layout (Pulse pattern)

```
HEADER: title + selectors (Program, Status, Province, Pair)
+------------------------------------------------------------------+
| KPI row: Schemes | Awarded | Progress | Cost | Area | HH | Canal km |
+---------------------------+--------------------------------------+
| MAP  (~58%)               | Pie: Program                         |
| areas + lines + points    | Bar: awarded cost by province        |
| + always-on Map legend    | List: schemes (click to zoom)        |
+---------------------------+--------------------------------------+
```

---

# Part C — Indicators (use `JICA_Schemes` only)

**Add element → Indicator**, seven times. Data source = `JICA_Schemes`.

| Tile | Statistic | Field | Filter | Value color |
| --- | --- | --- | --- | --- |
| Schemes | Count | `Scheme_UID` | none | `#E8EEF7` |
| Awarded | Count | `Scheme_UID` | `STATUS` = Awarded | `#3DDC97` |
| Awarded progress | Average | `PROGRESS_PCT` | `STATUS` = Awarded | `#3DDC97` |
| Awarded cost | Sum | `COST_USD` | `STATUS` = Awarded | `#F5C15A` |
| Area | Sum | `AREA_HA` | none | `#2EE6D6` |
| Households | Sum | `HOUSEHOLDS` | `Program` = Irrigation | `#5B8CFF` |
| Canal km | Sum | `CANAL_KM` | `Program` = Irrigation | `#2EE6D6` |

**Households:** Irrigation and Watershed at the same `Pair_ID` often list the same villages. Sum **Irrigation only** so you do not double-count. (SITE-01 is 630 on both rows.)

**Cost:** empty on Not Awarded rows — leave blank in the table, do not use `0`.

Number format: grouping on, 0 decimals, `$` prefix on cost.

Indicator layout: top = label (muted `#8B9BB4`), middle = `{value}` large, bottom = short unit (`schemes`, `USD`, `ha`, `km`).

Expected totals from this CSV (after selectors = All):

- 14 schemes
- 9 awarded / 5 not awarded
- Awarded progress **27.7%** (average of the 9 awarded `%` values)
- Awarded cost **2,294,514** USD

---

# Part D — Charts and list

## Pie — Program mix

- Layer: `JICA_Schemes`
- Categories from **Grouped values** → `Program`
- Count
- Colors: Irrigation `#2EE6D6`, Watershed `#F5C15A`
- Legend on

## Bar — Awarded cost by province

- Layer: `JICA_Schemes`
- Grouped values → `Province`
- Sum `COST_USD`
- Data filter: `STATUS` = Awarded
- Horizontal bars, gold `#F5C15A`
- Title: `Awarded cost by province`

## List — Schemes

- Layer: `JICA_Schemes`
- Sort: `Scheme_UID`
- Line 1: `{Scheme_Name}`
- Line 2: `{Program} · {STATUS} · {Province}`
- Caption: `Select a scheme to zoom the map`
- Actions on selection:
  - **Filter** `JICA_Areas`, `JICA_Lines`, `JICA_Points` by `Scheme_UID`
  - **Zoom** the map
  - **Flash** the map

Zoom goes to the **union** of that scheme’s polygon + line + points, not the CSV centroid.

---

# Part E — Header selectors (Pulse-style filters)

**View → Header → Add selector → Category selector** (four times).

All four: **Grouped values**, **Multiple** selection, **Allow none** (first view = all).

| Caption | Field | Categories from | Actions |
| --- | --- | --- | --- |
| Program | `Program` | Grouped values | Filter `JICA_Schemes` + three map layers + all widgets |
| Status | `STATUS` | Grouped values | same |
| Province | `Province` | Grouped values | same |
| Site | `Pair_ID` | Grouped values | Filter all + **Zoom** map (shows IS + WSM at one site) |

If a map layer uses `Scheme_UID` and the selector is `Pair_ID`, add a **field map** only when names differ. Here names match — no field map needed.

Do **not** use **Features** for Program/Status (those are repeated values). Use **Features** only if you later add a true county/site polygon picker.

**Defined values** is optional for a button bar: `All` / `Awarded` / `Not Awarded`. Grouped values on `STATUS` is simpler.

---

# Part F — Actions (dashboard, not a poster)

| Source | Action | Target |
| --- | --- | --- |
| Program / Status / Province selectors | Filter | KPI layer + areas + lines + points + charts + list |
| Pair_ID selector | Filter + Zoom | Both IS and WSM at that site |
| Scheme list | Filter + Zoom + Flash | Three geometry layers |
| Pie slice | Filter | Map + KPIs |
| Map extent (optional) | Filter by geometry | KPIs/charts if you want “what is on screen” |

---

# Part G — Splash welcome (optional)

**View → Settings → Splash screen → Add**

Title: `JICA Irrigation & Watershed`  
Body: schemes vs sites, teal = irrigation, gold = watershed, use header filters, click a list row to zoom.

Add a header **information window** with the same text so users can reopen it.

---

# Key points (read before you click)

1. **Join on `Scheme_UID`**. `Pair_ID` groups the irrigation + watershed pair at one site.
2. **KPIs from 14 scheme rows**, never from exploded structures.
3. **Empty cost** for Not Awarded, not zero.
4. **Households:** sum Irrigation only (or max per `Pair_ID`).
5. **Dark theme first**, then widgets. Recoloring later is slow.
6. **Same teal/gold** on map, pie, and indicators.
7. **Legend stays on** = Map legend **element**, docked; the map-tool button does not stay open.
8. **WSM-03 XY is bad** in the raw file — take centroid from the catchment polygon.
9. WSM rows had empty `Site_Number`; the clean table fills `Pair_ID` as `SITE-01` … `SITE-07`.
10. Share the **hosted layers + web map + dashboard** together.

---

# Click path (one sitting)

1. Clean/join data → three geometry layers + `JICA_Schemes`.
2. Dark web map, legend visible in Map Viewer, save.
3. Create dashboard from the map, set Pulse dark colors, add header.
4. Add map + Map legend panel.
5. Add seven indicators on `JICA_Schemes` (include Awarded progress).
6. Add pie, bar, scheme list.
7. Add four header selectors; wire Filter / Zoom / Flash.
8. Splash screen; save; test Program, Status, list click, and a Pair_ID site zoom.
