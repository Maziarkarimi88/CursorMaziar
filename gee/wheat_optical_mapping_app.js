/**
 * MODULE 3 — Wheat mapping with Sentinel-2 optical thresholds.
 *
 * Continuation of MODULE 1 (phenology) and MODULE 2 (GCP split).
 * Composite sowing / peak / harvest images, compute NDVI (and peak NDSI),
 * apply phenology thresholds, inspect pixels, and export the wheat mask.
 *
 * Your asset layout (same as Modules 1–2):
 *   {root}/Admin/{Province}
 *   {root}/IR_RF/{Province}_Ag_{IR|RF}
 *   {root}/GCP/{Province}_{IR|RF}_GCP
 *
 * Create an Optical folder once, then Export writes:
 *   {root}/Optical/{Province}_{IR|RF}_NDVI_SOWING
 *   {root}/Optical/{Province}_{IR|RF}_NDVI_PEAK
 *   {root}/Optical/{Province}_{IR|RF}_NDSI_PEAK
 *   {root}/Optical/{Province}_{IR|RF}_NDVI_HARVEST
 *   {root}/Optical/{Province}_{IR|RF}_FINAL_MASK
 *
 * Defaults follow Module 1 Tiwari windows. The MODULE 3 PDF Kabul
 * exercise used sowing 2016-11-15–2016-12-30 (0–0.15), peak
 * 2017-05-01–2017-05-30 (min 0.30), harvest 2017-07-11–2017-07-20
 * (0.03–0.34). Change dates from your Module 1 phenology charts.
 *
 * How to run:
 * 1. Open https://code.earthengine.google.com/ and sign in.
 * 2. Profile menu > Change Cloud Project > ee-maziarkarimi3
 * 3. If Run/Save/Get Link are gray, register at
 *    https://code.earthengine.google.com/register then reload.
 * 4. Replace the entire editor contents with this script and click Run.
 * 5. Select province + IR/RF, tick seasons, Compute each, then Export.
 * 6. Open Tasks and click RUN. Create the Optical folder if prompted.
 */

var app = {};

app.createConstants = function() {
  app.DEFAULT = {
    ASSET_SOURCE: 'projects/ee-maziarkarimi3/assets/Wheat_Mapping',
    S2_COLLECTION: 'COPERNICUS/S2_HARMONIZED',
    SCALE: 10,
    SAMPLE_SCALE: 10,
    SO: {
      START_DATE: '2016-11-15',
      END_DATE: '2016-12-31',
      CLOUD_COVER: 30,
      FILTER: 'Median',
      MIN_NDVI: 0,
      MAX_NDVI: 0.15
    },
    PS: {
      START_DATE: '2017-02-01',
      END_DATE: '2017-03-31',
      CLOUD_COVER: 30,
      FILTER: 'Median',
      MIN_NDVI: 0.3
    },
    HAR: {
      START_DATE: '2017-05-01',
      END_DATE: '2017-06-15',
      CLOUD_COVER: 30,
      FILTER: 'Median',
      MIN_NDVI: 0.03,
      MAX_NDVI: 0.34
    }
  };
  app.RANGE = {
    SO_NDVI: [0, 0.5],
    PS_NDVI: [0.2, 1],
    HAR_NDVI: [0, 0.5]
  };
  app.LABEL = {
    TITLE: 'Wheat Optical Mapping',
    ASSET_SOURCE: 'Geometry Assets Folder',
    PROVINCE: 'Select Province',
    SEASONS: 'Seasons',
    SOWING: 'Sowing',
    PEAK: 'Peak',
    HARVEST: 'Harvesting',
    SO_MAIN: 'Sowing Season',
    PS_MAIN: 'Peak Season',
    HAR_MAIN: 'Harvest Season',
    EXPORT: 'Export',
    START: 'Start Date',
    END: 'End Date',
    CLOUD: 'Cloud Cover',
    FILTER: 'Filter',
    NDVI: 'NDVI Threshold',
    MIN: 'Min',
    MAX: 'Max',
    MIN_NDVI: 'Min NDVI',
    COMPUTE: 'Compute'
  };
  app.TEXT = {
    EXPORT: {
      NDVI_SO: 'NDVI Sowing Season',
      NDVI_PS: 'NDVI Peak Season',
      NDSI_PS: 'NDSI Peak Season',
      NDVI_HAR: 'NDVI Harvesting',
      FINAL_MASK: 'Final Mask'
    },
    INSPECT: {
      MAIN_LABEL: 'Inspector',
      LAT_LONG: 'Lat, Long',
      NDVI_SO: 'NDVI Sowing',
      NDVI_PS: 'NDVI Peak',
      NDSI_PS: 'NDSI Peak',
      NDVI_HAR: 'NDVI Harvesting'
    }
  };
  app.LAYER = {
    AGRI: 'Agriculture Mask',
    GCP: 'Sample GCP',
    SO_FCC: 'Sowing FCC',
    SO_NDVI: 'NDVI Sowing',
    SO_TH: 'NDVI Sowing Threshold',
    PS_FCC: 'Peak FCC',
    PS_NDVI: 'NDVI Peak',
    PS_TH: 'NDVI Peak Threshold',
    PS_COMBINE: 'Sowing Peak Combined Mask',
    HAR_FCC: 'Harvest FCC',
    HAR_NDVI: 'NDVI Harvest',
    HAR_TH: 'NDVI Harvest Threshold',
    HAR_COMBINE: 'Sowing Peak Harvest Combined Mask',
    ZOOM: 'Zoom Box Bounds'
  };
  app.PATH = {
    ADMIN: 'Admin',
    AGRI: 'IR_RF',
    GCP: 'GCP',
    OPTICAL: 'Optical'
  };
  app.ERROR = {
    MISSING_DATA: 'Error! Some data are missing',
    STH_WRONG: 'Something went wrong! Please re-check parameters and try again.',
    NO_AGRI_BOUNDS: 'Please make sure you have selected Province and IR or RF',
    NDVI_RANGE: 'NDVI values should be within the range ',
    NO_FILES: 'Files not found! Please make sure the required files exist!',
    NO_FOLDER: 'Could not list provinces. Check the folder path and that you have access.',
    NO_IMAGES: 'No Sentinel-2 images found for these filters.',
    NO_EXPORT: 'Select at least one computed layer to export.',
    NO_MASK: 'Compute at least one season before exporting the final mask.'
  };
  app.FILTERS = ['Mean', 'Median', 'Mode', 'Max', 'Min'];
  app.vis = {
    min: 0,
    max: 1,
    palette: [
      'FFFFFF', 'CE7E45', 'FCD163', '66A000', '207401',
      '056201', '004C00', '023B01', '012E01', '011301'
    ]
  };
  app.falseColor = {
    bands: ['B8', 'B4', 'B3'],
    min: 500,
    max: 3000,
    gamma: [1, 1, 1]
  };
};

