# After the join — publish and build the Pulse dashboard

You already joined the updated scheme table onto **canals, coverage, and structures**. Start here. Do not join again.

`Physical_Progress_Percentage` is the **% of physical works completed on that one project**. Each of the 14 schemes is an **independent** awarded (or not-awarded) contract.

**Rule:** never total, average, or roll up progress across projects — not all 14, not all awarded, not all irrigation, not all watershed, not both projects at a site. SITE-01 irrigation 13% and SITE-01 watershed 85% stay **13** and **85**. They are not 49%.

The Physical works tile shows **only the project you click** in the list. With no row selected, the tile stays empty.

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
| Physical works % (per project) | `Physical_Progress_Percentage` | `PROGRESS_PCT` |
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
Physical works: {Physical_Progress_Percentage}%
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

# Step H — Six roll-up KPIs + one per-project Physical works tile

**Add element → Indicator**, six times, for numbers that **may** roll up. Data source = the **14-row** `JICA_Schemes` table or points — never Areas / Lines / Points.

| Tile | Statistic | Field | Filter | Color |
| --- | --- | --- | --- | --- |
| Schemes | Count | `Scheme_UID` | none | `#E8EEF7` |
| Awarded | Count | `Scheme_UID` | `STATUS` = Awarded | `#3DDC97` |
| Awarded cost | Sum | `COST_USD` | `STATUS` = Awarded | `#F5C15A` |
| Area | Sum | `AREA_HA` | none | `#2EE6D6` |
| Households | Sum | `HOUSEHOLDS` | `Program` = Irrigation | `#5B8CFF` |
| Canal km | Sum | `CANAL_KM` | `Program` = Irrigation | `#2EE6D6` |

If the 14-row item still has raw names, use `UNID`, `Awarding_Status`, `Contract_Cost_USD`, `Households`, `Canal_Length_Km`. For area, pick the sanitized `Intervention_Area*` field.

### Physical works KPI — selected project only

Add a **seventh** indicator. It is **not** a portfolio number. It shows `PROGRESS_PCT` for **one** `Scheme_UID` after the user clicks that row.

1. Indicator → Data → `JICA_Schemes`.
2. Value type: **Statistic**. Statistic: **Maximum** (or Average — same thing on a single row).
3. Field: `PROGRESS_PCT` / `Physical_Progress_Percentage`.
4. **Do not** add a data filter on Awarded that you then leave unfiltered across many rows.
5. Value format: 0 or 1 decimal, suffix ` %`.
6. Title: `Physical works`. Bottom text: `selected project only`.
7. Optional reference: fixed **100**.
8. Color `#3DDC97`. Empty / no-data when Not Awarded (blank field).

**Actions (required):**

- Scheme **list** → selection: **single**.
- List **Actions → Filter** this Physical works indicator by `Scheme_UID`.
- List option: **When no selection is made → Show empty / no features** (do **not** render all 14).
- **Do not** let Program, Status, Site, or Province selectors drive this indicator. Those filters would leave more than one project and the tile would start combining `%` values.

If you click Sorkh Joy Irrigation, the tile is **13%**. Click Sorkh Joy Watershed, it is **85%**. Never 49%, never 27.7%, never an irrigation-only total.

Dock the six roll-up tiles plus this seventh tile in **one row**.

### Unfiltered roll-up totals (no progress mix-in)

| Tile | Value |
| --- | --- |
| Schemes | **14** |
| Awarded | **9** |
| Physical works | **empty** until one list row is clicked |
| Awarded cost | **$2,294,514** |
| Area | **12,225** ha |
| Households | **15,887** |
| Canal km | **97.3** |

Independent physical works (use these only on that project’s row, bar, or selected KPI):

| Project | Physical works |
| --- | --- |
| JICA-IS-01 | 13% |
| JICA-IS-02 | 19% |
| JICA-IS-03 | 15% |
| JICA-IS-04 | 27% |
| JICA-IS-05 | blank (not awarded) |
| JICA-IS-06 | 39% |
| JICA-IS-07 | 5% |
| JICA-WSM-01 | 85% |
| JICA-WSM-02 | 45% |
| JICA-WSM-03 | 1% |
| JICA-WSM-04 … 07 | blank (not awarded) |

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

## Bar — Physical works, one bar per project

