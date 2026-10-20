# Pond storage from DEM in ArcGIS (Surface Volume / Storage Capacity)

**What you are measuring.** Storage of the **pond behind the wall**, at each water-surface height up to **that dam’s crest** (your structures are about **2–6 m** high). You are **not** filling the catchment. The catchment only supplies runoff. “100% full” means water at the **spillway / crest**, volume \(V(H_{\mathrm{crest}})\).

**What you need from GIS.** A table of **stage–area–volume**:

| Height above bed \(h\) (m) | Water-surface area \(A\) (m²) | Storage \(V\) (m³) |
|----------------------------|-------------------------------|---------------------|
| 0 | 0 | 0 |
| 0.5 | … | … |
| … | … | … |
| \(H_{\mathrm{crest}}\) (2–6 m) | \(A_{\mathrm{full}}\) | \(V_{\mathrm{crest}}\) = 100% |

Paste into workbook sheet `StageAreaVolume` (Form A4). Rainfall-to-fill then uses **this \(V_{\mathrm{crest}}\)**, not catchment area as a volume.

---

## 1. Why the dam wall and a zone polygon are mandatory

**Surface Volume** (3D Analyst) computes the space between a DEM and a **horizontal plane**. If you run it on the whole catchment DEM at “bed + 4 m”, the tool will count **every cell in the map that is below that elevation** — hillsides, the next valley, everything — not the check-dam pond.

You must:

1. Know the **dam axis** (cross-section at the wall) and **crest height** 2–6 m above the thalweg (or surveyed crest elevation in metres a.s.l.).
2. Restrict the calculation to the **upstream bowl** that the wall actually closes (a **zone** / reservoir polygon, or a DEM with the wall “burned in”).

The dam **cross-section** tells you wall length and maximum height. The **DEM of the valley upstream** tells you how the water surface spreads as \(h\) rises. Together they give \(A(h)\) and \(V(h)\).

---

## 2. Data and accuracy (2–6 m dams)

| Input | Role | Practical note |
|-------|------|----------------|
| DEM | Valley topography | **Cell size should be much smaller than the pond.** For a 2–6 m dam, **1–5 m** DEM is usable; **30 m SRTM/Copernicus is often too coarse** (one cell can be wider than the wadi, vertical error similar to dam height). UAV / stereo / Pleiades / national 5–12.5 m DEM is the right class. |
| Dam location | Polyline on the wall | GPS or georeferenced design drawing |
| Crest height | 2–6 m above bed, **per dam** | Field: staff + bed; or design drawing. Convert to **absolute elevation**: \(Z_{\mathrm{crest}} = Z_{\mathrm{bed}} + H\) |
| Cross-section at dam | Width, bed, banks | Check that GIS inundation width at crest matches the surveyed section |
| Projection | Metric (UTM) | Do not compute volume in geographic degrees. Set **Z factor = 1** if X,Y,Z are all metres |

Vertical error of the DEM should be **small compared with \(H\)**. If RMSE is 3–5 m and the dam is 2 m, GIS \(V\) is not reliable until you have a better DEM or a field survey.

---

## 3. Prepare the “bowl” (do this once per dam)

### 3.1 Raise the dam in the DEM (recommended)

The wall is a barrier. On the raw DEM the wadi is an open channel, so water “spills” downstream in the raster.

1. Digitise the dam as a polyline (crest).
2. Convert to raster (same cell size as DEM). Assign cell values = \(Z_{\mathrm{crest}}\).
3. **Mosaic** / `Con` : DEM_dam = max(DEM, dam_raster) along the wall (or replace those cells).
4. Optional: thicken the wall to 2–3 cells so it does not leak through diagonals.

This creates a closed depression upstream. That depression **is** the pond.

### 3.2 Zone polygon (required for Storage Capacity; useful for Surface Volume)

Delineate the land that can be inundated **upstream of the wall** and **below \(Z_{\mathrm{crest}}\)**:

- Clip DEM to a generous buffer upstream of the dam, **or**
- `Con(DEM < Z_crest, 1)` inside the upstream catchment, convert to polygon.

This polygon is the **zone**. It is **not** the whole watershed. The watershed can be tens of km²; the pond at 4 m might be a few hectares.

---

## 4. Tool A — Storage Capacity (Spatial Analyst) — best if you have ArcGIS Pro