app.createHelpers = function() {
  app.assetShortName = function(assetId) {
    if (!assetId) return '';
    var parts = String(assetId).replace(/\/+$/, '').split('/');
    return parts[parts.length - 1];
  };

  app.isProvinceAssetType = function(type) {
    var t = String(type || '').toUpperCase().replace(/ /g, '_');
    return t === 'FOLDER' || t === 'TABLE' || t === 'FEATURE_COLLECTION' ||
      t === 'FEATURECOLLECTION' || t === 'ASSET';
  };

  app.collectProvinceNames = function(assets) {
    var list = Array.isArray(assets) ? assets : (assets && assets.assets) || [];
    var ids = [];
    for (var i = 0; i < list.length; i++) {
      var element = list[i] || {};
      if (!app.isProvinceAssetType(element.type)) continue;
      var name = app.assetShortName(element.id || element.name || '');
      if (name && ids.indexOf(name) === -1) ids.push(name);
    }
    return ids.sort();
  };

  app.buildWheatAssetIds = function(root, province, irrf) {
    var base = String(root || '').replace(/\/+$/, '');
    var prov = String(province || '');
    var kind = String(irrf || 'IR');
    return {
      aoi: base + '/' + app.PATH.ADMIN + '/' + prov,
      agri: base + '/' + app.PATH.AGRI + '/' + prov + '_Ag_' + kind,
      gcp: base + '/' + app.PATH.GCP + '/' + prov + '_' + kind + '_GCP'
    };
  };

  app.opticalExportDescriptions = function(province, irrf) {
    var prov = String(province || 'Province').replace(/[^\w]+/g, '_');
    var kind = String(irrf || 'IR');
    var prefix = prov + '_' + kind + '_';
    return {
      ndviSowing: prefix + 'NDVI_SOWING',
      ndviPeak: prefix + 'NDVI_PEAK',
      ndsiPeak: prefix + 'NDSI_PEAK',
      ndviHarvest: prefix + 'NDVI_HARVEST',
      finalMask: prefix + 'FINAL_MASK'
    };
  };

  app.buildOpticalAssetIds = function(root, province, irrf) {
    var base = String(root || '').replace(/\/+$/, '');
    var names = app.opticalExportDescriptions(province, irrf);
    var folder = base + '/' + app.PATH.OPTICAL + '/';
    return {
      ndviSowing: folder + names.ndviSowing,
      ndviPeak: folder + names.ndviPeak,
      ndsiPeak: folder + names.ndsiPeak,
      ndviHarvest: folder + names.ndviHarvest,
      finalMask: folder + names.finalMask
    };
  };

  app.isValidIsoDate = function(value) {
    if (!/^\d{4}-\d{2}-\d{2}$/.test(String(value))) return false;
    var parts = String(value).split('-');
    var year = parseInt(parts[0], 10);
    var month = parseInt(parts[1], 10);
    var day = parseInt(parts[2], 10);
    if (month < 1 || month > 12 || day < 1 || day > 31) return false;
    var dt = new Date(Date.UTC(year, month - 1, day));
    return dt.getUTCFullYear() === year &&
      dt.getUTCMonth() === month - 1 &&
      dt.getUTCDate() === day;
  };

  app.parseNumericField = function(value) {
    if (value === null || value === undefined || value === '') return NaN;
    return typeof value === 'number' ? value : parseFloat(value);
  };

  app.compositeReducerName = function(filter) {
    var f = String(filter || 'Median');
    if (f === 'Mean' || f === 'Mode' || f === 'Max' || f === 'Min') return f;
    return 'Median';
  };

  app.ndviPairInRange = function(minNdvi, maxNdvi, range) {
    var minN = app.parseNumericField(minNdvi);
    var maxN = app.parseNumericField(maxNdvi);
    if (isNaN(minN) || isNaN(maxN) || minN > maxN) return false;
    if (!range || range.length < 2) return true;
    return minN >= range[0] && maxN <= range[1];
  };

  app.ndviMinInRange = function(minNdvi, range) {
    var minN = app.parseNumericField(minNdvi);
    if (isNaN(minN)) return false;
    if (!range || range.length < 2) return true;
    return minN >= range[0] && minN <= range[1];
  };

  app.opticalSeasonInputsValid = function(opts) {
    opts = opts || {};
    if (!app.isValidIsoDate(opts.startDate) || !app.isValidIsoDate(opts.endDate) ||
        opts.startDate >= opts.endDate) {
      return false;
    }
    var cloudNum = app.parseNumericField(opts.cloud);
    if (isNaN(cloudNum) || cloudNum < 0 || cloudNum > 100) return false;
    if (!opts.filter) return false;
    if (opts.requireMax) return app.ndviPairInRange(opts.minNdvi, opts.maxNdvi, opts.range);
    return app.ndviMinInRange(opts.minNdvi, opts.range);
  };

  app.chooseFinalMaskLayer = function(hasHarvest, hasPeak, hasSowing) {
    if (hasHarvest) return 'harvest';
    if (hasPeak) return 'peak';
    if (hasSowing) return 'sowing';
    return null;
  };

  app.prompt = function(state, txt) {
    app.promptText.setValue(txt || '');
    app.promptText.style().set('shown', state);
  };

  app.setBusy = function(state) {
    if (state) app.prompt(true, 'Loading...');
    else app.prompt(false, '');
    app.bo.provincePicker.setDisabled(state);
    app.bo.irRfPicker.setDisabled(state);
    app.bo.soCheckBox.setDisabled(state);
    app.bo.psCheckBox.setDisabled(state);
    app.bo.harCheckBox.setDisabled(state);
    app.so.button.setDisabled(state);
    app.ps.button.setDisabled(state);
    app.har.button.setDisabled(state);
    app.ex.export.setDisabled(state);
  };

  app.listFolderAssets = function(folderId, callback) {
    var finished = false;
    var finish = function(assets, error) {
      if (finished) return;
      finished = true;
      callback(assets, error);
    };
    try {
      ee.data.listAssets(folderId, {}, function(result, error) {
        if (!error && result) {
          finish(result.assets || [], null);
          return;
        }
        ee.data.getList({id: folderId}, function(list, err2) {
          if (err2 || list == null) {
            finish([], error || err2 || 'Unable to list assets');
            return;
          }
          finish(Array.isArray(list) ? list : (list.assets || []), null);
        });
      });
    } catch (err) {
      finish([], String(err));
    }
  };

  app.loadTable = function(assetId, callback) {
    if (!assetId) {
      callback(null, 'missing');
      return;
    }
    var fc = ee.FeatureCollection(assetId);
    fc.size().evaluate(function(n, error) {
      if (error || n === null || n === undefined) {
        callback(null, error || 'missing');
        return;
      }
      callback(fc, null);
    });
  };

  app.removeLayers = function(names) {
    var findAndRemove = function(mapLayers) {
      var toRemove = [];
      for (var i = 0; i < mapLayers.length(); i++) {
        var layer = mapLayers.get(i);
        if (names.indexOf(layer.getName()) > -1) toRemove.push(layer);
      }
      for (var j = 0; j < toRemove.length; j++) mapLayers.remove(toRemove[j]);
    };
    findAndRemove(Map.layers());
    if (app.zp && app.zp.zoomBox) findAndRemove(app.zp.zoomBox.layers());
  };

  app.addLayer = function(features, args, name, show) {
    var visible = show !== false;
    Map.addLayer(features, args, name, visible);
    if (app.zp && app.zp.zoomBox) app.zp.zoomBox.addLayer(features, args, name, visible);
  };

  app.maskS2clouds = function(image) {
    var qa = image.select('QA60');
    var mask = qa.bitwiseAnd(1 << 10).eq(0).and(qa.bitwiseAnd(1 << 11).eq(0));
    return image.updateMask(mask).copyProperties(image, ['system:time_start']);
  };

  app.clipRegion = function() {
    return ee.FeatureCollection(app.geometry).geometry({maxError: 100}).simplify(100);
  };

  app.exportRegion = function() {
    return ee.FeatureCollection(app.geometry).geometry({maxError: 100}).bounds(100);
  };

  app.normalizeLonLatBox = function(west, south, east, north) {
    west = app.parseNumericField(west);
    south = app.parseNumericField(south);
    east = app.parseNumericField(east);
    north = app.parseNumericField(north);
    if (isNaN(west) || isNaN(south) || isNaN(east) || isNaN(north)) return null;
    if (south > north) {
      var swapLat = south;
      south = north;
      north = swapLat;
    }
    if (west > east) {
      var swapLon = west;
      west = east;
      east = swapLon;
    }
    if (west === east || south === north) return null;
    if (south < -90 || north > 90 || west < -180 || east > 180) return null;
    return {west: west, south: south, east: east, north: north};
  };

  app.flattenLonLatPairs = function(node, out) {
    out = out || [];
    if (!node) return out;
    if (typeof node[0] === 'number' && typeof node[1] === 'number') {
      out.push([app.parseNumericField(node[0]), app.parseNumericField(node[1])]);
      return out;
    }
    if (Object.prototype.toString.call(node) === '[object Array]') {
      for (var i = 0; i < node.length; i++) app.flattenLonLatPairs(node[i], out);
    }
    return out;
  };

  app.parseMapBounds = function(source) {
    if (!source) return null;
    if (source.bounds && source.bounds !== source) {
      var fromEvent = app.parseMapBounds(source.bounds);
      if (fromEvent) return fromEvent;
    }
    if (source.geometry && source.geometry !== source) {
      var fromGeom = app.parseMapBounds(source.geometry);
      if (fromGeom) return fromGeom;
    }
    if (source.bbox && source.bbox.length >= 4) {
      var fromBbox = app.normalizeLonLatBox(
        source.bbox[0], source.bbox[1], source.bbox[2], source.bbox[3]
      );
      if (fromBbox) return fromBbox;
    }
    if (source.west != null && source.south != null &&
        source.east != null && source.north != null) {
      return app.normalizeLonLatBox(source.west, source.south, source.east, source.north);
    }
    if (source.coordinates) {
      var pairs = app.flattenLonLatPairs(source.coordinates, []);
      if (pairs.length) {
        var west = pairs[0][0];
        var east = pairs[0][0];
        var south = pairs[0][1];
        var north = pairs[0][1];
        for (var i = 1; i < pairs.length; i++) {
          west = Math.min(west, pairs[i][0]);
          east = Math.max(east, pairs[i][0]);
          south = Math.min(south, pairs[i][1]);
          north = Math.max(north, pairs[i][1]);
        }
        return app.normalizeLonLatBox(west, south, east, north);
      }
    }
    if (Object.prototype.toString.call(source) === '[object Array]' &&
        source.length === 4 &&
        Object.prototype.toString.call(source[0]) !== '[object Array]') {
      return app.normalizeLonLatBox(source[0], source[1], source[2], source[3]);
    }
    return null;
  };

  app.readZoomBounds = function(event) {
    var box = app.parseMapBounds(event);
    if (box) return box;
    var raw = null;
    try {
      raw = app.zp.zoomBox.getBounds(true);
    } catch (errGeo) {
      raw = null;
    }
    box = app.parseMapBounds(raw);
    if (box) return box;
    try {
      raw = app.zp.zoomBox.getBounds(false);
    } catch (errList) {
      try {
        raw = app.zp.zoomBox.getBounds();
      } catch (errBare) {
        raw = null;
      }
    }
    return app.parseMapBounds(raw);
  };

  app.getCollection = function(startDate, endDate, cloudThreshold, region) {
    return ee.ImageCollection(app.DEFAULT.S2_COLLECTION)
      .filterDate(startDate, endDate)
      .filterBounds(region)
      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloudThreshold))
      .map(app.maskS2clouds)
      .map(function(image) {
        return image.select(['B8', 'B4', 'B3', 'B11']).clip(region)
          .copyProperties(image, ['system:time_start']);
      });
  };

  app.reduceCollection = function(col, metricType) {
    var name = app.compositeReducerName(metricType);
    if (name === 'Mean') return col.mean();
    if (name === 'Mode') return col.mode();
    if (name === 'Max') return col.max();
    if (name === 'Min') return col.min();
    return col.median();
  };

  app.getImage = function(startDate, endDate, cloudThreshold, metricType) {
    var region = app.clipRegion();
    var col = app.getCollection(startDate, endDate, cloudThreshold, region);
    return app.reduceCollection(col, metricType).clip(region);
  };

  app.getND = function(image, band1, band2) {
    var b1 = band1 || 'B8';
    var b2 = band2 || 'B4';
    var name = (b1 === 'B11' && b2 === 'B8') ? 'NDSI' : 'NDVI';
    return image.normalizedDifference([b1, b2]).rename(name);
  };

  app.applyThreshold = function(image, minVal, maxVal) {
    return image.gte(minVal).and(image.lte(maxVal));
  };

  app.applyMask = function(image, mask) {
    return image.updateMask(mask);
  };

  app.populatePickers = function() {
    var root = app.bo.assetSource.getValue();
    var adminFolder = String(root || '').replace(/\/+$/, '') + '/' + app.PATH.ADMIN;
    app.setBusy(true);
    app.listFolderAssets(adminFolder, function(assets, error) {
      var names = app.collectProvinceNames(assets);
      if (!names.length) names = ['Nangarhar'];
      app.bo.provincePicker.items().reset(names);
      app.setBusy(false);
      if (error && !assets.length) {
        app.prompt(true, app.ERROR.NO_FOLDER + ' Showing Nangarhar as a fallback.');
        print('Admin folder list error:', error);
      }
    });
  };

  app.onProvSelected = function() {
    if (app.bo.irRfPicker.getValue()) app.onBothSelected();
  };

  app.onIRRFSelected = function() {
    if (app.bo.provincePicker.getValue()) app.onBothSelected();
  };

  app.onBothSelected = function() {
    var ids = app.buildWheatAssetIds(
      app.bo.assetSource.getValue(),
      app.bo.provincePicker.getValue(),
      app.bo.irRfPicker.getValue()
    );
    app.setBusy(true);
    app.ndviSowingImage = null;
    app.ndviPeakImage = null;
    app.ndsiPeakImage = null;
    app.ndviHarvestImage = null;
    app.updateNdviSowing = null;
    app.psThresholdCombine = null;
    app.harThresholdCombine = null;
    app.ex.ndviSo.setDisabled(true);
    app.ex.ndviPs.setDisabled(true);
    app.ex.ndsiPs.setDisabled(true);
    app.ex.ndviHar.setDisabled(true);
    app.ex.finalMask.setDisabled(true);
    app.removeLayers([
      app.LAYER.AGRI, app.LAYER.GCP,
      app.LAYER.SO_FCC, app.LAYER.SO_NDVI, app.LAYER.SO_TH,
      app.LAYER.PS_FCC, app.LAYER.PS_NDVI, app.LAYER.PS_TH, app.LAYER.PS_COMBINE,
      app.LAYER.HAR_FCC, app.LAYER.HAR_NDVI, app.LAYER.HAR_TH, app.LAYER.HAR_COMBINE
    ]);
    print('Loading assets', ids);
    app.loadTable(ids.agri, function(agriFc, agriErr) {
      if (agriErr || !agriFc) {
        app.setBusy(false);
        app.prompt(true, app.ERROR.NO_FILES);
        return;
      }
      app.geometry = agriFc;
      app.addLayer(app.geometry, {color: 'ffd468'}, app.LAYER.AGRI, true);
      Map.centerObject(app.geometry, 8);
      app.loadTable(ids.gcp, function(gcpFc) {
        if (gcpFc) {
          app.addLayer(gcpFc, {color: 'red'}, app.LAYER.GCP, false);
        }
        app.setBusy(false);
      });
    });
  };

  app.soCheckChanged = function(checkedState) {
    app.soPanel.style().set('shown', checkedState);
    if (!checkedState) {
      app.ex.ndviSo.setValue(false);
      app.ex.ndviSo.setDisabled(true);
    }
  };

  app.psCheckChanged = function(checkedState) {
    app.psPanel.style().set('shown', checkedState);
    if (!checkedState) {
      app.ex.ndviPs.setValue(false);
      app.ex.ndviPs.setDisabled(true);
      app.ex.ndsiPs.setValue(false);
      app.ex.ndsiPs.setDisabled(true);
    }
  };

  app.harCheckChanged = function(checkedState) {
    app.harPanel.style().set('shown', checkedState);
    if (!checkedState) {
      app.ex.ndviHar.setValue(false);
      app.ex.ndviHar.setDisabled(true);
    }
  };

  app.readSeasonInputs = function(panel, requireMax, range) {
    return {
      startDate: panel.startDate.getValue(),
      endDate: panel.endDate.getValue(),
      cloud: panel.cloudCover.getValue(),
      filter: panel.filterPicker.getValue(),
      minNdvi: panel.minNDVI.getValue(),
      maxNdvi: requireMax ? panel.maxNDVI.getValue() : null,
      range: range,
      requireMax: requireMax
    };
  };

  app.computeSeasonImage = function(inputs, onReady) {
    var cloud = app.parseNumericField(inputs.cloud);
    var region = app.clipRegion();
    var col = app.getCollection(inputs.startDate, inputs.endDate, cloud, region);
    col.size().evaluate(function(n, error) {
      if (error) {
        app.setBusy(false);
        app.prompt(true, app.ERROR.STH_WRONG);
        print(error);
        return;
      }
      if (!n) {
        app.setBusy(false);
        app.prompt(true, app.ERROR.NO_IMAGES);
        return;
      }
      print('Sentinel-2 scenes:', n);
      var composite = app.reduceCollection(col, inputs.filter).clip(region);
      onReady(composite, n);
    });
  };

  app.onSoComputeClicked = function() {
    if (!app.geometry) {
      app.prompt(true, app.ERROR.NO_AGRI_BOUNDS);
      return;
    }
    var inputs = app.readSeasonInputs(app.so, true, app.RANGE.SO_NDVI);
    if (!app.opticalSeasonInputsValid(inputs)) {
      if (!app.isValidIsoDate(inputs.startDate) || !app.isValidIsoDate(inputs.endDate) ||
          inputs.startDate >= inputs.endDate) {
        app.prompt(true, app.ERROR.MISSING_DATA + ' - Sowing season');
        return;
      }
      if (!app.ndviPairInRange(inputs.minNdvi, inputs.maxNdvi, app.RANGE.SO_NDVI)) {
        app.prompt(true, app.ERROR.NDVI_RANGE + app.RANGE.SO_NDVI[0] +
          ' and ' + app.RANGE.SO_NDVI[1] + ' - Sowing season');
        return;
      }
      app.prompt(true, app.ERROR.MISSING_DATA + ' - Sowing season');
      return;
    }
    app.setBusy(true);
    app.computeSeasonImage(inputs, function(composite) {
      app.removeLayers([app.LAYER.SO_FCC, app.LAYER.SO_NDVI, app.LAYER.SO_TH]);
      var minNDVI = app.parseNumericField(inputs.minNdvi);
      var maxNDVI = app.parseNumericField(inputs.maxNdvi);
      app.addLayer(composite, app.falseColor, app.LAYER.SO_FCC, false);
      var ndvi = app.getND(composite);
      app.addLayer(ndvi, app.vis, app.LAYER.SO_NDVI, false);
      var sowingZone = app.applyThreshold(ndvi, minNDVI, maxNDVI);
      app.updateNdviSowing = app.applyMask(ndvi, sowingZone);
      app.addLayer(app.updateNdviSowing, app.vis, app.LAYER.SO_TH, true);
      app.ndviSowingImage = ndvi;
      app.ex.ndviSo.setDisabled(false);
      app.ex.finalMask.setDisabled(false);
      app.setBusy(false);
      app.prompt(true, 'Sowing NDVI threshold applied.');
    });
  };

  app.onPsComputeClicked = function() {
    if (!app.geometry) {
      app.prompt(true, app.ERROR.NO_AGRI_BOUNDS);
      return;
    }
    var inputs = app.readSeasonInputs(app.ps, false, app.RANGE.PS_NDVI);
    if (!app.opticalSeasonInputsValid(inputs)) {
      if (!app.ndviMinInRange(inputs.minNdvi, app.RANGE.PS_NDVI)) {
        app.prompt(true, app.ERROR.NDVI_RANGE + app.RANGE.PS_NDVI[0] +
          ' and ' + app.RANGE.PS_NDVI[1] + ' - Peak season');
        return;
      }
      app.prompt(true, app.ERROR.MISSING_DATA + ' - Peak season');
      return;
    }
    app.setBusy(true);
    app.computeSeasonImage(inputs, function(composite) {
      app.removeLayers([
        app.LAYER.PS_FCC, app.LAYER.PS_NDVI, app.LAYER.PS_TH, app.LAYER.PS_COMBINE
      ]);
      var minNDVI = app.parseNumericField(inputs.minNdvi);
      app.addLayer(composite, app.falseColor, app.LAYER.PS_FCC, false);
      var ndvi = app.getND(composite);
      var ndsi = app.getND(composite, 'B11', 'B8');
      app.addLayer(ndvi, app.vis, app.LAYER.PS_NDVI, false);
      var reject = ndvi.lte(minNDVI).or(ndsi.gte(0));
      var keep = reject.eq(0);
      app.addLayer(keep, app.vis, app.LAYER.PS_TH, false);
      if (app.updateNdviSowing) {
        app.psThresholdCombine = app.applyMask(app.updateNdviSowing, keep);
      } else {
        app.psThresholdCombine = keep;
      }
      app.addLayer(app.psThresholdCombine, app.vis, app.LAYER.PS_COMBINE, true);
      app.ndviPeakImage = ndvi;
      app.ndsiPeakImage = ndsi;
      app.ex.ndviPs.setDisabled(false);
      app.ex.ndsiPs.setDisabled(false);
      app.ex.finalMask.setDisabled(false);
      app.setBusy(false);
      app.prompt(true, 'Peak NDVI/NDSI threshold applied.');
    });
  };

  app.onHarComputeClicked = function() {
    if (!app.geometry) {
      app.prompt(true, app.ERROR.NO_AGRI_BOUNDS);
      return;
    }
    var inputs = app.readSeasonInputs(app.har, true, app.RANGE.HAR_NDVI);
    if (!app.opticalSeasonInputsValid(inputs)) {
      if (!app.ndviPairInRange(inputs.minNdvi, inputs.maxNdvi, app.RANGE.HAR_NDVI)) {
        app.prompt(true, app.ERROR.NDVI_RANGE + app.RANGE.HAR_NDVI[0] +
          ' and ' + app.RANGE.HAR_NDVI[1] + ' - Harvest season');
        return;
      }
      app.prompt(true, app.ERROR.MISSING_DATA + ' - Harvest season');
      return;
    }
    app.setBusy(true);
    app.computeSeasonImage(inputs, function(composite) {
      app.removeLayers([
        app.LAYER.HAR_FCC, app.LAYER.HAR_NDVI, app.LAYER.HAR_TH, app.LAYER.HAR_COMBINE
      ]);
      var minNDVI = app.parseNumericField(inputs.minNdvi);
      var maxNDVI = app.parseNumericField(inputs.maxNdvi);
      app.addLayer(composite, app.falseColor, app.LAYER.HAR_FCC, false);
      var ndvi = app.getND(composite);
      app.addLayer(ndvi, app.vis, app.LAYER.HAR_NDVI, false);
      var harvestingth = app.applyThreshold(ndvi, minNDVI, maxNDVI);
      app.addLayer(harvestingth, app.vis, app.LAYER.HAR_TH, false);
      if (app.psThresholdCombine) {
        app.harThresholdCombine = app.applyMask(app.psThresholdCombine, harvestingth);
      } else if (app.updateNdviSowing) {
        app.harThresholdCombine = app.applyMask(app.updateNdviSowing, harvestingth);
      } else {
        app.harThresholdCombine = harvestingth;
      }
      app.addLayer(app.harThresholdCombine, app.vis, app.LAYER.HAR_COMBINE, true);
      app.ndviHarvestImage = ndvi;
      app.ex.ndviHar.setDisabled(false);
      app.ex.finalMask.setDisabled(false);
      app.setBusy(false);
      app.prompt(true, 'Harvest NDVI threshold applied. Combined optical mask is on the map.');
    });
  };

  app.finalMaskImage = function() {
    var kind = app.chooseFinalMaskLayer(
      !!app.harThresholdCombine && app.bo.harCheckBox.getValue(),
      !!app.psThresholdCombine && app.bo.psCheckBox.getValue(),
      !!app.updateNdviSowing && app.bo.soCheckBox.getValue()
    );
    if (kind === 'harvest') return app.harThresholdCombine;
    if (kind === 'peak') return app.psThresholdCombine;
    if (kind === 'sowing') return app.updateNdviSowing;
    if (app.harThresholdCombine) return app.harThresholdCombine;
    if (app.psThresholdCombine) return app.psThresholdCombine;
    if (app.updateNdviSowing) return app.updateNdviSowing;
    return null;
  };

  app.onExportClicked = function() {
    var wantSo = app.ex.ndviSo.getValue();
    var wantPs = app.ex.ndviPs.getValue();
    var wantNdsi = app.ex.ndsiPs.getValue();
    var wantHar = app.ex.ndviHar.getValue();
    var wantMask = app.ex.finalMask.getValue();
    if (!wantSo && !wantPs && !wantNdsi && !wantHar && !wantMask) {
      app.prompt(true, app.ERROR.NO_EXPORT);
      return;
    }
    var names = app.opticalExportDescriptions(
      app.bo.provincePicker.getValue(),
      app.bo.irRfPicker.getValue()
    );
    var ids = app.buildOpticalAssetIds(
      app.bo.assetSource.getValue(),
      app.bo.provincePicker.getValue(),
      app.bo.irRfPicker.getValue()
    );
    var region = app.exportRegion();
    var queued = 0;
    var exportImage = function(image, desc, assetId) {
      if (!image) return;
      Export.image.toAsset({
        image: image,
        description: desc,
        assetId: assetId,
        scale: app.DEFAULT.SCALE,
        region: region,
        maxPixels: 3e12
      });
      Export.image.toDrive({
        image: image,
        description: desc,
        fileNamePrefix: desc,
        scale: app.DEFAULT.SCALE,
        region: region,
        maxPixels: 3e12,
        fileFormat: 'GeoTIFF'
      });
      queued += 1;
    };
    if (wantSo) exportImage(app.ndviSowingImage, names.ndviSowing, ids.ndviSowing);
    if (wantPs) exportImage(app.ndviPeakImage, names.ndviPeak, ids.ndviPeak);
    if (wantNdsi) exportImage(app.ndsiPeakImage, names.ndsiPeak, ids.ndsiPeak);
    if (wantHar) exportImage(app.ndviHarvestImage, names.ndviHarvest, ids.ndviHarvest);
    if (wantMask) {
      var mask = app.finalMaskImage();
      if (!mask) {
        app.prompt(true, app.ERROR.NO_MASK);
        return;
      }
      exportImage(mask, names.finalMask, ids.finalMask);
    }
    if (!queued) {
      app.prompt(true, app.ERROR.NO_EXPORT);
      return;
    }
    app.prompt(true, queued + ' Asset + Drive export pair(s) queued. Open Tasks and click RUN. Create the Optical folder if the asset path is missing.');
    print('Queued optical exports', names, ids);
  };

  app.mapClicked = function(latlon) {
    var lat = Math.round(latlon.lat * 100000) / 100000;
    var lon = Math.round(latlon.lon * 100000) / 100000;
    app.ins.latLong.setValue(lat + ', ' + lon);
    app.ins.ndviSo.setValue('');
    app.ins.ndviPs.setValue('');
    app.ins.ndsiPs.setValue('');
    app.ins.ndviHar.setValue('');

    var getValueAndUpdate = function(image, band, point, textBox) {
      var sample = image.sample({
        region: point,
        scale: app.DEFAULT.SAMPLE_SCALE,
        geometries: false
      });
      sample.size().evaluate(function(n) {
        if (!n) {
          textBox.setValue('—');
          return;
        }
        sample.first().get(band).evaluate(function(result) {
          if (typeof result === 'number' && isFinite(result)) {
            textBox.setValue(Math.round(result * 1000) / 1000);
          } else {
            textBox.setValue(result == null ? '—' : String(result));
          }
        });
      });
    };

    var point = ee.Geometry.Point(latlon.lon, latlon.lat);
    if (app.ndviSowingImage) getValueAndUpdate(app.ndviSowingImage, 'NDVI', point, app.ins.ndviSo);
    if (app.ndviPeakImage) getValueAndUpdate(app.ndviPeakImage, 'NDVI', point, app.ins.ndviPs);
    if (app.ndsiPeakImage) getValueAndUpdate(app.ndsiPeakImage, 'NDSI', point, app.ins.ndsiPs);
    if (app.ndviHarvestImage) getValueAndUpdate(app.ndviHarvestImage, 'NDVI', point, app.ins.ndviHar);
  };

  app.centerZoomBox = function(lon, lat) {
    app.zp.instructions.style().set('shown', false);
    app.zp.zoomBox.style().set('shown', true);
    app.zp.zoomBox.setCenter(lon, lat);
  };

  app.onZoomBoxChange = function(event) {
    try {
      if (!app.zp.zoomBox.style().get('shown')) return;
      var box = app.readZoomBounds(event);
      if (!box) return;
      var outline = ee.Geometry.Rectangle({
        coords: [box.west, box.south, box.east, box.north],
        geodesic: false
      });
      app.removeLayers([app.LAYER.ZOOM]);
      Map.addLayer(outline, {color: 'F00'}, app.LAYER.ZOOM, false);
    } catch (err) {
      print('Zoom box outline skipped:', err);
    }
  };
};

