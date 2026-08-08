# MetroTel FTTH Geometric Network — ArcGIS Desktop

Complete geometric-network-ready dataset for **Day 4: Fiber & Transmission**.

- **22,889** junctions (nodes/devices)
- **22,893** edges (fiber segments)
- **21,420** Home_ONT end-users
- **3** internet sources (IXP A, IXP B, satellite backup)
- CRS: **EPSG:32642** (UTM 42N)

Path: `Internet_Source → Core_POP → Regional_Hub → OLT → Joint_Closure → FDH → Optical_Splitter → Home_ONT`

## Quick start (ArcMap)

1. Read `docs/ArcMap_GeometricNetwork_Build_Guide.md`
2. Run `scripts/build_geometric_network_arcmap.py` in ArcGIS Desktop Python
   **or** follow the manual wizard steps in the guide
3. Use **Utility Network Analyst** for upstream/downstream traces

## Main layers

| File | Description |
|------|-------------|
| `shapefiles/GN_Junctions.shp` | All devices / connection nodes |
| `shapefiles/GN_Edges.shp` | All fiber edges snapped to junctions |
| `MetroTel_FTTH_GeometricNetwork_Data.gpkg` | Same data in GeoPackage |
| `tables/Connectivity_Rules.csv` | Allowed junction–edge–junction rules |
| `tables/Network_Hierarchy.csv` | Device hierarchy explanation |

Typed subsets (`Junc_*.shp`, `Edge_*.shp`) are provided for building a multi-class geometric network if preferred.
