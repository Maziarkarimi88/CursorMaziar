# After the join — publish and build the Pulse dashboard

You already joined the updated scheme table onto **canals, coverage, and structures**. Start here. Do not join again.

The new column is **physical progress on awarded schemes**. The dashboard now has **seven** KPI tiles. The seventh is **Awarded progress** (average `%` of the 9 awarded rows).

Open `design/pulse-jica-preview.html` to see the dark layout.

---

## You are here

```
[done] Clean GDB geometry
[done] Join scheme table → Areas / Lines / Points
[ next ] Verify the join (field names + numeric cost/progress)
[ next ] Add a 14-row KPI source (do not chart the exploded GIS)
[ next ] Pulse symbology + pop-ups
[ next ] Publish → web map → dashboard (7 KPIs)
```

KPIs still **cannot** use canals, catchments, or structures. One scheme has many features, so a sum of cost or an average of progress on those layers is wrong (schemes with more features would dominate the average).

---

## Field names (raw join vs clean KPI table)

The attached table used Excel-style names. After Join Field, open each GIS attribute table and note the **exact** names Pro created. Use this map when you pick fields in Dashboards.

| Meaning | Name on the attached table | Name on `schemes_dashboard.csv` / `JICA_Schemes` |
| --- | --- | --- |
| Scheme id | `UNID` | `Scheme_UID` |
| Site pair | `Site_Number` | `Pair_ID` |
| Award status | `Awarding_Status` | `STATUS` |
| Progress % | `Physical_Progress_Percentage` | `PROGRESS_PCT` |
| Cost | `Contract_Cost_USD` | `COST_USD` |
| Area ha | `Intervention_Area (Ha)` → often `Intervention_Area__Ha_` | `AREA_HA` |
| Households | `Households` | `HOUSEHOLDS` |
| Canal km | `Canal_Length_Km` | `CANAL_KM` |
| Contractor | `Construction_Company` | `CONTRACTOR` |
| Start / end | `Contract_Signed_date` / `Contract_End_Date` | `CONTRACT_START` / `CONTRACT_END` |
| Lon / lat | `Longitude` / `Latitude` | `LON` / `LAT` |

GIS layers already had `Scheme_UID`, `Pair_ID`, `Program`, `Feature_Role`, `Feature_Name`, `Asset_Name`. Keep those. If the join created `UNID` plus `Scheme_UID`, that is fine — they should match.

**Program** is not on the attached table. It stays on the GIS (`Irrigation` / `Watershed`). The clean 14-row file derives it from `JICA-IS-*` vs `JICA-WSM-*`.

---

# Step A — Verify the join (5 minutes)

On **Areas, Lines, and Points**:

1. Attribute table → confirm **14 unique** `Scheme_UID` (or `UNID`) values.
2. `Physical_Progress_Percentage` (or `PROGRESS_PCT`) is **numeric**, not text. Awarded rows: 13, 19, 15, 27, 39, 5, 85, 45, 1. Not Awarded is **blank**, not `0`.
3. Cost is **numeric with no commas**. If you see `428,787` as text, add a new Double field and Calculate: `ToNumber(Replace($feature.Contract_Cost_USD, ',', ''))` (Arcade). Name it `COST_USD`.
4. Delete accidental `*_1` duplicates from the join.
5. `JICA-WSM-03` longitude in the attached file is **34.425989** (a latitude). Do not XY-event that row until you replace it with the catchment centroid (or use IS-03 `63.233673, 34.355257` as a temporary site point).

If cost or progress is still text, fix it **before** publishing. Dashboards cannot average a text field.

---

# Step B — Add the 14-row KPI source

Use `data/schemes_dashboard.csv` (progress already cleaned, commas removed, dates ISO).

**Option 1 — hosted table (fastest after a GIS-only join)**

1. ArcGIS Online → **Content → New item → Your device** → `schemes_dashboard.csv` → **Table**.
2. Title: `JICA_Schemes`.
3. This table is the data source for every indicator, chart, selector, and list.

**Option 2 — 14 points (if you want scheme centroids on the map)**

1. Pro: **XY Table To Point** on `schemes_dashboard.csv` (`LON` / `LAT`, WGS 1984) → `JICA_Schemes`.
2. Fix `JICA-WSM-03` XY (Step A.5).
3. Leave the layer in the web map but **unchecked** so it does not clutter the map.

Do **not** dissolve canals or structures to make this layer.

---

# Step C — Pulse symbology and pop-ups

**Draw order (bottom → top):** Areas → Lines → Points. `JICA_Schemes` hidden.

### Colors

