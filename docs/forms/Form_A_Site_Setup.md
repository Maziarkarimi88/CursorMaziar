# Form A — Site setup and gauge survey

**بند چک / Check dam ID:** ______________  
**Wadi / fan:** ______________ **Province / district:** ______________  
**Treated or control:** ☐ Treated ☐ Control  
**Date:** ______________ **Observers:** ______________

## A1. Structure

| Item | Value |
|------|--------|
| Type (masonry / gabion / earth) | |
| Crest length (m) | |
| Crest height above bed (m) | |
| Year built / implementing agency | |
| Cascade position (1 = most upstream) | of |
| Pond used for irrigation pumping? | ☐ No ☐ Yes — exclude those days from MDWIR |
| Bed material at survey (gravel / sand / silt / rock) | |

Sketch north arrow, spillway, staff gauge, BM, village, karez:

```
[                                        ]
```

## A2. Staff gauge and benchmark

| Item | Value |
|------|--------|
| Gauge ID | SG- |
| Gauge zero description (pond bed / other) | |
| Crest reading on gauge (m) | |
| BM description | |
| Level: BM minus gauge zero (m) | |
| GPS of gauge (lat, lon, m asl) | |
| GPS of BM | |
| Photo IDs | |

## A3. Rain gauge

| Item | Value |
|------|--------|
| Diameter (mm) | |
| Height above ground (m) | |
| Distance to nearest obstacle (m) / obstacle height (m) | |
| GPS | |

## A4. Stage–area–volume (pond only, not the catchment)

**Method:** ☐ tape + level on empty pond  ☐ ArcGIS DEM Surface Volume / Storage Capacity  
DEM name / cell size (m): ______________  
\(Z_{\mathrm{bed}}\) (m a.s.l.): ______________  \(Z_{\mathrm{crest}}=Z_{\mathrm{bed}}+H\) (m a.s.l.): ______________  
Crest height \(H\) (2–6 m): ______________  Dam axis / zone polygon IDs: ______________

Contour interval: ________ m. GIS increment should be 0.5 m (0.25 m if the valley is wide).

Height \(h\) is **above the pond bed**, up to **this dam’s crest only**. Do not compute volume for the whole catchment.

| Stage h (m) | Area A (m²) | ΔV (m³) | Cumulative V (m³) |
|-------------|-------------|---------|-------------------|
| 0.00 (bed) | 0 | 0 | 0 |
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |
| (crest = 100% full) | | | |

Copy this table into workbook sheet `StageAreaVolume`.  
Storage at crest \(V_{\text{crest}}\) = ________ m³. Full-supply area = ________ m².  
See `docs/ARCGIS_STORAGE_FROM_DEM.md`.

## A5. Observation points (GPS, owner, rim height, type)

| ID | Type (W-N/W-M/W-F/C/KS/KO) | Owner / village | Lat | Lon | Rim above GL (m) | Well depth (m) | Notes |
|----|----------------------------|-----------------|-----|-----|------------------|----------------|-------|
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |
| | | | | | | | |

Karez name: ______________ Length estimate (km): ______________  
*Sarchah* depth (m): ______________ *Owkura* description: ______________

## A6. Catchment and design hold (rainfall to fill; 1–3 month target)

See `docs/STORAGE_DURATION_AND_FILLING.md` and workbook sheet `FillAndHold`.

| Item | Value |
|------|--------|
| Catchment area (ha) | |
| How mapped (topo / DEM / walk) | |
| Land cover (rock / rangeland / farm / mixed) | |
| Curve number CN (first guess) | |
| Runoff coefficient C (first guess) | |
| Design hold when full (months) | ☐ 1 ☐ 2 ☐ 3 ☐ other: ____ |
| Wall type vs hold (masonry/earth vs gabion) | |
| Low-level drain normally | ☐ Closed ☐ Open |

## A7. Technician sign-off

Survey complete ☐  Observer trained ☐  Forms B–C issued ☐  
Signature / date: ______________
