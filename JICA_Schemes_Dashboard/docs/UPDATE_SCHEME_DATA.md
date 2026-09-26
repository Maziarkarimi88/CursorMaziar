# Efficient updates (progress and other scheme fields)

`schemes_dashboard.csv` / `JICA_Schemes` is the **only** place to change progress, cost, status, dates, and households.

Do **not** rejoin or republish coverage, canal, or structures when those numbers change. Those layers are geometry. One scheme has many features, so editing progress there is slow and easy to get wrong.

Physical works stays **per `Scheme_UID`**. Do not average or total it.

---

## What to update where

| Change | Edit this | Leave alone |
| --- | --- | --- |
| `PROGRESS_PCT` / physical works | 14-row `JICA_Schemes` | Three shapefiles |
| Cost, status, contractor, dates, HH | 14-row `JICA_Schemes` | Three shapefiles |
| New canal / catchment / dam geometry | The matching shapefile / GDB | — |
| New scheme (15th row) | Add one row to `JICA_Schemes`, then add GIS features with that `Scheme_UID` | — |

---

## Fastest day-to-day: edit the hosted table in ArcGIS Online

After `schemes_dashboard.csv` is a **hosted feature layer** (14 points) or **hosted table**:

1. Content → open **`JICA_Schemes`** (the 14-row item).
2. **Data** tab → **Table**.
3. Click the `PROGRESS_PCT` cell (or `Physical_Progress_Percentage`).
4. Type the new % for **that one** `Scheme_UID`. Enter.
5. Refresh the dashboard (or wait for the next auto-refresh).

Change three schemes in about a minute. No Pro, no join, no overwrite.

Turn on **Enable editing** on that item (Update attributes only). Do not enable editing on the three GIS layers unless someone is fixing geometry.

---

## Fastest batch: overwrite from Excel / CSV

Use this when many rows change at once (monthly progress pack).

1. Keep a **master** workbook with the same column names as the hosted layer (`Scheme_UID`, `PROGRESS_PCT`, `STATUS`, `COST_USD`, …).
2. Update the cells. Save as UTF-8 CSV (same name).
3. ArcGIS Online → `JICA_Schemes` item → **Update data** → **Overwrite entire feature layer** (or **Update** / append with match on `Scheme_UID`).
4. Field names and types must match the first publish. Do not add commas in cost. Leave Not Awarded progress **blank**, not `0`.
5. Refresh the dashboard.

Do **not** overwrite coverage / canal / structures with this CSV.

If **Update data** is missing, the item was added as a one-off file, not a hosted layer. Publish the 14 points as a hosted feature layer once, then overwrite from then on.

---

## From ArcGIS Pro (if the layer is already hosted)

1. Add the hosted `JICA_Schemes` to a Pro map (not a local shapefile copy).
2. Edit the table → save edits. They write back to AGOL.
3. Or: edit the local CSV → **XY Table To Point** / Table To Table → **Overwrite Web Layer** for `JICA_Schemes` only.

---

## Do not do this for progress

1. Re-join the Excel table onto all three shapefiles and export again (the `CONTRACT_S` / 002809 path).
2. Calculate progress on canals or structures (one scheme = many rows).
3. Overwrite the whole web map or the three-layer service.

Map pop-ups on canals can skip progress, or show it from the list / Physical works tile. If a pop-up must show `%`, run **Join Field** in Pro onto the GIS **only when you need pop-ups refreshed**, not every progress cycle.

---

## One-time setup (if not done)

1. Publish **`JICA_Schemes`** as its own hosted feature layer (14 points from `LON`/`LAT`).
2. Point every indicator, pie, list, and header selector at **that** item.
3. Point map Filter actions at the three shapefiles by `Scheme_UID` / `Program`.
4. Share the scheme layer with the same group as the map.

After that, a progress update is **one table edit** (or one CSV overwrite).