| Feature_Role | Color | Notes |
| --- | --- | --- |
| `Command_Area` | `#2EE6D6` fill, 70% transparent | |
| `Incremental_Area` | `#2EE6D6` fill, 88% transparent | |
| `Catchment` | `#F5C15A` fill, 70% transparent | |
| `Canal` | `#2EE6D6` line, 2.5 pt | |
| `Riverbank` | `#5B8CFF` line, 2 pt | |
| `Intake` | `#2EE6D6` circle | |
| `Check_Dam` | `#F5C15A` square | |
| `Pond` | `#5B8CFF` circle | |
| `Spillway` | `#5B8CFF` triangle | |
| Other structures | `#8B9BB4` | |

Basemap: **Human Geography Dark** or **Dark Gray Canvas**. **Show in map legend** = on for the three GIS layers.

### Pop-up

Title: `{Feature_Name}`

```
{Scheme_Name}
{Program} · {Awarding_Status} · {Asset_Name}
Progress: {Physical_Progress_Percentage}%
Role: {Feature_Role}
Site: {Pair_ID} · {Scheme_UID}
```

If you joined the clean CSV instead, use `{STATUS}` and `{PROGRESS_PCT}`.

---

# Step D — Publish / update the service

If the three GIS layers are **not** hosted yet:

1. **Share → Web Layer** → `JICA_IS_WSM_Schemes` (Feature).
2. Include Areas, Lines, Points, and `JICA_Schemes` if you created points.
3. Also share the 14-row table if you used Option 1.

If the GIS is **already** hosted: overwrite / append is not required for attributes you already joined in Pro — **overwrite the feature layer** from Pro so AGOL gets `Physical_Progress_Percentage`. Then add `JICA_Schemes` (table or points) as a new item if it is not in the service.

Share the layer, the table, and (next) the map to the **same** group.

---

# Step E — Web map

1. Open the hosted GIS in **Map Viewer**.
2. Re-apply Pulse colors if publishing reset them.
3. Add `JICA_Schemes` (table does not draw; points stay unchecked).
4. Save: `JICA IS WSM Schemes (Pulse)`.
5. Share like the layer.

---

# Step F — Dashboard shell (Pulse dark)

1. Map → **Create app → Dashboards**.
2. Title: `JICA Irrigation and Watershed Schemes`.
3. **Theme → Dark** first:
   - Background `#070B14`
   - Element `#121B2C`
   - Text `#E8EEF7`
   - Selection `#5B8CFF`
4. **Header:** `JICA Irrigation & Watershed` / `14 schemes · 7 sites · IS + WSM`.

---

# Step G — Map + always-on legend

1. **Add element → Map** → this web map. Tools: search, layer visibility, home, pop-ups.
2. **Add element → Map legend** → dock on the map (left or bottom of the map card). Do not rely on the map Legend **tool** — it does not stay open.
3. Map ≈ 58% width, left, under the KPI row.

---

# Step H — Seven KPI indicators (`JICA_Schemes` only)

**Add element → Indicator**, seven times. Data source = the **14-row** table or points — never Areas / Lines / Points.

| Tile | Statistic | Field | Filter | Color |
| --- | --- | --- | --- | --- |
| Schemes | Count | `Scheme_UID` | none | `#E8EEF7` |
| Awarded | Count | `Scheme_UID` | `STATUS` = Awarded | `#3DDC97` |
| **Awarded progress** | **Average** | **`PROGRESS_PCT`** | **`STATUS` = Awarded** | **`#3DDC97`** |
| Awarded cost | Sum | `COST_USD` | `STATUS` = Awarded | `#F5C15A` |
| Area | Sum | `AREA_HA` | none | `#2EE6D6` |
| Households | Sum | `HOUSEHOLDS` | `Program` = Irrigation | `#5B8CFF` |
| Canal km | Sum | `CANAL_KM` | `Program` = Irrigation | `#2EE6D6` |

If the 14-row item still has raw names, use `UNID`, `Awarding_Status`, `Physical_Progress_Percentage`, `Contract_Cost_USD`, `Households`, `Canal_Length_Km`. For area, pick the sanitized `Intervention_Area*` field. `Program` must exist on the KPI source (it does on the clean CSV).

### Awarded progress — exact clicks

1. Indicator → Data → layer `JICA_Schemes`.
2. Value type: **Statistic**.
3. Statistic: **Average**.
4. Field: `PROGRESS_PCT` (or `Physical_Progress_Percentage`).
5. **Filter → Add filter:** `STATUS` / `Awarding_Status` **equal** `Awarded`.
6. Value format: 1 decimal, suffix ` %` (space + percent).
7. Optional reference: **Fixed value 100** so the tile reads like a target.
8. Title: `Awarded progress`. Bottom text: `average of 9 awarded schemes`.

Do **not** sum progress. Do **not** average on the GIS layers. Do **not** include Not Awarded (blank or 0 would drag the average down).

Dock all **seven** tiles in **one row** under the header, equal widths.

### Unfiltered totals you must see

