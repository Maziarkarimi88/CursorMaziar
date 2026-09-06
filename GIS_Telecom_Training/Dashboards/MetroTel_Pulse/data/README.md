# Dashboard data

Training extracts from Day 3 (geo-marketing) and Day 5 (executive KPIs).

| File | Layer | Locate by |
|---|---|---|
| `MarketingZones.geojson` | 12 districts | polygons, property `DIST_ID` |
| `ExecZone_KPI_Dashboard.csv` | Zone KPIs (join to polygons) | `DIST_ID` |
| `Capstone_CellSites.csv` | On-air + candidate sites | `LON`, `LAT` |
| `CompetitorSites.csv` | Rival A/B | `LON`, `LAT` |
| `Subscribers_with_XY.csv` | 600 geocoded customers | `LON`, `LAT` |
| `Monthly_Executive_KPI_Timeseries.csv` | Network trend | `MONTH` |
| `Capstone_Decisions.csv` | Open actions | `ZONE` = `DIST_ID` |

After editing these files run `python ../scripts/build_embedded_data.py` so `index.html` picks up the change.
