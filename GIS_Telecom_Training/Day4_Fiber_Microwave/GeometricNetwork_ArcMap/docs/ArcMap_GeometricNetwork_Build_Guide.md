# Day 4 — MetroTel FTTH Geometric Network (ArcGIS Desktop / ArcMap)

Complete multi-source fiber distribution network for training: internet sources → core → hubs → OLTs → joints/FDHs → splitters → **21,420** home ONTs.

## Network hierarchy

| Level | Device / node type | Count | Role |
|------:|--------------------|------:|------|
| 0 | Internet_Source | 3 | IXP A, IXP B, Satellite backup (Sources) |
| 1 | Core_POP | 2 | National core + core ring |
| 2 | Regional_Hub | 6 | City aggregation + hub rings |
| 3 | OLT | 18 | PON headends |
| 4 | Joint_Closure | 90 | Feeder splice points |
| 4 | FDH | 90 | Fiber Distribution Hubs |
| 5 | Optical_Splitter | 1,260 | 1:16 distribution splitters |
| 6 | Home_ONT | **21,420** | End-user premises (Sinks) |

**Totals:** 22,889 junctions · 22,893 edges

### Edge types

| EdgeType | Count | Connects |
|----------|------:|----------|
| Backbone_Fiber | 9 | Source↔Core, Core↔Hub |
| Core_Ring | 1 | Core↔Core |
| Hub_Ring | 5 | Hub↔Hub |
| Feeder_Fiber | 198 | Hub/OLT↔Joint↔FDH |
| Distribution_Fiber | 1,260 | FDH↔Splitter |
| Drop_Fiber | 21,420 | Splitter↔Home_ONT |

Topology path:

`Internet_Source → Core_POP → Regional_Hub → OLT → Joint_Closure → FDH → Optical_Splitter → Home_ONT`

## Package contents

```
GeometricNetwork_ArcMap/
  shapefiles/
    GN_Junctions.shp      # all nodes (points, EPSG:32642)
    GN_Edges.shp          # all edges (lines, snapped to junctions)
    Junc_*.shp            # typed junction subsets
    Edge_*.shp            # typed edge subsets
  tables/
    GN_Junctions_Catalog.csv
    GN_Edges_Catalog.csv
    Connectivity_Rules.csv
    Network_Hierarchy.csv
    Summary_*.csv
    Dataset_Metadata.json
  MetroTel_FTTH_GeometricNetwork_Data.gpkg
  scripts/build_geometric_network_arcmap.py
  docs/ArcMap_GeometricNetwork_Build_Guide.md
```

CRS: **EPSG:32642** (WGS 84 / UTM zone 42N), meters — required for geometric network snapping.

Shapefile field notes (10-char limit):

| Full name | Shapefile field |
|-----------|-----------------|
| JunctionID | JunctionID |
| JuncType | JuncType |
| AncillaryRole | AncillaryR (1=Source, 2=Sink, 0=None) |
| EdgeID | EdgeID |
| FromID / ToID | FromID / ToID |
| FlowDirection | FlowDirect |

## Method A — ArcPy (recommended)

1. Copy this folder to a local path, e.g. `C:\GIS_Telecom_Training\Day4_Fiber_Microwave\GeometricNetwork_ArcMap`.
2. Edit `DATA_ROOT` at the top of `scripts/build_geometric_network_arcmap.py`.
3. Run with ArcGIS Desktop Python 2.7, or paste into the ArcMap Python window.
4. Output: `gdb/MetroTel_FTTH_GN.gdb` → feature dataset `FD_FTTH` → geometric network `GN_MetroTel_FTTH`.

## Method B — Manual in ArcMap (step-by-step)

### 1. Create geodatabase & feature dataset

1. Open **ArcCatalog** (or Catalog window in ArcMap).
2. Create File Geodatabase: `MetroTel_FTTH_GN.gdb`.
3. Right-click GDB → **New → Feature Dataset** → name `FD_FTTH`.
4. Import coordinate system: **Projected → UTM → WGS 1984 → Northern Hemisphere → WGS 1984 UTM Zone 42N**.

