# Native ArcGIS Online dashboard — zoom to each scheme

Publish two hosted feature layers that share `SCHEME_UID`:

1. **Scheme areas** — polygons (`data/schemes_areas.geojson`, then swap in surveyed command areas / watersheds)
2. **Scheme lines** — polylines (`data/schemes_lines.geojson`, then swap in canals / check-dam alignments)

Put both in one web map. Irrigation = teal, watershed = sand. Add the attribute table `schemes_dashboard.csv` as a table or join it onto both layers.

## Actions that match the HTML prototype

On the **scheme list** (and on the map):

1. **Filter** both layers where `SCHEME_UID` equals the selected row.
2. **Zoom** the map to the **union extent** of that scheme’s polygon **and** line.
3. Optional: **Flash** both features.

Do not zoom only to the point centroid. Each irrigation and each watershed scheme has both a polygon and a line; the map must fit both.

Category selectors (`PROGRAM`, `STATUS`, `PROVINCE`) filter both layers. After a filter, zoom to the visible features.

## Replace placeholder geometry

The GeoJSON in this folder is sized from district centroids and `AREA_HA` / `CANAL_KM`. When you have surveyed GIS:

1. Keep `SCHEME_UID` (`JICA-IS-01` … `JICA-WSM-07`) on every feature.
2. Overwrite `data/schemes_areas.geojson` and `data/schemes_lines.geojson`.
3. Re-run `python3 scripts/build_geometries.py` only if you still need the HTML embed; or load the new files with **Replace areas** / **Replace lines** in the prototype.
4. Republish the hosted layers and the zoom action keeps working because it keys on `SCHEME_UID`.
