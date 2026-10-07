# Why 15 m can give 1,041 noise and 2,339 clustered

The KOBO file has **3380** rows. **26** have no GPS. **3354** visits have coordinates.

GIS tools (ArcGIS / QGIS / sklearn DBSCAN) usually do this:

- search radius = 15 m
- a record is **noise** if no other record lies within the search radius
- a **cluster** needs at least 2 records

That is **single-linkage** (A near B and B near C → A, B, C one cluster) and it **drops** isolated points instead of keeping them as 1-visit wells.

Your 1,041 + 2,339 = 3,380 is the full file (3,354 GPS rows + 26 empty). 1,041 noise is what you get if the 26 empty rows are noise and about 1,015 GPS points have no neighbour inside the search radius.

## Counts on this file (great-circle metres)

| Rule | Isolated / noise | In a group of 2+ | Groups of 2+ | What we call them |
|---|---:|---:|---:|---|
| DBSCAN / single-linkage 15 m, min 2 | 415 GPS + 26 empty = **441** | **2939** | 359 | noise vs clustered records |
| Complete-linkage 15 m (this repo) | **533** one-visit wells | **2821** visits in 548 wells | 548 | every visit is a well |
| Earlier GIS (~5.2 m) | **1,041** | **2,339** | — | GPS precision window |
| Your GIS now (15 m geodesic) | **415** GPS isolates | **2939** | 359 | Near Table and DBSCAN min 2 must match |
| Single-linkage **5.0 m** (GPS precision, max 5.0 m) | 1059 GPS + 26 empty = **1085** | **2295** | 428 | GPS-fix window |
| Single-linkage **5.2 m** | 1022 GPS + 26 empty = **1048** | **2332** | 420 | near your split |
| Single-linkage **5.22 m** | 1014 GPS + 26 empty = **1040** | **2340** | 422 | one record from your 1,041 / 2,339 |

True **15 m** great-circle DBSCAN on this export is **441 noise / 2939 clustered**, not 1,041 / 2,339.

If Generate Near Table and DBSCAN (15 m, min 2) both show **2939** points, the search is geodesic metres. Those two tools **must** agree on that count: a point is clustered when it has at least one neighbour ≤ 15 m. That is not 2939 wells. DBSCAN still makes **359** groups; **165** of them span more than 15 m (1966 visits in street chains). Complete linkage gives **1081** wells. Keep the **415** GPS isolates as one-visit wells.

1,041 / 2,339 is what we get at about **5.22 m**, not 15 m. That is the GPS precision field (median 4.62 m, maximum 5.0 m), or a layer in degrees whose tool is not using geodesic metres.

Please check in the GIS: layer CRS (UTM metres vs WGS84 degrees), DBSCAN `min_samples` (2 vs 5), and whether empty GPS rows are noise.

This repo keeps complete-linkage wells so a street of houses 11 m apart does not become one well. Isolated GPS points stay as one-visit wells, not 'noise' — they are still real home-dug wells, just measured once.