1. **Serial chart** → `JICA_Schemes`.
2. Categories from **Features** (not Grouped values). Category field: `Scheme_UID` or `{Scheme_Name}`.
3. Series: **Maximum** `PROGRESS_PCT` (one row per project, so this is that project’s value only).
4. Optional filter: `STATUS` = Awarded (hides blank Not Awarded bars). Or show all 14 and leave Not Awarded empty.
5. **Do not** group by `Program` or `Pair_ID`. **Do not** split-by if that would stack or average.
6. Color by `Program`: Irrigation `#2EE6D6`, Watershed `#F5C15A` (arcade / unique values on the series if available; otherwise one green `#3DDC97`).
7. Title: `Physical works by project`.
8. Sort descending by value or by `Scheme_UID`.

Expected independent bars: WSM-01 **85** · WSM-02 **45** · IS-06 **39** · IS-04 **27** · IS-02 **19** · IS-03 **15** · IS-01 **13** · IS-07 **5** · WSM-03 **1**.

Clicking a bar should not create a combined %. Optional: bar selection filters the list / map to that one `Scheme_UID`.

## List — One row per independent project

- Sort: `Scheme_UID` (or `Pair_ID` then `Scheme_UID` only to keep site pairs next to each other — still two separate rows).
- Line 1: `{Scheme_Name}`
- Line 2: `{Scheme_UID} · {Program} · physical works {PROGRESS_PCT}%`
- Line 3: `{STATUS} · {Pair_ID} · {Province}`
- Awarded `#3DDC97`, Not Awarded `#FF5C7A`. Blank % on Not Awarded.
- Selection: **single**.
- Actions: Filter Areas + Lines + Points by `Scheme_UID`; Zoom; Flash; **Filter the Physical works indicator** by `Scheme_UID`. When no selection, the progress indicator stays empty.

---

# Step J — Header selectors

**Category selector**, Grouped values, Multiple, allow none.

| Caption | Field on `JICA_Schemes` | Also filter GIS using |
| --- | --- | --- |
| Program | `Program` | `Program` |
| Status | `STATUS` | `Awarding_Status` or `STATUS` |
| Province | `Province` | `Province` |
| Site | `Pair_ID` | `Pair_ID` or `Site_Number` (+ Zoom). Filters the **map, list, and project bars** so you see that site’s projects as **separate rows**. Do **not** target the Physical works indicator |
| Asset | `Asset_Name` (GIS) | `Asset_Name` (+ Zoom) |

Wire Program / Status / Province / Site / Asset to **`JICA_Schemes` + Areas + Lines + Points + the six roll-up KPIs + pie + cost bar + project-progress chart + list**.

**Do not** connect those selectors to the Physical works indicator. Only the list (one `Scheme_UID`) may filter that tile.

Do not use **Features** for Program or Status.

---

# Step K — Splash, share, test

Splash body:

```
14 schemes at 7 sites. Teal is irrigation. Gold is watershed.

Physical works % belongs to one project only.
Click a list row to see that project's % in the green tile.
Do not add or average progress across projects, programs, or sites.
```

Share **GIS layer + JICA_Schemes table/points + web map + dashboard** together.

| Test | Pass |
| --- | --- |
| No filters, no list click | 14 · 9 · Physical works **empty** · $2,294,514 · 12,225 ha · 15,887 HH · 97.3 km |
| Program = Irrigation | 7 schemes; progress tile still empty until one IS row is clicked |
| Program = Watershed | 7 schemes; HH **0**, canal km **0**, cost $241,239; no WSM progress total |
| Site = SITE-01 | list shows IS-01 **13%** and WSM-01 **85%** as two rows; progress tile still empty |
| List click IS-01 | Physical works tile **13%**; map zooms to Sorkh Joy irrigation |
| List click WSM-01 | Physical works tile **85%** (not 49%) |
| List click Shah Joy IS-04 | Physical works tile **27%** |
| Legend | stays visible on the map |

---

## What not to do

1. Do not add a second join.
2. Do not point any indicator at Areas / Lines / Points.
3. Do not **sum or average** `PROGRESS_PCT` across more than one `Scheme_UID` (no 27.7%, no 19.7%, no 43.7%, no 49%).
4. Do not fill Not Awarded progress or cost with `0`.
5. Do not let Site / Program selectors drive the Physical works indicator.
6. Do not XY-event WSM-03 at 34.4°E / 34.4°N.

---

## One-sitting path from here

1. Step A — field names, numeric cost/progress, WSM-03 XY.
2. Step B — add `JICA_Schemes` from `schemes_dashboard.csv`.
3. Step C — Pulse colors + pop-up with progress.
4. Step D–E — publish / overwrite, save the dark web map.
5. Step F–G — dashboard theme, map, Map legend element.
6. Step H — six roll-up indicators + Physical works **selected project only**.
7. Step I–K — pie, cost bar, **one bar per project**, list click drives the progress tile, selectors (except progress tile), splash, tests.