| Tile | Value |
| --- | --- |
| Schemes | **14** |
| Awarded | **9** |
| Awarded progress | **27.7%** |
| Awarded cost | **$2,294,514** |
| Area | **12,225** ha |
| Households | **15,887** |
| Canal km | **97.3** |

Progress by program (for later filters): Irrigation awarded average **19.7%** (13, 19, 15, 27, 39, 5). Watershed awarded average **43.7%** (85, 45, 1).

If progress shows ~20% or a strange number, the indicator is averaging **features**, not 14 scheme rows. Switch the data source to `JICA_Schemes`.

---

# Step I — Charts and list

Right column, stacked.

## Pie — Program mix

- `JICA_Schemes` → Grouped values → `Program` → Count.
- Irrigation `#2EE6D6`, Watershed `#F5C15A`.

## Bar — Awarded cost by province

- Grouped values → `Province` → Sum `COST_USD`.
- Filter `STATUS` = Awarded. Color `#F5C15A`.
- Bars (USD): Herat 778,395 · Bamyan 479,862 · Ghazni 400,087 · Faryab 236,870 · Baghlan 229,571 · Maidan Wardak 169,729.

## Bar — Awarded progress by scheme (new)

1. **Serial chart** → `JICA_Schemes`.
2. Categories from **Features** (or Grouped values → `Scheme_UID`).
3. Series: **Average** (or Maximum — same on one row) `PROGRESS_PCT`.
4. Filter: `STATUS` = Awarded.
5. Horizontal bars, color `#3DDC97`.
6. Category labels: `{Scheme_Name}` or `{Scheme_UID}`.
7. Title: `Awarded progress by scheme`.

Expected order if sorted descending: WSM-01 85 · WSM-02 45 · IS-06 39 · IS-04 27 · IS-02 19 · IS-03 15 · IS-01 13 · IS-07 5 · WSM-03 1.

## List — Schemes

- Sort `Scheme_UID`.
- Line 1: `{Scheme_Name}`
- Line 2: `{Program} · {STATUS} · {PROGRESS_PCT}%`
- Line 3: `{Province} · {Pair_ID}`
- Awarded `#3DDC97`, Not Awarded `#FF5C7A`. Blank progress on Not Awarded is correct.
- Actions: Filter Areas + Lines + Points by `Scheme_UID`; Zoom; Flash.

---

# Step J — Header selectors

**Category selector**, Grouped values, Multiple, allow none.

| Caption | Field on `JICA_Schemes` | Also filter GIS using |
| --- | --- | --- |
| Program | `Program` | `Program` |
| Status | `STATUS` | `Awarding_Status` or `STATUS` |
| Province | `Province` | `Province` |
| Site | `Pair_ID` | `Pair_ID` or `Site_Number` (+ Zoom) |
| Asset | `Asset_Name` (GIS) | `Asset_Name` (+ Zoom) |

Wire each selector to **`JICA_Schemes` + Areas + Lines + Points + every widget**. If a GIS field name differs, set a **field map** on that action.

Do not use **Features** for Program or Status.

---

# Step K — Splash, share, test

Splash body:

```
14 schemes at 7 sites. Teal is irrigation. Gold is watershed.

Awarded progress is the average % of the 9 awarded schemes
(not a sum, and not taken from canals or structures).

Use the header filters. Click a list row to zoom the map.
```

Share **GIS layer + JICA_Schemes table/points + web map + dashboard** together.

| Test | Pass |
| --- | --- |
| No filters | 14 · 9 · **27.7%** · $2,294,514 · 12,225 ha · 15,887 HH · 97.3 km |
| Program = Irrigation | progress **19.7%**, 7 schemes, HH and canal km unchanged, area 4,112 |
| Program = Watershed | progress **43.7%**, HH **0**, canal km **0**, cost $241,239 |
| Status = Not Awarded | 5 schemes, progress empty / no awarded rows, cost empty |
| Site = SITE-03 | IS-03 (15%) and WSM-03 (1%) |
| List click Shah Joy | map zooms; IS-04 shows 27% |
| Legend | stays visible on the map |

---

## What not to do

1. Do not add a second join.
2. Do not point any indicator at Areas / Lines / Points.
3. Do not **sum** `PROGRESS_PCT` (that would read 249%).
4. Do not fill Not Awarded progress or cost with `0`.
5. Do not average progress without the Awarded filter.
6. Do not XY-event WSM-03 at 34.4°E / 34.4°N.

---

## One-sitting path from here

1. Step A — field names, numeric cost/progress, WSM-03 XY.
2. Step B — add `JICA_Schemes` from `schemes_dashboard.csv`.
3. Step C — Pulse colors + pop-up with progress.
4. Step D–E — publish / overwrite, save the dark web map.
5. Step F–G — dashboard theme, map, Map legend element.
6. Step H — **seven** indicators, including Awarded progress = **27.7%**.
7. Step I–K — pie, two bars, list, selectors, splash, tests.