### 2. Load junctions and edges

1. Right-click `FD_FTTH` → **Import → Feature Class (multiple)**.
2. Add:
   - `shapefiles/GN_Junctions.shp`
   - `shapefiles/GN_Edges.shp`
3. Confirm both feature classes are inside `FD_FTTH` and share the same CRS.

Optional (complex network with typed classes): import `Junc_*.shp` and `Edge_*.shp` instead, then include all classes when building the geometric network.

### 3. Create Geometric Network

1. Right-click `FD_FTTH` → **New → Geometric Network**.
2. Name: `GN_MetroTel_FTTH`.
3. Select features:
   - `GN_Junctions` → **Simple Junction**
   - `GN_Edges` → **Simple Edge**
4. Snap tolerance: **0.5 meters**.
5. Do **not** exclude any features for this training set.
6. Finish the wizard.

### 4. Sources and sinks (Ancillary Roles)

Geometric Network uses ancillary roles for flow:

| Role | Value in `AncillaryR` | Features |
|------|----------------------:|----------|
| Source | 1 | Internet_Source (3) |
| Sink | 2 | Home_ONT (21,420) |
| None | 0 | Core, Hub, OLT, Joint, FDH, Splitter |

In ArcMap:

1. Open **Utility Network Analyst** toolbar (`Customize → Toolbars → Utility Network Analyst`).
2. Set the geometric network target to `GN_MetroTel_FTTH`.
3. Select Internet_Source junctions (`JuncType = 'Internet_Source'`) → set as **Source**.
4. Select Home_ONT junctions (`JuncType = 'Home_ONT'`) → set as **Sink** (or rely on digitized direction + Set Flow Direction).
5. **Utility Network Analyst → Flow → Set Flow Direction** → With Digitized Direction (edges were built Source→Home).

### 5. Connectivity rules (conceptual)

Use `tables/Connectivity_Rules.csv` when defining rules in the geometric network:

- Internet_Source —Backbone→ Core_POP  
- Core_POP —Backbone→ Regional_Hub  
- Regional_Hub —Feeder→ OLT  
- OLT —Feeder→ Joint_Closure —Feeder→ FDH  
- FDH —Distribution→ Optical_Splitter  
- Optical_Splitter —Drop→ Home_ONT  

### 6. Training traces

| Exercise | Tool | Start | Expected result |
|----------|------|-------|-----------------|
| Connected plant | Find Connected | CORE-01 | Large connected component |
| Downstream customers | Trace Downstream | OLT-01 | FDHs → splitters → homes under that OLT |
| Upstream path | Trace Upstream | any ONT-* | Splitter → FDH → Joint → OLT → Hub → Core → Source |
| Isolation | Disable edge | cut a Feeder_Fiber | Downstream homes lose connectivity |
| Redundancy | Find Path / Loops | Core ring / Hub ring | Alternate backbone path |

### 7. Symbology tips

- Junctions by `JuncType` (unique values); enlarge Core/OLT/FDH; small points for Home_ONT.
- Edges by `EdgeType`; thicker for Backbone/Feeder; thin for Drop_Fiber.
- Definition query for overview maps: `JuncType <> 'Home_ONT'` or show only Levels 0–4.
- For performance in ArcMap with 21k homes: use scale-dependent rendering (show Home_ONT only below 1:5,000).

## Important ArcMap vs ArcGIS Pro note

- **Geometric Network** = ArcGIS Desktop (ArcMap) classic utility model.
- **Utility Network** = ArcGIS Pro / Enterprise (different schema).
- This package is built for **ArcMap Geometric Network**. In Pro, import the same shapefiles/GPKG as feature classes and analyze connectivity with Trace Network or a simplified Utility Network — do not expect the `.gdb` geometric network binary to open unchanged in Pro.

## Synthetic scenario

**MetroTel Capital Region** — multi-source internet distribution to FTTH end-users for GIS telecom training. Coordinates are synthetic training geometry (not a live carrier inventory).