app.initializeGUIElements = function() {
  var dateStyle = {width: '100px'};
  var rowLabel = function(text) {
    return ui.Label(text, {width: '100px', margin: '8px 8px 0px 8px'});
  };
  var sectionLabel = function(text) {
    return ui.Label(text, {fontWeight: 'bold', margin: '8px 8px 0px 8px'});
  };

  app.bo = {
    assetSource: ui.Textbox({
      value: app.DEFAULT.ASSET_SOURCE,
      style: {stretch: 'horizontal', padding: '0px 0px 10px 0px'},
      onChange: app.populatePickers
    }),
    provincePicker: ui.Select({
      placeholder: 'Select Province',
      style: {stretch: 'horizontal'},
      onChange: app.onProvSelected
    }),
    irRfPicker: ui.Select({
      placeholder: 'Select IR or RF',
      style: {stretch: 'horizontal'},
      items: ['IR', 'RF'],
      onChange: app.onIRRFSelected
    }),
    soCheckBox: ui.Checkbox({
      label: app.LABEL.SOWING,
      value: false,
      onChange: app.soCheckChanged
    }),
    psCheckBox: ui.Checkbox({
      label: app.LABEL.PEAK,
      value: false,
      onChange: app.psCheckChanged
    }),
    harCheckBox: ui.Checkbox({
      label: app.LABEL.HARVEST,
      value: false,
      onChange: app.harCheckChanged
    })
  };
  app.boPanel = ui.Panel({
    layout: ui.Panel.Layout.flow('vertical'),
    widgets: [
      ui.Label({
        value: app.LABEL.TITLE,
        style: {margin: '10px 10px 0px 10px', fontWeight: 'bold', fontSize: '16px'}
      }),
      ui.Label({
        value: app.LABEL.ASSET_SOURCE,
        style: {margin: '10px 10px 0px 10px'}
      }),
      app.bo.assetSource,
      ui.Label({
        value: app.LABEL.PROVINCE,
        style: {fontWeight: 'bold', margin: '10px 10px 0px 10px'}
      }),
      app.bo.provincePicker,
      app.bo.irRfPicker,
      ui.Label({
        value: app.LABEL.SEASONS,
        style: {fontWeight: 'bold', margin: '10px 10px 0px 10px'}
      }),
      app.bo.soCheckBox,
      app.bo.psCheckBox,
      app.bo.harCheckBox
    ]
  });

  app.so = {
    startDate: ui.Textbox({
      placeholder: 'YYYY-MM-DD',
      value: app.DEFAULT.SO.START_DATE,
      style: dateStyle
    }),
    endDate: ui.Textbox({
      placeholder: 'YYYY-MM-DD',
      value: app.DEFAULT.SO.END_DATE,
      style: dateStyle
    }),
    cloudCover: ui.Textbox({value: app.DEFAULT.SO.CLOUD_COVER, style: dateStyle}),
    filterPicker: ui.Select({
      items: app.FILTERS,
      value: app.DEFAULT.SO.FILTER,
      placeholder: 'Filter',
      style: dateStyle
    }),
    minNDVI: ui.Textbox({value: app.DEFAULT.SO.MIN_NDVI, style: dateStyle}),
    maxNDVI: ui.Textbox({value: app.DEFAULT.SO.MAX_NDVI, style: dateStyle}),
    button: ui.Button({
      label: app.LABEL.COMPUTE,
      onClick: app.onSoComputeClicked,
      style: {stretch: 'horizontal'}
    })
  };
  app.soPanel = ui.Panel({
    style: {shown: false, border: '1px solid black', margin: '5px'},
    widgets: [
      sectionLabel(app.LABEL.SO_MAIN),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [rowLabel(app.LABEL.START), rowLabel(app.LABEL.END)]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [app.so.startDate, app.so.endDate]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [rowLabel(app.LABEL.CLOUD), rowLabel(app.LABEL.FILTER)]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [app.so.cloudCover, app.so.filterPicker]
      }),
      ui.Label(app.LABEL.NDVI, {margin: '8px 8px 0px 8px'}),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [rowLabel(app.LABEL.MIN), rowLabel(app.LABEL.MAX)]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [app.so.minNDVI, app.so.maxNDVI]
      }),
      app.so.button
    ]
  });

  app.ps = {
    startDate: ui.Textbox({
      placeholder: 'YYYY-MM-DD',
      value: app.DEFAULT.PS.START_DATE,
      style: dateStyle
    }),
    endDate: ui.Textbox({
      placeholder: 'YYYY-MM-DD',
      value: app.DEFAULT.PS.END_DATE,
      style: dateStyle
    }),
    cloudCover: ui.Textbox({value: app.DEFAULT.PS.CLOUD_COVER, style: dateStyle}),
    filterPicker: ui.Select({
      items: app.FILTERS,
      value: app.DEFAULT.PS.FILTER,
      placeholder: 'Filter',
      style: dateStyle
    }),
    minNDVI: ui.Textbox({value: app.DEFAULT.PS.MIN_NDVI, style: dateStyle}),
    button: ui.Button({
      label: app.LABEL.COMPUTE,
      onClick: app.onPsComputeClicked,
      style: {stretch: 'horizontal'}
    })
  };
  app.psPanel = ui.Panel({
    style: {shown: false, border: '1px solid black', margin: '5px'},
    widgets: [
      sectionLabel(app.LABEL.PS_MAIN),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [rowLabel(app.LABEL.START), rowLabel(app.LABEL.END)]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [app.ps.startDate, app.ps.endDate]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [rowLabel(app.LABEL.CLOUD), rowLabel(app.LABEL.FILTER)]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [app.ps.cloudCover, app.ps.filterPicker]
      }),
      ui.Label(app.LABEL.MIN_NDVI, {margin: '8px 8px 0px 8px'}),
      app.ps.minNDVI,
      app.ps.button
    ]
  });

  app.har = {
    startDate: ui.Textbox({
      placeholder: 'YYYY-MM-DD',
      value: app.DEFAULT.HAR.START_DATE,
      style: dateStyle
    }),
    endDate: ui.Textbox({
      placeholder: 'YYYY-MM-DD',
      value: app.DEFAULT.HAR.END_DATE,
      style: dateStyle
    }),
    cloudCover: ui.Textbox({value: app.DEFAULT.HAR.CLOUD_COVER, style: dateStyle}),
    filterPicker: ui.Select({
      items: app.FILTERS,
      value: app.DEFAULT.HAR.FILTER,
      placeholder: 'Filter',
      style: dateStyle
    }),
    minNDVI: ui.Textbox({value: app.DEFAULT.HAR.MIN_NDVI, style: dateStyle}),
    maxNDVI: ui.Textbox({value: app.DEFAULT.HAR.MAX_NDVI, style: dateStyle}),
    button: ui.Button({
      label: app.LABEL.COMPUTE,
      onClick: app.onHarComputeClicked,
      style: {stretch: 'horizontal'}
    })
  };
  app.harPanel = ui.Panel({
    style: {shown: false, border: '1px solid black', margin: '5px'},
    widgets: [
      sectionLabel(app.LABEL.HAR_MAIN),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [rowLabel(app.LABEL.START), rowLabel(app.LABEL.END)]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [app.har.startDate, app.har.endDate]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [rowLabel(app.LABEL.CLOUD), rowLabel(app.LABEL.FILTER)]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [app.har.cloudCover, app.har.filterPicker]
      }),
      ui.Label(app.LABEL.NDVI, {margin: '8px 8px 0px 8px'}),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [rowLabel(app.LABEL.MIN), rowLabel(app.LABEL.MAX)]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [app.har.minNDVI, app.har.maxNDVI]
      }),
      app.har.button
    ]
  });

  app.ex = {
    ndviSo: ui.Checkbox({label: app.TEXT.EXPORT.NDVI_SO, value: false, disabled: true}),
    ndviPs: ui.Checkbox({label: app.TEXT.EXPORT.NDVI_PS, value: false, disabled: true}),
    ndsiPs: ui.Checkbox({label: app.TEXT.EXPORT.NDSI_PS, value: false, disabled: true}),
    ndviHar: ui.Checkbox({label: app.TEXT.EXPORT.NDVI_HAR, value: false, disabled: true}),
    finalMask: ui.Checkbox({label: app.TEXT.EXPORT.FINAL_MASK, value: false, disabled: true}),
    export: ui.Button({
      label: app.LABEL.EXPORT,
      onClick: app.onExportClicked,
      style: {stretch: 'horizontal'}
    })
  };
  app.exPanel = ui.Panel({
    layout: ui.Panel.Layout.flow('vertical'),
    style: {shown: true},
    widgets: [
      sectionLabel(app.LABEL.EXPORT),
      app.ex.ndviSo,
      app.ex.ndviPs,
      app.ex.ndsiPs,
      app.ex.ndviHar,
      app.ex.finalMask,
      app.ex.export
    ]
  });

  app.ins = {
    latLong: ui.Label({style: {margin: '2px 8px 0px 8px'}}),
    ndviSo: ui.Label({style: {margin: '2px 8px 0px 8px'}}),
    ndviPs: ui.Label({style: {margin: '2px 8px 0px 8px'}}),
    ndsiPs: ui.Label({style: {margin: '2px 8px 0px 8px'}}),
    ndviHar: ui.Label({style: {margin: '2px 8px 0px 8px'}})
  };
  var inspectRow = function(label, widget) {
    return ui.Panel({
      layout: ui.Panel.Layout.flow('horizontal'),
      widgets: [
        ui.Label({value: label, style: {width: '100px', margin: '2px 8px 0px 8px'}}),
        widget
      ],
      style: {border: '1px solid gray'}
    });
  };
  app.inspectPanel = ui.Panel({
    layout: ui.Panel.Layout.flow('vertical'),
    style: {width: '300px', position: 'bottom-right'},
    widgets: [
      ui.Label({
        value: app.TEXT.INSPECT.MAIN_LABEL,
        style: {fontWeight: 'bold', margin: '10px 10px 0px 10px'}
      }),
      inspectRow(app.TEXT.INSPECT.LAT_LONG, app.ins.latLong),
      inspectRow(app.TEXT.INSPECT.NDVI_SO, app.ins.ndviSo),
      inspectRow(app.TEXT.INSPECT.NDVI_PS, app.ins.ndviPs),
      inspectRow(app.TEXT.INSPECT.NDSI_PS, app.ins.ndsiPs),
      inspectRow(app.TEXT.INSPECT.NDVI_HAR, app.ins.ndviHar)
    ]
  });

  app.zp = {
    zoomBox: ui.Map({style: {stretch: 'both', shown: false, margin: '0px'}})
      .setControlVisibility(false, true, true),
    instructions: ui.Label('Click the map to see an area in detail.', {
      stretch: 'both',
      textAlign: 'center',
      margin: '0px'
    })
  };
  app.zp.zoomBox.setZoom(12);
  app.zp.zoomBox.onChangeBounds(app.onZoomBoxChange);
  app.zp.zoomBox.onClick(app.mapClicked);
  app.zoomPanel = ui.Panel({
    widgets: [app.zp.zoomBox, app.zp.instructions],
    style: {
      position: 'bottom-left',
      height: '300px',
      width: '300px',
      backgroundColor: 'F00',
      padding: '2px'
    }
  });

  app.mainPanel = ui.Panel({
    layout: ui.Panel.Layout.flow('vertical'),
    widgets: [app.boPanel, app.soPanel, app.psPanel, app.harPanel, app.exPanel],
    style: {width: '300px'}
  });
  app.promptText = ui.Label({
    style: {shown: false, color: 'red', padding: '8px'}
  });
};

app.init = function() {
  Map.setOptions('HYBRID');
  Map.setCenter(70.999, 33.98, 6);
  app.createConstants();
  app.createHelpers();
  app.initializeGUIElements();
  app.populatePickers();
  ui.root.insert(0, app.mainPanel);
  Map.add(app.promptText);
  Map.add(app.inspectPanel);
  Map.add(app.zoomPanel);
  Map.style().set('cursor', 'crosshair');
  Map.onClick(function(latlon) {
    app.mapClicked(latlon);
    app.centerZoomBox(latlon.lon, latlon.lat);
  });
};

app.init();
