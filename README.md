# CursorMaziar

## Wheat phenology mapping (Google Earth Engine)

The original Code Editor script did not run. The fixed app is in `gee/wheat_phenology_mapping.js`.

### Run in Earth Engine

1. Open [Earth Engine Code Editor](https://code.earthengine.google.com/).
2. Paste the contents of `gee/wheat_phenology_mapping.js`.
3. Click **Run**.
4. Set **Geometry Assets Folder** to a folder with one subfolder per province. Each province folder should contain:
   - `<Province>_Ag_IR` or `<Province>_Ag_RF`
   - `<Province>_Wheat_IR` or `<Province>_Wheat_RF`
5. Pick a province and IR/RF, then use **Show Overall Phenology**, the sample-point list, or zoom in and click the map.

You can still click the map (zoom ≥ 9) to chart NDVI phenology at an arbitrary point if the SERVIR province assets are not shared with your account.

### What was broken

- Earth Engine widget styles used CSS kebab-case (`fontWeight` is required).
- Asset folder listing crashed when the folder was missing or private.
- Map layers were removed with a dictionary-style get call instead of `getName()`.
- Deprecated Sentinel-2 L1C collection ID; the app now uses `COPERNICUS/S2_HARMONIZED`.
- Sample-point buttons were created disabled, so list selection did nothing.
- Monthly composites used browser `Date` objects and could skip months or loop.
- Linear/harmonic regression ran on unclipped Sentinel-2 granules and often timed out.

### Interactive app (province, IR/RF, dates)

`gee/wheat_phenology_app.js` is the original-style interface pointed at:

`projects/ee-maziarkarimi3/assets/Wheat_Mapping`

This matches MODULE 1: **Show Overall Phenology** draws one NDVI/harmonic line per GPS sample. Click a sample in the list (or on the map) to see that point’s four charts plus monthly false-color Sentinel-2 chips.

Select a province, **IR** or **RF**, and a date range, then click **Show Overall Phenology**. The app loads:

- `{root}/Admin/{Province}`
- `{root}/IR_RF/{Province}_Ag_{IR|RF}`
- `{root}/GCP/{Province}_{IR|RF}_GCP`

It charts NDVI and reports sowing / peak / harvest values at the wheat GCPs. Delete non-wheat samples here, then continue with MODULE 2 to merge remaining quality wheat GPS and split training/validation points.

### Nangarhar irrigated wheat (your assets)

`gee/nangarhar_wheat_phenology.js` uses Tiwari et al. (2020) seasonal NDVI composites at sowing, peak and harvest:

- AOI: `projects/ee-maziarkarimi3/assets/Wheat_Mapping/Admin/Nangarhar`
- Irrigated agriculture: `projects/ee-maziarkarimi3/assets/Wheat_Mapping/IR_RF/Nangarhar_Ag_IR`
- Wheat GCPs: `projects/ee-maziarkarimi3/assets/Wheat_Mapping/GCP/Nangarhar_IR_GCP`

Paste that file, select Cloud project `ee-maziarkarimi3`, and click Run. Charts appear on the left; Console prints mean/min/max NDVI for each season and a per-GCP table.

### MODULE 2 — GCP preprocessing (train / validation split)

`gee/wheat_gcp_preprocess_app.js` is the Module 2 interface on the same assets as Module 1. After Module 1, use it to visualize the agriculture mask and GPS points, optionally merge quality-wheat GCPs, split 70/30 training/validation, and export.

1. Paste `gee/wheat_gcp_preprocess_app.js` (replace the entire editor, do not merge with Module 1).
2. Select Cloud project `ee-maziarkarimi3` and click **Run**.
3. Pick a province and **IR** or **RF**. The agriculture mask and Sample GCP layers load.
4. Optional: paste an additional GPS **folder** of point tables, or one FeatureCollection (quality wheat remaining from Module 1).
5. Click **Merge all GCP and split to training/validation datasets**. Training points are red; validation points are green.
6. Click **Export**. Open **Tasks** and click **RUN** on each queued job (Drive SHP plus Earth Engine Assets under `GCP/`).

Asset IDs written for later modules:

- `{root}/GCP/{Province}_{IR|RF}_GCP_MERGED`
- `{root}/GCP/{Province}_{IR|RF}_GCP_TRAIN`
- `{root}/GCP/{Province}_{IR|RF}_GCP_VALIDATE`

### Tests (no Earth Engine login required)

```bash
node --check gee/wheat_phenology_mapping.js
node --check gee/nangarhar_wheat_phenology.js
node --check gee/wheat_phenology_app.js
node --check gee/wheat_gcp_preprocess_app.js
node --check gee/client_helpers.js
node gee/test_client_logic.js
```