[Storage Capacity](https://pro.arcgis.com/en/pro-app/latest/tool-reference/spatial-analyst/storage-capacity.htm) was built for reservoirs: it writes **ELEVATION, AREA, VOLUME** at set increments.

1. Input surface raster = DEM with dam burned in (or clipped bowl).
2. Input zone = reservoir polygon (one feature per check dam; zone field = Dam ID).
3. Analysis type = **Area and Volume**.
4. Minimum elevation = \(Z_{\mathrm{bed}}\) (thalweg at the wall, from DEM min in the zone **or** field).
5. Maximum elevation = \(Z_{\mathrm{crest}}\) = bed + **2 to 6 m** (that dam only).
6. Increment type = **Value of Increment**; Increment = **0.5 m** (0.25 m if the valley is wide and shallow).
7. Z unit = **Meter**.
8. Output table + optional elevation–area and elevation–volume charts.

Convert ELEVATION to **height above bed**: \(h = Z - Z_{\mathrm{bed}}\). The last row is **100% storage** for that dam.

Python sketch:

```python
import arcpy
from arcpy.sa import StorageCapacity

StorageCapacity(
    in_surface_raster="DEM_with_dam.tif",
    out_table="storage_by_dam",
    in_zone_data="pond_zones",
    zone_field="DamID",
    analysis_type="AREA_VOLUME",
    min_elevation=None,          # or Z_bed
    max_elevation=None,          # or Z_crest
    increment_type="VALUE_OF_INCREMENT",
    increment=0.5,
    z_unit="METER",
)
```

If min/max are left default, the tool uses zonal min/max of the DEM. Then **clip the table** to \(h \le H_{\mathrm{crest}}\). Do not take volume at the highest hill in the zone — that is not the dam.

---

## 5. Tool B — Surface Volume (3D Analyst) — what you named

[Surface Volume](https://pro.arcgis.com/en/pro-app/latest/tool-reference/3d-analyst/surface-volume.htm) is one plane at a time. Use **Below the plane**.

For each water height \(h = 0.5, 1.0, \ldots, H_{\mathrm{crest}}\):

1. Clip DEM (with dam burned in) to the **pond zone**.
2. Plane height \(Z = Z_{\mathrm{bed}} + h\) (absolute metres).
3. `SurfaceVolume`: input surface = clipped DEM (or TIN), **reference_plane = BELOW**, **plane_height = Z**, z_factor = 1.
4. Read **2D Area** → \(A(h)\), **Volume** → \(V(h)\).

Loop in ModelBuilder or `arcpy.ddd.SurfaceVolume`. Same idea as GIS Stack Exchange “volume in basin vs incremental dam height”.

**TIN option:** convert the clipped DEM to TIN, then Surface Volume on the TIN (smoother on a V-shaped wadi).

**Check:** \(V\) must **increase** with \(h\). If it jumps when \(h\) exceeds a saddle, the zone leaked around the abutment — extend the wall raster into both banks.

---

## 6. Tool C — raster sum (no 3D Analyst)

For each \(Z\):

\[
V=\sum_{\mathrm{cells}:\, z_i < Z,\,\mathrm{in\,zone}} (Z-z_i)\,\Delta x\,\Delta y
\]

\[
A=N_{\mathrm{wet}}\,\Delta x\,\Delta y
\]

`Raster Calculator` / `Con` + `Zonal Statistics as Table`. This is the same physics as Surface Volume.

---

## 7. Use the dam cross-section as a quality check

At the wall, a surveyed cross-section gives width \(W\) at each height. A crude prism:

\[
V_{\mathrm{approx}}\approx \tfrac{1}{2}\,W_{\mathrm{crest}}\,H\,L_{\mathrm{pond}}
\]

\(L_{\mathrm{pond}}\) = length of inundation up the wadi at crest (from the GIS water polygon). If GIS \(V_{\mathrm{crest}}\) differs from this by a **factor of several**, the zone leaked, the DEM missed the thalweg, or crest height is wrong. For a U-shaped gravel wadi the factor vs a triangle is often 1.2–2; a factor of 10 is an error.

---

## 8. What “100% full” is, and what it is not

| Phrase | Meaning |
|--------|---------|
| 100% of **check-dam storage** | Water surface at **crest / spillway** of that dam (2 m, 4 m, or 6 m). \(V = V(H_{\mathrm{crest}})\) from the table above. |
| 100% of the **catchment** | **Not used.** You never flood the watershed. Catchment area \(A_c\) only converts rainfall to **runoff volume**. |

Rainfall to reach 100% (still):

\[
P_{\mathrm{fill}}\approx\frac{V(H_{\mathrm{crest}})}{C\,A_c}
\]

or SCS-CN with \(Q = V(H_{\mathrm{crest}})/A_c\) (see `docs/STORAGE_DURATION_AND_FILLING.md` and sheet `FillAndHold`). Different dams (2 m vs 6 m) have **different** \(V_{\mathrm{crest}}\) even on the same wadi.

Hold time still uses \(V(h)\) and \(A(h)\) as stage falls: that is why you need the **whole curve**, not only the crest row.

---

## 9. Deliverables into the field workbook

1. Export GIS table → columns: `h_m`, `A_m2`, `V_m3`.
2. Paste into `StageAreaVolume` (stage, area); volume column can stay as trapezoid **or** you overwrite with GIS \(V\) if you trust it more.
3. Site sheet: crest stage = \(H_{\mathrm{crest}}\) (m on the gauge, same as GIS \(h\) at full).
4. Form A4: tick **DEM / ArcGIS Surface Volume** and record DEM name, cell size, \(Z_{\mathrm{bed}}\), \(Z_{\mathrm{crest}}\).

After heavy siltation, the DEM of the **bed** is wrong; re-survey silt (Form D) or a new UAV DEM.

---

## 10. Short references

- Esri. *Surface Volume (3D Analyst)* — area and volume between a surface and a plane (use **Below**).
- Esri. *Storage Capacity (Spatial Analyst)* — elevation, area, and volume increments for a reservoir **zone**.
- GIS Stack Exchange: “Volume of water in basin with reference to incremental height of DAM” — loop Surface Volume by plane height.
- Dashora et al. (2018, 2019) — once \(A(h), V(h)\) exist, daily stage → recharge; GIS replaces the tape survey, not the water-balance step.
