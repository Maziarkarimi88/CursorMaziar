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

### Tests (no Earth Engine login required)

```bash
node --check gee/wheat_phenology_mapping.js
node --check gee/client_helpers.js
node gee/test_client_logic.js
```
