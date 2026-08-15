# Day 1 — GIS Fundamentals & Geodatabase (Manual v4)

Aligned to the ready presentation **Day 1_ready.pptx** (also at `presentation/Day1_GIS_Application_in_Telecom_Ready.pptx`).

## Use these files
- `Day1_GIS_Fundamentals_Geodatabase_Manual_v4.docx` — lab manual (Word)
- `Day1_GIS_Fundamentals_Geodatabase_Manual_v4.pdf` — same manual (PDF)
- `Day1_GIS_Fundamentals_Geodatabase_Manual_v4.html` — same manual (HTML)
- Presentation: repo root `Day 1_ready.pptx`

## How to teach
1. Open the presentation. After each part-divider slide, do the matching lab in the v4 manual.
2. Students create objects in ArcGIS Pro (shapefile, feature dataset, feature classes, domains, subtypes, keys, relationship classes).
3. **Do not load the CSV/GeoJSON files in `data/`.** v4 does not use synthetic tables. Digitize a few features by clicking.

## Labs
| Lab | After presentation part | What you create |
|-----|-------------------------|-----------------|
| 1 | Part 1 — GIS concepts | Project, folder connection, empty GDB |
| 2 | Part 2 — Coordinate systems | Map CRS = WGS 1984 UTM |
| 3 | Part 3 — Geodatabase | Shapefile, FD_Irrigation, FD_Telecom, feature classes |
| 4 | Domains & subtypes | Dom_Status, Dom_Height_m, Tower subtypes |
| 5 | Relationships / irrigation | PK/FK then six 1:M relationship classes |
| 6 | Raster / DEM | Add a real DEM; Hillshade + Slope |

v3 files in this folder are the previous MetroTel synthetic version. Use **v4** with the ready deck.
