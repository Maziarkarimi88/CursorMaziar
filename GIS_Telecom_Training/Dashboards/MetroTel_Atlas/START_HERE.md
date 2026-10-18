# START HERE — MetroTel Atlas (light briefing)

This is the **light-color** dashboard. Layout is different from MetroTel Pulse (dark command center).

## How it is arranged

1. **Left rail** — brand, filters, legend, and the full decisions list (open-action count sits here, not in a sixth KPI tile).
2. **Hero KPI** — large weighted **ARPU** (the commercial lead number).
3. **2×2 KPI grid** — Subscribers, Churn, 4G coverage (with a bar), P1 expand count.
4. **Tall map on the right** — districts fill the remaining height.
5. **Three equal charts on the bottom** — priority doughnut, **horizontal** ARPU bars, yearly trend.

Paper background `#F3EFE6`, terracotta `#C45C26`, sage `#2F6F5E`.

## Open it

```text
python -m http.server 8767
```

Then open http://localhost:8767

Or double-click `index.html`. If the map is blank, use the Python server.

You should see **$32.0** as the big ARPU figure and **526** subscribers.

## Load your data

CSV columns:

```text
DIST_ID, DIST_NAME, SUBSCRIBERS, AVG_ARPU, AVG_CHURN, COV_4G_PCT, PRIORITY, POPULATION, FIBER_STATUS
```

Click **Load my CSV** or drag the file onto the page.

## Upload to ArcGIS Online

Same data model as Pulse. After you like the HTML design, publish layers with the Pulse script (`../MetroTel_Pulse/scripts/publish_to_agol.py`) or rebuild widgets using `agol/NATIVE_DASHBOARD.md` (light theme colors).
