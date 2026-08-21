# How to Build Professional ArcGIS Online Dashboards

A step-by-step tutorial based on two public dashboards:

| Example | What it is | Live app |
| --- | --- | --- |
| **Program / conservation summary** | Audubon Society of Northern Virginia (ASNV) Wildlife Sanctuary Program | [Open dashboard](https://www.arcgis.com/apps/dashboards/96896859c42c4301a8032609493a9e00) |
| **Real-time operations** | California Governor’s Office of Emergency Services (Cal OES) statewide power outages | [Open dashboard](https://www.arcgis.com/apps/dashboards/7edefc1970d44b839ebbfd7b45e51e2d) |

These two apps look different, but they use the same ArcGIS Dashboards workflow. The professional result comes from **clean data**, a **well-authored web map**, a **deliberate layout**, and **actions that make every click useful**.

![ASNV Wildlife Sanctuary Program dashboard](images/asnv-wildlife-sanctuary-dashboard.png)

*ASNV: light theme, branded header, KPI indicators, tabbed charts, map in the center.*

![Cal OES California Statewide Power Outages dashboard](images/caloes-power-outages-dashboard.png)

*Cal OES: dark operations theme, live KPIs, county/utility filters, lists that zoom the map.*

---

## What you will build

You will not copy these organizations’ data. You will recreate **the same professional patterns** with your own hosted layers.

**Pattern A — Program summary (ASNV style)**

- Light branded theme
- Header with title plus global Year and Date selectors
- Four KPI indicators
- Center map with bookmarks, legend, layers, and search
- Side charts stacked into tabs so one screen holds six charts
- Map extent filters the charts (pan/zoom updates numbers)

**Pattern B — Live operations (Cal OES style)**

- Dark theme for 24/7 monitoring
- Header logo, subtitle, and filter selectors (place, organization, type)
- Large “total impact” number plus planned vs unplanned split
- Center map of current incidents
- Ranked bar charts (filter out noise, for example “500+ customers”)
- Lists that zoom and flash the map when a row is selected

You need an ArcGIS Online account with privileges to create content, hosted feature layers, web maps, and dashboards.

---

## The professional formula (read this first)

Both dashboards follow the same five-layer stack. Do not start in the dashboard editor until layers 1–3 are done.

1. **Question.** One sentence. ASNV: “How much certified habitat exists, where is it, and how has it grown?” Cal OES: “Who is without power right now, where, and is it planned?”
2. **Authoritative data.** Hosted feature layers (or hosted views) with coded fields, aliases, and a public-safe field set.
3. **Web map.** Basemap, symbology, definition queries, pop-ups, bookmarks, refresh interval. The map is the dashboard’s data engine.
4. **Layout.** Header + 3-column body. Big numbers at a glance. Detail on demand via tabs and lists.
5. **Actions.** Selectors, lists, and the map all filter or zoom each other. A dashboard that does not react feels like a poster.

---

## Part 1 — Design the information, not the widgets

### 1. Write a one-screen story

Sketch three zones on paper before you open ArcGIS:

| Zone | Job | ASNV | Cal OES |
| --- | --- | --- | --- |
| Header | Identity + global filters | Title, Year, Date | Logo, county, utility, outage type |
| Hero | Spatial context | Map of certified properties | Statewide outage map |
| KPIs | Answer in 2 seconds | Total acres, total properties, PADUS, IBAs | Customers out, planned vs not planned |
| Breakdown | Explain the KPI | Acres/count by year, county, city, type | Customers by utility and county |
| Roster | Take action | (charts replace lists) | County list + current outage list |

If a widget does not serve one of those jobs, leave it out.

### 2. Pick a visual language and stick to it

| | Program summary | Operations |
| --- | --- | --- |
| Theme | Light | Dark |
| Accent | One brand navy, for example `#004C73` | Amber/gold for impact, yellow for planned |
| Context color | Green for reference layers (protected areas, bird areas) | Neutral gray for “all”, colored for status |
| Basemap | Light Human Geography / canvas + hillshade | Dark or imagery hybrid so incident colors pop |
| Density | Tabs so six charts occupy two panels | Lists + charts always visible |

Cal OES uses **orange (`#E69800` / `#FFAA00`) for unplanned** and **yellow (`#FFFF00`) for planned** on the indicators, lists, and stacked bars. That consistency is what makes the dashboard feel official.

### 3. Decide what is “live” vs historical

- **Historical / program data (ASNV):** no refresh interval required. Filter by `Year` and `Close_Date`.
- **Live operations (Cal OES):** source data is updated about every 10–15 minutes. Set the layer refresh interval to match (30 seconds is the ArcGIS Online minimum; 5–15 minutes is usually enough and is kinder to the service).

---

## Part 2 — Prepare the data (this is 50% of a professional dashboard)

Dashboards only look as good as the table behind them.

### Step 1. Model fields the dashboard can group on

Minimum fields for a **site / property** layer (ASNV pattern):

| Field | Type | Why |
| --- | --- | --- |
| `Name` | Text | Pop-up and search |
| `Type` | Text (domain) | Pie chart + unique-value map |
| `Year` | Integer or text | Year selector + bar chart |
| `Close_Date` | Date | Date-range selector |
| `City` | Text | Top-10 chart |
| `County` or `Jurisdicti` | Text | County charts |
| `Acres` | Double | Sum indicators and charts |
| `MapVisibility` | Text | `Visible` vs hidden for public view |

Minimum fields for an **incident** layer (Cal OES pattern):

| Field | Type | Why |
| --- | --- | --- |
| `IncidentId` | Text | List line and pop-up title |
| `UtilityCompany` | Text (domain) | Selector + stacked bars |
| `County` | Text | Selector, list, chart, URL parameter |
| `OutageType` | Text | Planned / Not Planned color |
| `OutageStatus` | Text | Filter to `Active` only |
| `ImpactedCustomers` | Integer | Sum KPI |
| `Cause` | Text | List detail |
| `StartDate` | Date | List |
| `EstimatedRestoreDate` | Date | List |

Use **domains or a lookup list** so pie charts and selectors do not show `Fairfax`, `fairfax `, and `Fairfax County` as three categories.

### Step 2. Publish a hosted feature layer

1. In ArcGIS Online, go to **Content** > **New item** > **Your device** (or **Feature layer** from a template).
2. Upload a file geodatabase, shapefile, GeoJSON, or CSV with coordinates.
3. Enable **Publish this file as a hosted layer**.
4. After publishing, open the item > **Data** > **Fields**.
5. Set **aliases** (`Jurisdicti` → `County`, `ImpactedCustomers` → `Customers without power`). Aliases appear in lists and pop-ups.
6. Create **attribute indexes** on fields you will filter and group: `Year`, `County`, `UtilityCompany`, `OutageStatus`, `OutageType`.

### Step 3. Create a hosted feature layer view for the public

Both example dashboards use **public views**, not the editable source.

1. Open the hosted feature layer item.
2. **Create View Layer**.
3. Set a **view definition**:
   - ASNV: `MapVisibility = 'Visible'` (and drop owner names, emails, street numbers if needed).
   - Cal OES: `OutageStatus = 'Active'` for the incident layer used by KPIs and the live list.
4. On the view, **do not enable editing**.
5. Share the **view** with Everyone later. Keep the source layer in the organization or a staff group.

Create extra views when one layer must serve two jobs. Cal OES uses:

- Incident points for KPIs, lists, and the map
- County polygons summarized with `Number_Impacted_Customers` and `Number_Incidents`
- Outage area polygons (where a utility publishes them)

You can summarize counties with **ArcGIS Online analysis** (Summarize Within) on a schedule, or with Arcade/Attribute Rules, or a notebook. The dashboard should consume the summary, not calculate it from thousands of points on every load.

### Step 4. Set cache and refresh for live layers

On the **view item** (Settings):

- **Cache control:** match how often the data actually changes (for example 5 minutes, not 30 seconds, if the ETL runs every 10 minutes).
- Avoid **relative date** filters in the view definition (`in the last 7 days`). Those prevent effective caching on public dashboards. Cal OES keeps a separate “last week” layer that is **turned off** in the map and used only if needed.

---

## Part 3 — Author the web map (this is 30% of the look)

A dashboard map is not a GIS project map. It is a **display surface** plus a **data source** for every chart.

1. Open **Map Viewer**.
2. Choose the basemap:
   - Program: **Human Geography** (or Light Gray Canvas) + **World Hillshade**.
   - Operations: **Dark Gray Canvas** or **Imagery Hybrid** (Cal OES uses NAIP Imagery Hybrid).
3. **Add** your hosted views.
4. Save the map with a public-facing title, for example `Wildlife Sanctuary Program (Public)` or `Statewide Outages (Public View)`.

### Step 1. Filter in the layer, not only in the dashboard

On each layer: **Filter** (or **Processing** > **Filter**):

- Protected areas: `State = 'Virginia'`
- Chapter boundary: `ChapterName = 'Your Chapter'`
- Counties: `STATE_NAME = 'Virginia'` (or your state)
- Live incidents: `OutageStatus = 'Active'`
- County choropleth: `Number_Impacted_Customers > 0`
- Optional mask: a polygon of “not my state” at ~50% transparency so the study area is obvious (Cal OES does this with a California mask).

### Step 2. Symbolize for the question

**Program properties**

- Duplicate the properties layer.
- Layer A: **Counts and Amounts (size)** on `Acres` (class breaks).
- Layer B: **Types (unique symbols)** on `Type`, with a restrained blue ramp that matches the dashboard navy.
- Set transparency ~20% so the basemap still reads.

**Operations incidents**

- Unique values on `OutageType`: Not Planned = amber, Planned = yellow. Same colors you will use on indicators.
- County polygons: unique values or class breaks on customer-count bins (`0–1,000`, `1,001–2,000`, `2,001–5,000`, `More than 5,000`).
- Scale visibility if needed: a simplified “zoomed out” incident layer statewide, a denser layer when zoomed in. Cal OES keeps both and toggles visibility.

### Step 3. Configure pop-ups for humans and for dashboard lists

Pop-up fields are reused by **List**, **Details**, and **Feature** elements.

Title examples:

- `{UtilityCompany}: ID - {IncidentId}`
- `{Name} ({Type})`

Visible fields only: county, acres, type, year, city — or customers, cause, start, restore. Hide `OBJECTID`, shape area, internal color fields.

Turn **Enable pop-ups** off on mask, boundary, and basemap-context layers.

### Step 4. Bookmarks, labels, and refresh

1. Zoom to the study area. **Add bookmark** (`App Placement`, `Statewide`).
2. Labels: counties at small scales, incident IDs only when zoomed in.
3. On live layers: **Refresh interval** = your ETL cadence (for example 10 minutes).
4. Save the map.

### Step 5. Confirm the map is dashboard-ready

Checklist:

- [ ] Only operational layers you need
- [ ] Public-safe fields only
- [ ] Pop-ups titled and short
- [ ] Bookmark of the default extent
- [ ] Unique-value colors you can reuse in charts
- [ ] Definition queries already applied
- [ ] Search enabled on the name / county field (Map Viewer > **Configure search**)

---

## Part 4 — Create the dashboard shell

1. Sign in to ArcGIS Online.
2. **App launcher** (grid) > **Dashboards**, or **Content** > **Create app** > **Dashboards**.
3. **Create dashboard**.
4. Title, tags, summary, folder. Use a title the public will understand.
5. Click **Create dashboard**. You land on an empty **desktop view**.

Alternatively, open the web map item > **Create app** > **Dashboards**. That adds the map as the first element automatically.

### Theme (do this before adding charts)

1. Action bar > **Theme**.
2. Program: **Light**, then **Custom**:
   - Primary / header text: `#004C73`
   - Background: white / very light gray
   - Tight spacing, slightly rounded corners if you want a modern card look
3. Operations: **Dark**, then **Custom**:
   - Dashboard background `#242424`
   - Element outline / header `#1A1A1A`
   - Accent gold `#E69800`
4. If you set the theme first, new pie and serial charts inherit matching default colors.

### Header

1. Action bar > **View** (or **Header**) > **Add header**.
2. Program:
   - Title: `Wildlife Sanctuary Program` (this is the only H1 on the page — keep it unique).
   - Optional background image of habitat, sized **Fit height**, placed center.
   - Title color = brand navy.
3. Operations:
   - Large **logo** (agency seal).
   - Logo URL → organization website.
   - Subtitle: `(PG&E, SDG&E, SCE)` or whoever the data covers.
   - No extra title if the logo already names the agency.

You will add selectors to this header in Part 6.

---

## Part 5 — Recreate the ASNV-style layout

Target structure:

```text
HEADER  [ Title ......................... Year selector | Date selector ]

LEFT 25%                         CENTER 50%                      RIGHT 25%
┌─────────────────────┐          ┌────────────────────────┐      ┌─────────────────────┐
│ KPI: Total Acres    │          │ TAB: Map               │      │ KPI: Total Properties│
├─────────────────────┤          │ TAB: Growth over time  │      ├─────────────────────┤
│ TABS:               │          │   (embedded app)       │      │ TABS:               │
│  Acres by Year      │          └────────────────────────┘      │  Count by Year      │
│  Acres by County    │                                          │  Count by County    │
│  Acres by City      │                                          │  Count by Type (pie)│
├─────────────────────┤                                          ├─────────────────────┤
│ KPI: PADUS areas    │                                          │ KPI: IBAs           │
└─────────────────────┘                                          └─────────────────────┘
```

### Step 1. Add the map

1. **Add element** > **Map**.
2. Choose your web map.
3. **Map tools:** Bookmarks, Legend, Layers (map contents), Search. Turn **Compass** and **Locate** off unless field staff need them.
4. Scale bar: **Ruler** (program) or **None** (operations).
5. **Point zoom scale:** something like `1:200,000` so a selected point does not zoom to 1:500.
6. Pop-ups: on.
7. **Done**. Drag the map to the center and size it to about half the width.

### Step 2. Add four indicators

**Add element** > **Indicator**, once per KPI.

| Indicator | Data | Statistic | Top text | Bottom text | Color |
| --- | --- | --- | --- | --- | --- |
| Total Acres | Properties view | Sum of `Acres` | Total Acres | (ASNV Certified) | Navy `#004C73` |
| Total Properties | Properties view | Count of features | Total Properties | (ASNV Certified) | Navy |
| PADUS Protected Areas | PADUS layer (filtered to state) | Count (or sum of acres) | PADUS Protected Areas | (Acres in Virginia) | Green `#267300` |
| Important Bird Areas | IBA layer | Count | Important Bird Areas (IBA) | (In Virginia) | Green |

Configuration tips:

1. **Data** tab: layer from the **map** (not a second copy of the service) so map filters can flow through.
2. **Indicator** tab: value type **Statistic**.
3. Middle section: `{value}` at a large size (ASNV uses a very large middle font).
4. Add a simple icon (land parcel, plant, shield, bird) in the same color as the number.
5. **Value formatting:** grouping on, 0–1 decimal places for acres, 0 for counts.
6. **General:** give each indicator a unique **name** (`TotalAcresIndicator`) and a descriptive **Accessible name**.

Dock Total Acres top-left, Total Properties top-right, PADUS bottom-left, IBAs bottom-right.

**Quality check:** the statistic must match the caption. If the subtitle says “acres”, sum an acres field; do not count polygons and call it acres.

### Step 3. Add the six charts, then stack them into two tab sets

**Serial chart — Certified Acres by Year**

1. **Add element** > **Serial chart**.
2. Layer: properties view.
3. Categories from **Grouped values**, category field `Year`.
4. Statistic: **Sum** of `Acres`.
5. Sort: Year descending (newest at the top if you use a bar chart).
6. Series: **Bar** (horizontal) in brand navy. Hide the legend. Show data labels.
7. Title: `Certified Acres by Year`.
8. **Actions:** Selection change > **Filter** the map properties layer (optional; ASNV mainly filters from the header and the map).

**Serial chart — Certified Acres by County**

- Group by `County`.
- Sum of `Acres`.
- Sort by value descending.
- **Maximum categories: 10** if you only want the leaders.
- Optional **label overrides** (`Arlington/City of Alexandria` → `Alexandria`).

**Serial chart — Certified Acres by Top Ten Cities**

- Group by `City`, sum `Acres`, sort value desc, **max 10**.

**Serial chart — Property Count by Year**

- Group by `Year`, **Count**.

**Serial chart — Property Count by County**

- Group by `County`, **Count**, sort desc.

**Pie chart — Count by Property Type**

1. **Add element** > **Pie chart**.
2. Group by `Type`, Count.
3. Turn **color match** on if the map already uses unique symbols for `Type`.
4. Legend on the right, showing counts (not only percents).
5. Inner radius 0 (full pie) or a small donut if you prefer.

**Stack into tabs**

1. Drag **Acres by County** onto the center of **Acres by Year** until the hint says **Stack the items**.
2. Drag **Acres by City** onto the same stack.
3. Click each tab > rename: `Acres by Year`, `Acres by County`, `Acres by City`.
4. Repeat on the right: `Count by Year`, `Count by County`, `Count by Type`.

Tabs are how ASNV stays informative without looking busy. Viewers see one chart; power users click for the rest.

### Step 4. Optional: embed a second story in the map’s tab

ASNV stacks an **Embedded content** element with the map. The second tab is titled `Growth of Certifications over Time` and points at an ArcGIS Experience.

1. **Add element** > **Embedded content**.
2. Type: **Document** (or **Dashboard** / URL).
3. Paste a public Experience, StoryMap, or chart URL. The URL must allow iframe embedding and be HTTPS.
4. Stack it with the map. Rename tabs `Map` and `Growth of Certifications over Time`.

### Step 5. Wire the map to the charts

This is the behavior that makes ASNV feel alive: **as you pan the map, side charts and KPIs update to the visible extent**.

1. Hover the map > **Configure**.
2. **Actions** tab > **When map extent changes**.
3. **Filter** > enable every chart and every indicator that should follow the map (acres, property count, pie, year charts).
4. Filter method: **Geometry** (spatial).
5. Do **not** filter the statewide context indicators (PADUS, IBAs) if those numbers should stay statewide.

### Step 6. Add header selectors

1. On the header, **Add category selector**.
   - Name: `Year`.
   - Categories from **Grouped values** on `Year`.
   - Display: **Dropdown**, compact.
   - Selection: **Multiple**, operator **is in**.
   - Include **None** option (show all years).
   - **Actions** > Filter the map properties layer **and** every chart/indicator that uses that layer.
2. **Add date selector**.
   - Type: **Date picker**, **Range**, dates only (no time).
   - Presentation: dropdown.
   - **Actions** > Filter the same targets using field `Close_Date` (or your certification date).

Test: pick one year. Map points, KPIs, and every tabbed chart should drop to that year. Clear the selector (None) and everything returns.

---

## Part 6 — Recreate the Cal OES-style layout

Target structure:

```text
HEADER  [ Logo + subtitle ........ County | Utility | Outage type ]

LEFT ~22%              CENTER ~50%                 RIGHT ~18%           FAR RIGHT ~18%
┌──────────────────┐   ┌─────────────────────┐    ┌─────────────────┐  ┌──────────────┐
│ KPI: Customers   │   │                     │    │ LIST: Counties  │  │ LIST: Current│
│     without power│   │        MAP          │    │  with outages   │  │ outages      │
│ Planned | Unplan │   │                     │    │                 │  │              │
│ H-BAR: by utility│   │                     │    │                 │  │              │
└──────────────────┘   └─────────────────────┘    └─────────────────┘  └──────────────┘
┌─────────────────────────────────────────────┐
│ COLUMN CHART: Counties with 500+ customers  │
└─────────────────────────────────────────────┘
```

### Step 1. Map for operations

1. Add the outage web map.
2. Map tools: **Search only** (Cal OES keeps the map clean). Zoom buttons stay on.
3. Default bookmark: Statewide.
4. Selection / highlight color that shows on imagery (Cal OES uses orange selection).

### Step 2. KPI row with a reference statistic

Cal OES does not show a lone number. The main indicator is:

- **Value:** Sum of `ImpactedCustomers` (active outages)
- **Reference:** Count of outage features
- Caption: `Total Customers Without Power`
- Description: `From {reference} Outages`
- Value color: amber `#E69800`

Then two sibling indicators:

| | Filter | Value | Reference (caption) | Color |
| --- | --- | --- | --- | --- |
| Planned | `OutageType = 'Planned'` AND `OutageStatus = 'Active'` | Sum customers | Count of those outages (`{reference} Planned Outages`) | Yellow |
| Not planned | `OutageType <> 'Planned'` AND active | Sum customers | Count (`{reference} Not Planned Outages`) | Amber |

How to configure the reference:

1. Indicator > **Data**.
2. Statistic for the main value (sum of customers).
3. Enable **Reference** > statistic **Count**.
4. Apply the **same filter** to both, or the caption will disagree with the number.
5. Bottom text: `Customers Without Power`.

Group the two smaller indicators **side by side** under the total (Shift-drag to **Group as a column** so they share one card).

### Step 3. Serial chart — customers by utility (stacked, horizontal)

1. **Serial chart**.
2. Layer: active incidents.
3. Category field: `UtilityCompany`.
4. Split by (series): `OutageType`.
5. Statistic: Sum of `ImpactedCustomers`.
6. Filter: `OutageStatus = 'Active'`.
7. Chart type: **Bar** (horizontal).
8. Stack: **Stacked** (regular).
9. Series colors: Not Planned = `#FFAA00`, Planned = `#FFFF00`.
10. Sort by value descending.
11. Data labels on. Legend optional if the KPI colors already teach the legend.
12. Title: `Customers Without Power`. Axis title: `Power Company`.

### Step 4. Serial chart — counties with serious impact only

Noise kills operations dashboards. Cal OES **does not chart every county**.

1. Layer: county summary.
2. Category: `NAME`.
3. Sum `Number_Impacted_Customers`.
4. **Filter:** `Number_Impacted_Customers > 499`.
5. Chart type: **Column** (vertical).
6. Category labels rotated ~30°.
7. Integers only on the value axis.
8. Color: amber.
9. Title: `Counties (500+ Customers Impacted)`.
10. Dock this chart **under** the map + left column so it reads as a statewide strip.

### Step 5. List — counties with outages

1. **Add element** > **List**.
2. Layer: county summary (or counties with `Number_Impacted_Customers > 0`).
3. Sort: `Number_Impacted_Customers DESC`.
4. Max features: 60.
5. Line item (rich text), for example:

```text
{NAME}
Customers Without Power: {Number_Impacted_Customers}
Outages: {Number_Incidents}
```

6. Selection mode: **Multiple**.
7. Title: `Counties with Outages` and a one-line instruction: `(Select County to Filter Map & Outage List)`.
8. Background: `#1A1A1A`. Selection color: a dark orange.

**Actions** (this is the operations pattern):

- Selection change > **Zoom** the map
- **Flash** the map
- **Filter** incident points where `County` = selected `NAME` (use a **field map** if the names differ)
- **Filter** the outage list, utility chart, and KPIs the same way

### Step 6. List — current outages

1. Layer: incident points.
2. Filter: `OutageStatus = 'Active'`.
3. Sort: `ImpactedCustomers DESC`.
4. Max features: 100.
5. Line item:

```text
{County}
{UtilityCompany} - Incident ID: {IncidentId}
Customers Without Power: {ImpactedCustomers}
Type: {OutageType}    Cause: {Cause}
Date/Time Started: {StartDate}
Date/Time Restored (Estimate): {EstimatedRestoreDate}
```

6. **Actions:** Zoom + Flash the map. Do not also filter the whole dashboard unless you want a drill-down that hides other outages.

### Step 7. Header selectors

**County** (categories from **features**, not grouped values)

- Layer: counties.
- Display field `{NAME}`.
- Sort A–Z.
- Dropdown, single selection.
- None option labeled **All Counties**, placed first.
- Actions: Filter incidents (`NAME` → `County`), filter county layer, filter both lists, filter charts and indicators, **Zoom** the map.

Using **features** (not grouped values) is what allows zoom/flash because the selector still has geometry.

**Utility company** (grouped values)

- Group by `UtilityCompany`.
- Multiple selection, operator **is in**.
- Filter incidents, lists, KPIs, and charts.

**Outage type** (defined values or grouped values)

- Display: **Button bar**, inline in the header.
- Options: All Outages | Planned | Not Planned (Cal OES also uses static PSPS labels for specific utility messages).
- Single selection, default **All Outages**.
- Filter `OutageType`.

### Step 8. Optional URL parameter

Cal OES adds a **feature** URL parameter so a county link can open the dashboard already zoomed and filtered.

1. Dashboard **options** / **URL parameters**.
2. Type: **Feature** (or Category).
3. Layer: counties, ID field `NAME`.
4. Actions: Zoom map + the same filters as the county selector.

Example: append a parameter such as `?county=Monterey` (exact name depends on how you configure the parameter).

---

## Part 7 — Layout craft (what makes it look “designed”)

### Docking vs grouping vs stacking

| Move | How | Use |
| --- | --- | --- |
| **Dock as row / column** | Drag to an edge until the hint says Dock | Three-column body |
| **Stack** | Drop on the center of another element | Tabs (ASNV charts and map) |
| **Group** | Same as stack but hold **Shift** (green hint) | KPI pair with no inner margin (Cal OES planned | unplanned) |

Resize by dragging borders. Percentages appear as you drag. Typical map share: **45–55%** of width. KPIs: about **15%** of height each.

### Element titles are part of the UI

- Every chart and list needs a visible title (H2).
- Put the **instruction in the title or subtitle**: `(Select County to Filter Map & Outage List)`.
- Leave KPI titles inside the indicator (top section), not as a duplicate element title.

### Last update, empty states, and expansion

- Map: **Show last update** on for live data.
- Charts: often off so the chrome stays quiet.
- Configure **No data** text (`No outages in this county`) instead of a blank panel.
- Allow **element expansion** (both examples do). Allow **resize** on exploratory dashboards; Cal OES turns resize **off** so operators cannot break the layout.

### Mobile view

1. **View** pane > **Add mobile view**.
2. Copy only: header title, the main KPI, the map, and one list.
3. Put selectors in the **drawer**, not the header.
4. Reconfigure actions on the mobile copies (they are not copied).
5. Skip refresh intervals on mobile (not supported).

---

## Part 8 — Share, document, and scale

### Item pages

Complete the **dashboard**, **web map**, and **layer** item pages:

- Summary that states what the numbers mean and how often they update
- Thumbnail (Cal OES uses a branded 600×600 graphic: agency mark + “Dashboard” + public badge)
- Credits and a disclaimer (Cal OES: data compiled from utilities, not certified by the agency)
- Tags people will search

### Sharing order

Share **inside-out** so the dashboard never shows a broken layer:

1. Hosted views
2. Web map
3. Dashboard
4. Then **Everyone (public)** if it is a public app

If any layer is organization-only, anonymous users see empty widgets.

### High-demand public dashboards

Follow Esri’s [scalable dashboard](https://doc.arcgis.com/en/dashboards/latest/reference/build-highly-scalable-dashboards.htm) rules:

- Hosted feature layers or hosted views only (not dynamic map services) for public traffic
- No public editing
- Cache control aligned with real update frequency
- No relative-date view definitions
- Indexes on filter fields
- Do not point twenty widgets at twenty duplicate layer items; reuse the map’s layers

### Accessibility

- One H1: the header title
- Element titles stay H2
- Contrast: navy on white, or amber on `#1A1A1A` — check both
- Accessible names on charts
- Do not encode meaning in color alone; Cal OES also writes `Planned` / `Not Planned` in the list

---

## Part 9 — Click-path cheat sheet (from a blank organization)

Use this when you are actually at the keyboard.

1. **Content** > New item > publish hosted feature layer from your cleaned table.
2. **Create View Layer** > definition query > disable editing > set aliases and indexes.
3. **Map Viewer** > basemap > add views > filter > symbolize > pop-ups > bookmark > refresh interval > save.
4. Map item > **Create app** > **Dashboards**.
5. **Theme** (light or dark custom colors).
6. **Add header** (title or logo).
7. Configure the **map** element (tools, zoom scale, extent actions).
8. Add **indicators** (statistic + optional reference).
9. Add **serial / pie charts**; stack related charts into **tabs**.
10. Add **lists** with line-item templates.
11. **Group** KPI pairs with Shift-drag.
12. Add **selectors** to the header; Actions > Filter / Zoom / Flash.
13. Map **Actions** > extent change > Filter charts.
14. List **Actions** > Zoom + Flash + Filter.
15. **View** > mobile view (optional).
16. Save. Fill in item details and thumbnail.
17. Share views → map → dashboard.
18. Open the public URL in a private window and click every selector.

---

## Part 10 — Why these two dashboards feel professional

Steal these habits; do not steal the data.

**From ASNV (program summary)**

- Brand color on every number, chart bar, and header
- Tabs instead of a wall of charts
- Map-driven statistics (extent filter)
- Context KPIs in a second color (protected areas vs certified acres)
- Public view that hides sensitive properties
- Header filters for year and date so one dashboard serves annual reports and ad-hoc questions

**From Cal OES (operations)**

- Dark theme and a quiet map toolbar
- One huge number (customers) plus a count of events as `{reference}`
- Color = status, reused on KPIs, bars, and lists
- Lists are **controllers**, not decoration: click a county, the map and incident list follow
- Charts that **drop the long tail** (`> 499` customers) so the signal is readable
- County selector based on **features** so zoom works
- Disclaimer and branded thumbnail on the item page
- Deep link via URL parameter

**Shared habits**

- Hosted **views** named “Public View”
- One web map as the single data source
- Instructions written on the element (`Select Outage to Go To area`)
- Default extent bookmarks
- No unused tools, no unused fields, no unused layers

---

## Official Esri references

- [Create a dashboard](https://doc.arcgis.com/en/dashboards/latest/get-started/create-a-dashboard.htm)
- [Dashboard layouts](https://doc.arcgis.com/en/dashboards/latest/get-started/dashboard-layout.htm)
- [Create web maps for dashboards](https://doc.arcgis.com/en/dashboards/latest/reference/create-web-maps-for-dashboards.htm)
- [Actions](https://doc.arcgis.com/en/dashboards/latest/create-and-share/actions.htm)
- [Selectors](https://doc.arcgis.com/en/dashboards/latest/create-and-share/selectors.htm)
- [Themes](https://doc.arcgis.com/en/dashboards/latest/get-started/change-theme.htm)
- [Build highly scalable dashboards](https://doc.arcgis.com/en/dashboards/latest/reference/build-highly-scalable-dashboards.htm)
- [Accessibility best practices](https://doc.arcgis.com/en/dashboards/latest/reference/accessibility-best-practices.htm)
- [Learn lesson: Build an interactive dashboard](https://learn.arcgis.com/en/projects/build-an-interactive-dashboard/)
- [Learn lesson: Showcase fire data with a dashboard](https://learn.arcgis.com/en/projects/showcase-fire-data-with-a-dashboard/)

---

## Source dashboards (for study)

- ASNV dashboard item: `96896859c42c4301a8032609493a9e00`  
  Map: [ASNV Wildlife Sanctuary Program Summary (Public)](https://www.arcgis.com/home/item.html?id=fd8e15e1be434958833f3a59240a7ceb)
- Cal OES dashboard item: `7edefc1970d44b839ebbfd7b45e51e2d`  
  Map: [Cumulative Statewide Power Outages (Public View)](https://www.arcgis.com/home/item.html?id=2d5a95786c69479c84e3291ab4cadffe)  
  Data: [Statewide Power Outages (Public View)](https://www.arcgis.com/home/item.html?id=439afad071eb4754903906aff1946719)
