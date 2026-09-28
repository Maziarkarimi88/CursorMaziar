/**
 * Wheat phenology mapper for the Earth Engine Code Editor.
 *
 * Interface: province, Irrigated/Rainfed, date range, cloud, scale.
 * Method: Tiwari et al. (2020) seasonal median NDVI at sowing, peak, harvest.
 *
 * Your asset layout:
 *   {root}/Admin/{Province}
 *   {root}/IR_RF/{Province}_Ag_{IR|RF}
 *   {root}/GCP/{Province}_{IR|RF}_GCP
 *
 * How to run:
 * 1. Open https://code.earthengine.google.com/ and sign in.
 * 2. Profile menu > Change Cloud Project > ee-maziarkarimi3
 * 3. If Run/Save/Get Link are gray, register at
 *    https://code.earthengine.google.com/register then reload.
 * 4. Paste this script and click Run.
 */

var app = {};

app.createConstants = function() {
  app.DEFAULT = {
    ASSET_SOURCE: 'projects/ee-maziarkarimi3/assets/Wheat_Mapping',
    S2_COLLECTION: 'COPERNICUS/S2_HARMONIZED',
    CLOUD: 30,
    SCALE: 10,
    CYCLE: 4,
    START: '2016-11-01',
    END: '2017-07-30',
    MAX_FEATURES: 400,
    MAX_MONTHS: 24,
    MAX_CHART_ROWS: 20000
  };
  app.LABEL = {
    TITLE: 'Wheat Phenology Mapper',
    ASSET_SOURCE: 'Geometry Assets Folder',
    AGRI_BOUNDS: 'Select Province',
    GPS_DATA: 'Select Province GPS',
    INIT_BTN: 'Show Overall Phenology',
    GPS_SOURCE: 'Provide GPS Asset Source',
    START: 'Start Date',
    END: 'End Date',
    CLOUD: 'Cloud %',
    FILTER: 'Filter',
    CHARTS: 'Charts',
    SCALE: 'Scale',
    CYCLE: 'Frequency',
    GPSLIST: 'List of sample points',
    DELETE: 'Delete Selected',
    EXPORT: 'Export Features'
  };
  app.PATH = {
    ADMIN: 'Admin',
    AGRI: 'IR_RF',
    GCP: 'GCP'
  };
  app.ERROR = {
    NO_GEOM: 'Please select a province and IR or RF',
    EMPTY_FIELDS: 'Please enter all the required values',
    ZOOM_IN: 'Please zoom in to select points',
    TOO_MANY_FEATURES: 'Please provide a GPS dataset with ' +
      app.DEFAULT.MAX_FEATURES + ' or less points',
    NO_FILES: 'Some files are missing. Check Admin, IR_RF and GCP assets for this province.',
    NO_FOLDER: 'Could not list provinces. Check the folder path and that you have access.',
    NO_IMAGES: 'No Sentinel-2 images found for these filters.'
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

  app.hasRequiredInputs = function(startDate, endDate, cloud, scale, cycles) {
    var cloudNum = app.parseNumericField(cloud);
    var scaleNum = app.parseNumericField(scale);
    var cycleNum = app.parseNumericField(cycles);
    return app.isValidIsoDate(startDate) &&
      app.isValidIsoDate(endDate) &&
      startDate < endDate &&
      !isNaN(cloudNum) && cloudNum >= 0 && cloudNum <= 100 &&
      !isNaN(scaleNum) && scaleNum > 0 &&
      !isNaN(cycleNum) && cycleNum > 0;
  };

  app.monthStart = function(isoDate) {
    var parts = String(isoDate).split('-');
    return parts[0] + '-' + parts[1] + '-01';
  };

  app.pad2 = function(n) {
    return (n < 10 ? '0' : '') + n;
  };

  app.addMonths = function(isoDate, n) {
    var parts = String(isoDate).split('-');
    var y = parseInt(parts[0], 10);
    var m = parseInt(parts[1], 10) + n;
    var d = parts[2] || '01';
    while (m > 12) {
      y += 1;
      m -= 12;
    }
    while (m < 1) {
      y -= 1;
      m += 12;
    }
    return y + '-' + app.pad2(m) + '-' + d;
  };

  app.monthWindows = function(startIso, endIso) {
    var windows = [];
    if (!app.isValidIsoDate(startIso) || !app.isValidIsoDate(endIso) || startIso >= endIso) {
      return windows;
    }
    var cursor = app.monthStart(startIso);
    var endExclusive = app.addMonths(app.monthStart(endIso), 1);
    var guard = 0;
    while (cursor < endExclusive && guard < app.DEFAULT.MAX_MONTHS) {
      var next = app.addMonths(cursor, 1);
      windows.push({
        start: cursor,
        end: next,
        label: cursor.slice(0, 7)
      });
      cursor = next;
      guard += 1;
    }
    return windows;
  };

  app.seasonsFromRange = function(startIso, endIso) {
    var sy = String(startIso).slice(0, 4);
    var ey = String(endIso).slice(0, 4);
    if (!ey) ey = String(parseInt(sy, 10) + 1);
    return [
      {id: 'sowing', label: 'Sowing', start: sy + '-11-15', end: sy + '-12-31'},
      {id: 'peak', label: 'Peak', start: ey + '-02-01', end: ey + '-03-31'},
      {id: 'harvest', label: 'Harvest', start: ey + '-05-01', end: ey + '-06-15'}
    ];
  };

  app.prompt = function(state, text) {
    app.promptText.setValue(text || '');
    app.promptText.style().set('shown', state);
  };

  app.setBusy = function(state) {
    app.widgets.compute.setDisabled(state);
    app.prompt(state, state ? 'Loading...' : '');
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

  app.populatePickers = function() {
    var root = app.widgets.assetSource.getValue();
    var adminFolder = String(root || '').replace(/\/+$/, '') + '/' + app.PATH.ADMIN;
    app.widgets.provincePicker.setDisabled(true);
    app.prompt(true, 'Loading provinces...');
    app.listFolderAssets(adminFolder, function(assets, error) {
      app.widgets.provincePicker.setDisabled(false);
      var names = app.collectProvinceNames(assets);
      if (!names.length) names = ['Nangarhar'];
      app.widgets.provincePicker.items().reset(names);
      if (error && !assets.length) {
        app.prompt(true, app.ERROR.NO_FOLDER + ' Showing Nangarhar as a fallback.');
        print('Admin folder list error:', error);
        return;
      }
      app.prompt(false, '');
    });
  };

  app.removeLayers = function(names) {
    var mapLayers = Map.layers();
    var toRemove = [];
    for (var i = 0; i < mapLayers.length(); i++) {
      var layer = mapLayers.get(i);
      if (names.indexOf(layer.getName()) > -1) toRemove.push(layer);
    }
    for (var j = 0; j < toRemove.length; j++) mapLayers.remove(toRemove[j]);
  };

  app.renderList = function(fc) {
    app.prevSelection = app.currentSelection = -1;
    app.widgets.del.style().set({shown: false});
    app.listArea.clear();
    fc.aggregate_array('id').evaluate(function(value) {
      app.idList = value || [];
      for (var i = 0; i < app.idList.length; i++) {
        app.listArea.add(ui.Panel({
          style: {padding: '0px', margin: '0px'},
          widgets: [ui.Button({
            label: app.idList[i] + '',
            style: {stretch: 'horizontal', textAlign: 'left', padding: '0px', margin: '2px'},
            onClick: app.listBtnClick
          })]
        }));
      }
    });
  };

  app.listBtnClick = function(btn) {
    if (!app.fc || !Array.isArray(app.idList)) return;
    var ind = btn.getLabel();
    app.activateListItem(app.idList.indexOf(ind));
    app.showSelectedPoint(app.fc.filter(ee.Filter.eq('id', ind)));
  };

  app.activateListItem = function(index) {
    if (index === undefined || index === null || index < 0) return;
    var widgets = app.listArea.widgets();
    if (index >= widgets.length()) return;
    if (app.currentSelection != -1 && app.currentSelection < widgets.length()) {
      widgets.get(app.currentSelection).style().set('backgroundColor', 'white');
    }
    app.currentSelection = index;
    widgets.get(index).style().set('backgroundColor', '#cfe8ff');
    app.widgets.del.style().set({shown: true});
  };

  app.deactivateListItem = function() {
    if (app.currentSelection != -1) {
      var widgets = app.listArea.widgets();
      if (app.currentSelection < widgets.length()) {
        widgets.get(app.currentSelection).style().set('backgroundColor', 'white');
      }
    }
    app.widgets.del.style().set({shown: false});
    app.prevSelection = app.currentSelection = -1;
  };

  app.deleteFeatureClick = function() {
    if (app.currentSelection == -1 || !Array.isArray(app.idList)) return;
    var selectedID = app.idList[app.currentSelection];
    app.fc = ee.FeatureCollection(app.fc.filter(ee.Filter.notEquals('id', selectedID)));
    app.removeLayers(['Selected']);
    Map.layers().set(2, ui.Map.Layer(app.fc, {color: 'red'}, 'Wheat GCP'));
    app.renderList(app.fc);
    app.chartArea.clear();
  };

  app.exportClick = function() {
    if (!app.seasonTable) {
      app.prompt(true, 'Run Show Overall Phenology first to export seasonal NDVI.');
      return;
    }
    Export.table.toDrive({
      collection: app.seasonTable,
      description: 'Wheat_GCP_NDVI_sowing_peak_harvest',
      fileFormat: 'CSV'
    });
  };

  app.onProvSelected = function() {
    if (app.widgets.irRfPicker.getValue()) app.onBothSelected();
  };

  app.onIRRFSelected = function() {
    if (app.widgets.provincePicker.getValue()) app.onBothSelected();
  };

  app.loadTable = function(assetId, callback) {
    var fc = ee.FeatureCollection(assetId);
    fc.size().evaluate(function(n, error) {
      if (error || n === null || n === undefined) {
        callback(null, error || 'missing');
        return;
      }
      callback(fc, null);
    });
  };

  app.onBothSelected = function() {
    var ids = app.buildWheatAssetIds(
      app.widgets.assetSource.getValue(),
      app.widgets.provincePicker.getValue(),
      app.widgets.irRfPicker.getValue()
    );
    app.setBusy(true);
    app.removeLayers([
      'Provincial boundary', 'Irrigated agriculture', 'Wheat GCP',
      'Selected', 'NDVI sowing', 'NDVI peak', 'NDVI harvest'
    ]);
    print('Loading assets', ids);
    app.loadTable(ids.aoi, function(aoiFc, aoiErr) {
      if (aoiErr || !aoiFc) {
        app.setBusy(false);
        app.prompt(true, app.ERROR.NO_FILES);
        return;
      }
      app.loadTable(ids.agri, function(agriFc, agriErr) {
        if (agriErr || !agriFc) {
          app.setBusy(false);
          app.prompt(true, app.ERROR.NO_FILES);
          return;
        }
        app.loadTable(ids.gcp, function(gcpFc, gcpErr) {
          if (gcpErr || !gcpFc) {
            app.setBusy(false);
            app.prompt(true, app.ERROR.NO_FILES);
            return;
          }
          app.geometry = aoiFc;
          app.agri = agriFc;
          app.fc = gcpFc.map(function(feature) {
            return feature.set('id', feature.id());
          }).sort('id');
          Map.layers().set(0, ui.Map.Layer(app.geometry, {color: 'white'}, 'Provincial boundary'));
          Map.layers().set(1, ui.Map.Layer(app.agri, {color: 'ffd468'}, 'Irrigated agriculture', false));
          Map.layers().set(2, ui.Map.Layer(app.fc, {color: 'red'}, 'Wheat GCP'));
          Map.centerObject(app.geometry, 8);
          app.renderList(app.fc);
          app.setBusy(false);
        });
      });
    });
  };

  app.maskS2clouds = function(image) {
    var qa = image.select('QA60');
    var mask = qa.bitwiseAnd(1 << 10).eq(0).and(qa.bitwiseAnd(1 << 11).eq(0));
    return image.updateMask(mask).copyProperties(image, ['system:time_start']);
  };

  app.addIndices = function(image) {
    return image
      .addBands(image.normalizedDifference(['B8', 'B4']).rename('NDVI'))
      .addBands(image.normalizedDifference(['B11', 'B8']).rename('NDSI'))
      .copyProperties(image, ['system:time_start']);
  };

  app.s2Collection = function(start, end, region, cloud) {
    return ee.ImageCollection(app.DEFAULT.S2_COLLECTION)
      .filterBounds(region)
      .filterDate(start, end)
      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud))
      .map(app.maskS2clouds)
      .map(app.addIndices)
      .map(function(image) {
        return image.clip(region).copyProperties(image, ['system:time_start']);
      });
  };

  app.sampleSeason = function(image, points, prefix, scale) {
    return image.reduceRegions({
      collection: points,
      reducer: ee.Reducer.mean(),
      scale: scale
    }).map(function(f) {
      return f.set(prefix + '_NDVI', f.get('NDVI'))
        .set(prefix + '_NDSI', f.get('NDSI'));
    });
  };

  app.seasonStats = function(sampled, prefix) {
    var valid = sampled.filter(ee.Filter.notNull([prefix + '_NDVI']));
    return ee.Dictionary({
      season: prefix,
      count: valid.size(),
      mean: valid.aggregate_mean(prefix + '_NDVI'),
      min: valid.aggregate_min(prefix + '_NDVI'),
      max: valid.aggregate_max(prefix + '_NDVI')
    });
  };

  app.joinSeasonSimple = function(base, sampled, prefix) {
    var dict = ee.Dictionary.fromLists(
      sampled.aggregate_array('system:index'),
      sampled.aggregate_array(prefix + '_NDVI')
    );
    return base.map(function(f) {
      return f.set(prefix + '_NDVI', dict.get(f.get('system:index')));
    });
  };

  app.addTimeBands = function(image) {
    var startDate = app.widgets.startDate.getValue();
    var years = ee.Date(image.get('system:time_start')).difference(ee.Date(startDate), 'year');
    return image
      .addBands(ee.Image(years).rename('t'))
      .addBands(ee.Image.constant(1).rename('constant'))
      .float()
      .copyProperties(image, ['system:time_start']);
  };

  app.asChartPoints = function(fc) {
    return ee.FeatureCollection(fc).map(function(f) {
      f = ee.Feature(f);
      var sid = ee.Algorithms.If(
        ee.Algorithms.IsEqual(f.get('id'), null),
        f.id(),
        f.get('id')
      );
      return f.setGeometry(f.geometry().buffer(40)).set('sample', ee.String(sid));
    });
  };

  app.yearFraction = function(millis) {
    var t = Number(millis);
    if (!isFinite(t)) return NaN;
    var d = new Date(t);
    var y = d.getUTCFullYear();
    var start = Date.UTC(y, 0, 1);
    var end = Date.UTC(y + 1, 0, 1);
    return y + (t - start) / (end - start);
  };

  app.isoDateFromMillis = function(millis) {
    var d = new Date(Number(millis));
    if (isNaN(d.getTime())) return '';
    var y = d.getUTCFullYear();
    var m = d.getUTCMonth() + 1;
    var day = d.getUTCDate();
    return y + '-' + (m < 10 ? '0' : '') + m + '-' + (day < 10 ? '0' : '') + day;
  };

  app.coerceChartNumber = function(value, asTime) {
    if (value === null || value === undefined || value === '') return NaN;
    if (typeof value === 'number') return isFinite(value) ? value : NaN;
    if (typeof value === 'boolean') return NaN;
    if (typeof value === 'object') {
      if (typeof value.getTime === 'function') {
        var ms = value.getTime();
        return isFinite(ms) ? ms : NaN;
      }
      if (value.value !== undefined && value.value !== value) {
        return app.coerceChartNumber(value.value, asTime);
      }
      return NaN;
    }
    var text = String(value).trim();
    var dateCtor = text.match(/^Date\((\d+)\)$/);
    if (dateCtor) return app.coerceChartNumber(Number(dateCtor[1]), asTime);
    if (asTime && /^\d{4}-\d{2}-\d{2}/.test(text)) {
      var parsed = Date.parse(text);
      return isFinite(parsed) ? parsed : NaN;
    }
    var n = parseFloat(text);
    return isFinite(n) ? n : NaN;
  };

  app.featureProperties = function(feature) {
    if (!feature) return {};
    if (feature.properties && typeof feature.properties === 'object') return feature.properties;
    return feature;
  };

  app.sortChartRows = function(rows) {
    rows.sort(function(a, b) {
      if (a.t !== b.t) return a.t - b.t;
      return a.s < b.s ? -1 : a.s > b.s ? 1 : 0;
    });
    return rows;
  };

  app.averageRowsBySampleTime = function(rows) {
    var sums = {};
    var counts = {};
    var i;
    for (i = 0; i < rows.length; i++) {
      var key = rows[i].s + '_' + rows[i].t;
      sums[key] = (sums[key] || 0) + rows[i].v;
      counts[key] = (counts[key] || 0) + 1;
    }
    var out = [];
    var seen = {};
    for (i = 0; i < rows.length; i++) {
      var k = rows[i].s + '_' + rows[i].t;
      if (seen[k]) continue;
      seen[k] = true;
      out.push({t: rows[i].t, v: sums[k] / counts[k], s: rows[i].s});
    }
    return app.sortChartRows(out);
  };

  app.collectChartRows = function(features) {
    var rows = [];
    var list = features || [];
    for (var i = 0; i < list.length; i++) {
      var p = app.featureProperties(list[i]);
      var t = app.coerceChartNumber(p.time != null ? p.time : p.millis, true);
      var v = app.coerceChartNumber(
        p.value != null ? p.value : (p.NDVI != null ? p.NDVI : p.fitted),
        false
      );
      if (!isFinite(t) || !isFinite(v)) continue;
      rows.push({
        t: t,
        v: v,
        s: String(p.sample != null ? p.sample : (p.id != null ? p.id : '1'))
      });
    }
    return app.sortChartRows(rows);
  };

  app.collectChartRowsFromArrays = function(times, values, samples) {
    times = times || [];
    values = values || [];
    samples = samples || [];
    var rows = [];
    var n = Math.min(times.length, values.length);
    for (var i = 0; i < n; i++) {
      var t = app.coerceChartNumber(times[i], true);
      var v = app.coerceChartNumber(values[i], false);
      if (!isFinite(t) || !isFinite(v)) continue;
      rows.push({
        t: t,
        v: v,
        s: String(samples[i] == null ? String(i + 1) : samples[i])
      });
    }
    return app.sortChartRows(rows);
  };

  app.collectChartRowsFromGetRegion = function(table, band) {
    if (!table || table.length < 2 || !table[0]) return [];
    var header = table[0];
    var timeIdx = header.indexOf('time');
    if (timeIdx < 0) timeIdx = 3;
    var valueIdx = band ? header.indexOf(band) : -1;
    if (valueIdx < 0) valueIdx = header.indexOf('value');
    if (valueIdx < 0) valueIdx = header.indexOf('NDVI');
    if (valueIdx < 0) valueIdx = header.indexOf('fitted');
    if (valueIdx < 0) valueIdx = header.length - 1;
    var lonIdx = header.indexOf('longitude');
    var latIdx = header.indexOf('latitude');
    var rows = [];
    for (var i = 1; i < table.length; i++) {
      var r = table[i];
      if (!r) continue;
      var t = app.coerceChartNumber(r[timeIdx], true);
      var v = app.coerceChartNumber(r[valueIdx], false);
      if (!isFinite(t) || !isFinite(v)) continue;
      var sample = '1';
      if (lonIdx >= 0 && latIdx >= 0) {
        var lon = Number(r[lonIdx]);
        var lat = Number(r[latIdx]);
        if (isFinite(lon) && isFinite(lat)) {
          sample = lon.toFixed(4) + ',' + lat.toFixed(4);
        }
      }
      rows.push({t: t, v: v, s: sample});
    }
    return app.averageRowsBySampleTime(rows);
  };

  app.buildNumericChartTable = function(rows) {
    rows = rows || [];
    var samples = [];
    var seenS = {};
    var times = [];
    var seenT = {};
    var lookup = {};
    for (var i = 0; i < rows.length; i++) {
      var r = rows[i];
      if (!seenS[r.s]) {
        seenS[r.s] = true;
        samples.push(r.s);
      }
      if (!seenT[r.t]) {
        seenT[r.t] = true;
        times.push(r.t);
      }
      lookup[r.s + '_' + r.t] = r.v;
    }
    times.sort(function(a, b) { return a - b; });

    var cols = [{id: 'x', label: 'Date', type: 'number', role: 'domain'}];
    for (var s = 0; s < samples.length; s++) {
      cols.push({
        id: 's' + s,
        label: String(samples[s]),
        type: 'number',
        role: 'data'
      });
    }

    var tableRows = [];
    for (var ti = 0; ti < times.length; ti++) {
      var t = times[ti];
      var cells = [{v: app.yearFraction(t), f: app.isoDateFromMillis(t)}];
      var any = false;
      for (var si = 0; si < samples.length; si++) {
        var val = lookup[samples[si] + '_' + t];
        if (typeof val === 'number' && isFinite(val)) {
          cells.push({v: val});
          any = true;
        } else {
          cells.push({v: null});
        }
      }
      if (any) tableRows.push({c: cells});
    }
    return {cols: cols, rows: tableRows, samples: samples, times: times};
  };

  app.extractNdviTable = function(imageCollection, points, band, scale) {
    var sampleScale = Math.max(Number(scale) || 10, 20);
    var ic = ee.ImageCollection(imageCollection).map(function(img) {
      return img.select([band]).rename(['value']).copyProperties(img, ['system:time_start']);
    });
    return ic.map(function(img) {
      var sampled = img.reduceRegions({
        collection: points,
        reducer: ee.Reducer.mean(),
        scale: sampleScale,
        tileScale: 4
      });
      return sampled.map(function(f) {
        f = ee.Feature(f);
        var val = f.get('value');
        val = ee.Algorithms.If(ee.Algorithms.IsEqual(val, null), f.get(band), val);
        return ee.Feature(null, {
          time: img.date().millis(),
          value: val,
          sample: ee.String(ee.Algorithms.If(f.get('sample'), f.get('sample'), f.id()))
        });
      });
    }).flatten().filter(ee.Filter.notNull(['value']));
  };

  app.renderNumericChart = function(rows, title) {
    var dataTable = app.buildNumericChartTable(rows);
    if (!dataTable.rows.length) return false;
    var chart = ui.Chart({cols: dataTable.cols, rows: dataTable.rows})
      .setChartType('LineChart')
      .setOptions({
        title: title,
        interpolateNulls: true,
        vAxis: {title: 'NDVI'},
        hAxis: {title: 'Date'},
        lineWidth: 1,
        pointSize: 2,
        legend: {
          position: dataTable.samples.length > 12 ? 'bottom' : 'right',
          textStyle: {fontSize: 9}
        },
        chartArea: {width: '75%'}
      });
    chart.style().set({width: '320px'});
    app.chartArea.add(chart);
    return true;
  };

  app.addChartError = function(title, message) {
    app.chartArea.add(ui.Label({
      value: title + ': ' + message,
      style: {color: 'red'}
    }));
  };

  app.addNumericChart = function(imageCollection, points, band, scale, title, onDone, singleSample) {
    var table = app.extractNdviTable(imageCollection, points, band, scale);
    var fc = ee.FeatureCollection(table);
    ee.Dictionary({
      n: fc.size(),
      time: fc.limit(app.DEFAULT.MAX_CHART_ROWS).aggregate_array('time'),
      value: fc.limit(app.DEFAULT.MAX_CHART_ROWS).aggregate_array('value'),
      sample: fc.limit(app.DEFAULT.MAX_CHART_ROWS).aggregate_array('sample')
    }).evaluate(function(raw, error) {
      var rows = app.collectChartRowsFromArrays(
        raw && raw.time,
        raw && raw.value,
        raw && raw.sample
      );
      if (rows.length && app.renderNumericChart(rows, title)) {
        if (onDone) onDone();
        return;
      }
      if (!singleSample) {
        app.addChartError(
          title,
          error ||
            ('sampled ' + ((raw && raw.n) || 0) +
              ' NDVI values at these points/dates')
        );
        if (onDone) onDone();
        return;
      }
      var sampleScale = Math.max(Number(scale) || 10, 20);
      ee.ImageCollection(imageCollection)
        .select([band])
        .getRegion(ee.FeatureCollection(points).geometry(), sampleScale)
        .evaluate(function(region, err2) {
          var rows2 = app.collectChartRowsFromGetRegion(region, band);
          if (rows2.length && app.renderNumericChart(rows2, title)) {
            if (onDone) onDone();
            return;
          }
          app.addChartError(
            title,
            error || err2 ||
              ('sampled ' + ((raw && raw.n) || 0) +
                ' NDVI values at these points/dates')
          );
          if (onDone) onDone();
        });
    });
  };

  app.reduceCollection = function(col, name) {
    if (name === 'Max') return col.max();
    if (name === 'Mean') return col.mean();
    if (name === 'Min') return col.min();
    return col.median();
  };

  app.addMonthlyMap = function(selected, win) {
    var cloud = app.parseNumericField(app.widgets.cloud.getValue());
    if (isNaN(cloud)) cloud = app.DEFAULT.CLOUD;
    var col = ee.ImageCollection(app.DEFAULT.S2_COLLECTION)
      .filterDate(win.start, win.end)
      .filterBounds(selected.geometry())
      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud))
      .map(app.maskS2clouds)
      .select(['B8', 'B4', 'B3']);
    var temp = app.reduceCollection(col, app.widgets.filterPicker.getValue());
    var map = ui.Map();
    map.style().set({margin: '2px', height: '100px'});
    map.setControlVisibility(false);
    map.addLayer(temp, {bands: ['B8', 'B4', 'B3'], max: 4000}, win.label);
    map.addLayer(selected, {color: 'FF0000'}, 'Selected');
    map.centerObject(selected, 15);
    app.subMapPanel.add(ui.Panel({
      layout: ui.Panel.Layout.flow('vertical'),
      widgets: [
        ui.Label(win.label),
        map
      ]
    }));
  };

  app.showMonthlyComposite = function(selected) {
    app.subMapPanel.clear();
    var windows = app.monthWindows(
      app.widgets.startDate.getValue(),
      app.widgets.endDate.getValue()
    );
    for (var m = 0; m < windows.length; m++) {
      app.addMonthlyMap(selected, windows[m]);
    }
    app.mainMapPanel.style().set({shown: windows.length > 0});
  };

  app.onShowPhenology = function(fc, singleSample) {
    var startDate = app.widgets.startDate.getValue();
    var endDate = app.widgets.endDate.getValue();
    var cloud = app.parseNumericField(app.widgets.cloud.getValue());
    var scale = app.parseNumericField(app.widgets.scale.getValue());
    var cycles = app.parseNumericField(app.widgets.cycle.getValue());
    if (!app.hasRequiredInputs(startDate, endDate, cloud, scale, cycles)) {
      app.prompt(true, app.ERROR.EMPTY_FIELDS);
      return;
    }
    app.setBusy(true);
    app.chartArea.clear();
    app.chartArea.add(ui.Label({
      value: singleSample ? 'Selected sample' : 'All sample points',
      style: {fontWeight: 'bold', margin: '8px 10px 0px 10px'}
    }));
    var points = app.asChartPoints(fc);
    if (singleSample) points = points.limit(1);
    var clipGeom = points.geometry().bounds().buffer(2000);
    var timeField = 'system:time_start';
    var col = app.s2Collection(startDate, endDate, clipGeom, cloud).map(app.addTimeBands);
    col.size().evaluate(function(n, error) {
      if (error || !n) {
        app.setBusy(false);
        app.prompt(true, app.ERROR.NO_IMAGES);
        return;
      }
      print('Sentinel-2 images used:', n);
      var independents = ee.List(['constant', 't']);
      var dependent = 'NDVI';
      var trend = col.select(independents.add(dependent))
        .reduce(ee.Reducer.linearRegression(2, 1));
      var coefficients = trend.select('coefficients')
        .arrayProject([0])
        .arrayFlatten([independents]);
      var detrended = col.map(function(image) {
        return image.select(dependent).subtract(
          image.select(independents).multiply(coefficients).reduce('sum'))
          .rename(dependent)
          .copyProperties(image, [timeField]);
      });
      var harmonicIndependents = ee.List(['constant', 't', 'cos', 'sin']);
      var harmonicImage = col.map(function(image) {
        var timeRadians = image.select('t').multiply(cycles * Math.PI);
        return image
          .addBands(timeRadians.cos().rename('cos'))
          .addBands(timeRadians.sin().rename('sin'));
      });
      var harmonicTrend = harmonicImage
        .select(harmonicIndependents.add(dependent))
        .reduce(ee.Reducer.linearRegression(4, 1));
      var harmonicTrendCoefficients = harmonicTrend.select('coefficients')
        .arrayProject([0])
        .arrayFlatten([harmonicIndependents]);
      var fittedHarmonic = harmonicImage.map(function(image) {
        return image.addBands(
          image.select(harmonicIndependents)
            .multiply(harmonicTrendCoefficients)
            .reduce('sum')
            .rename('fitted'));
      });

      var pending = 4;
      var finishChart = function() {
        pending -= 1;
        if (pending <= 0) app.setBusy(false);
      };
      app.addNumericChart(col, points, 'NDVI', scale,
        'Time series NDVI' + (singleSample ? ' (selected sample)' : ' (all samples)'),
        finishChart, singleSample);
      app.addNumericChart(detrended, points, 'NDVI', scale,
        'Detrended time series' + (singleSample ? ' (selected sample)' : ' (all samples)'),
        finishChart, singleSample);
      app.addNumericChart(fittedHarmonic, points, 'NDVI', scale,
        'Harmonic model: original values' + (singleSample ? ' (selected sample)' : ' (all samples)'),
        finishChart, singleSample);
      app.addNumericChart(fittedHarmonic, points, 'fitted', scale,
        'Harmonic model: fitted values' + (singleSample ? ' (selected sample)' : ' (all samples)'),
        finishChart, singleSample);

      var seasons = app.seasonsFromRange(startDate, endDate);
      var sowingImg = col.filterDate(seasons[0].start, seasons[0].end).select(['NDVI', 'NDSI']).median();
      var peakImg = col.filterDate(seasons[1].start, seasons[1].end).select(['NDVI', 'NDSI']).median();
      var harvestImg = col.filterDate(seasons[2].start, seasons[2].end).select(['NDVI', 'NDSI']).median();
      var sowingPts = app.sampleSeason(sowingImg, points, 'sowing', scale);
      var peakPts = app.sampleSeason(peakImg, points, 'peak', scale);
      var harvestPts = app.sampleSeason(harvestImg, points, 'harvest', scale);
      var table = points.map(function(f) { return f.select(['id']); });
      table = app.joinSeasonSimple(table, sowingPts, 'sowing');
      table = app.joinSeasonSimple(table, peakPts, 'peak');
      table = app.joinSeasonSimple(table, harvestPts, 'harvest');
      app.seasonTable = table;
      print('Seasonal NDVI at selected sample points', table);

      if (singleSample) {
        app.showMonthlyComposite(ee.Feature(points.first()));
      } else {
        app.mainMapPanel.style().set({shown: false});
      }
    });
  };

  app.onComputeClicked = function() {
    if (!app.fc) {
      app.prompt(true, app.ERROR.NO_GEOM);
      return;
    }
    app.removeLayers(['Selected']);
    app.deactivateListItem();
    app.mainMapPanel.style().set({shown: false});
    app.fc.size().evaluate(function(n, error) {
      if (error) {
        app.prompt(true, app.ERROR.NO_GEOM);
        return;
      }
      if (n > app.DEFAULT.MAX_FEATURES) {
        app.prompt(true, app.ERROR.TOO_MANY_FEATURES);
        return;
      }
      app.onShowPhenology(app.fc, false);
    });
  };

  app.mapClicked = function(latlon) {
    if (Map.getZoom() < 9) {
      app.prompt(true, app.ERROR.ZOOM_IN);
      return;
    }
    var point = ee.Geometry.Point([latlon.lon, latlon.lat]).buffer(3 * Map.getScale());
    if (!app.fc) {
      app.showSelectedPoint(ee.FeatureCollection([
        ee.Feature(ee.Geometry.Point([latlon.lon, latlon.lat]))
      ]));
      return;
    }
    var hits = app.fc.filterBounds(point);
    hits.size().evaluate(function(n, error) {
      if (error || !n) {
        app.showSelectedPoint(ee.FeatureCollection([
          ee.Feature(ee.Geometry.Point([latlon.lon, latlon.lat]))
        ]));
        return;
      }
      var feat = ee.Feature(hits.first());
      feat.get('id').evaluate(function(id) {
        if (Array.isArray(app.idList) && id != null) {
          app.activateListItem(app.idList.indexOf(id));
        }
      });
      app.showSelectedPoint(hits.limit(1));
    });
  };

  app.showSelectedPoint = function(selected) {
    var selectedFc = ee.FeatureCollection(selected);
    app.onShowPhenology(selectedFc, true);
    app.removeLayers(['Selected']);
    Map.layers().set(3, ui.Map.Layer(selectedFc, {color: 'FF0000'}, 'Selected'));
  };
};

app.initializeGUIElements = function() {
  app.widgets = {
    assetSource: ui.Textbox({
      value: app.DEFAULT.ASSET_SOURCE,
      style: {stretch: 'horizontal', padding: '0px 0px 20px 0px'},
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
    startDate: ui.Textbox({
      value: app.DEFAULT.START,
      placeholder: 'YYYY-MM-DD',
      style: {stretch: 'horizontal'}
    }),
    endDate: ui.Textbox({
      value: app.DEFAULT.END,
      placeholder: 'YYYY-MM-DD',
      style: {stretch: 'horizontal'}
    }),
    cloud: ui.Textbox({
      value: app.DEFAULT.CLOUD,
      style: {stretch: 'horizontal'}
    }),
    scale: ui.Textbox({
      value: app.DEFAULT.SCALE,
      style: {stretch: 'horizontal'}
    }),
    cycle: ui.Textbox({
      value: app.DEFAULT.CYCLE,
      style: {stretch: 'horizontal'}
    }),
    filterPicker: ui.Select({
      value: 'Median',
      style: {stretch: 'horizontal'},
      items: ['Max', 'Mean', 'Median', 'Min']
    }),
    compute: ui.Button({
      label: app.LABEL.INIT_BTN,
      style: {stretch: 'horizontal'},
      onClick: app.onComputeClicked
    }),
    del: ui.Button({
      label: app.LABEL.DELETE,
      onClick: app.deleteFeatureClick,
      style: {stretch: 'horizontal', shown: false}
    }),
    export: ui.Button({
      label: app.LABEL.EXPORT,
      onClick: app.exportClick,
      style: {stretch: 'horizontal'}
    })
  };
  app.listArea = ui.Panel({
    layout: ui.Panel.Layout.flow('vertical'),
    style: {height: '350px', padding: '0', margin: '0'}
  });
  app.listPanel = ui.Panel({
    layout: ui.Panel.Layout.flow('vertical'),
    widgets: [
      ui.Label(app.LABEL.GPSLIST, {margin: '8px 8px 0px 8px', fontWeight: 'bold'}),
      app.listArea,
      app.widgets.del,
      app.widgets.export
    ]
  });
  app.mainPanel = ui.Panel({
    layout: ui.Panel.Layout.flow('vertical'),
    style: {width: '300px'},
    widgets: [
      ui.Label({
        value: app.LABEL.TITLE,
        style: {margin: '10px 10px 0px 10px', fontWeight: 'bold', fontSize: '16px'}
      }),
      ui.Label({
        value: app.LABEL.ASSET_SOURCE,
        style: {margin: '10px 10px 0px 10px'}
      }),
      app.widgets.assetSource,
      ui.Label({
        value: app.LABEL.AGRI_BOUNDS,
        style: {margin: '10px 10px 0px 10px'}
      }),
      app.widgets.provincePicker,
      app.widgets.irRfPicker,
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [
          ui.Label(app.LABEL.START, {width: '100px', margin: '8px 8px 0px 8px'}),
          app.widgets.startDate
        ]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [
          ui.Label(app.LABEL.END, {width: '100px', margin: '8px 8px 0px 8px'}),
          app.widgets.endDate
        ]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [
          ui.Label(app.LABEL.CLOUD, {width: '100px', margin: '8px 8px 0px 8px'}),
          app.widgets.cloud
        ]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [
          ui.Label(app.LABEL.SCALE, {width: '100px', margin: '8px 8px 0px 8px'}),
          app.widgets.scale
        ]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [
          ui.Label(app.LABEL.CYCLE, {width: '100px', margin: '8px 8px 0px 8px'}),
          app.widgets.cycle
        ]
      }),
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [
          ui.Label(app.LABEL.FILTER, {width: '100px', margin: '8px 8px 0px 8px'}),
          app.widgets.filterPicker
        ]
      }),
      app.widgets.compute,
      app.listPanel
    ]
  });
  app.chartArea = ui.Panel({layout: ui.Panel.Layout.flow('vertical')});
  app.chartPanel = ui.Panel({
    layout: ui.Panel.Layout.flow('vertical'),
    style: {width: '350px', margin: '0px', padding: '0px'},
    widgets: [
      ui.Label({
        value: app.LABEL.CHARTS,
        style: {fontWeight: 'bold', margin: '10px 10px 0px 10px'}
      }),
      app.chartArea
    ]
  });
  app.subMapPanel = ui.Panel({
    layout: ui.Panel.Layout.flow('horizontal'),
    style: {minHeight: '220px', stretch: 'horizontal', margin: '0px', padding: '0px'}
  });
  app.mainMapPanel = ui.Panel({
    layout: ui.Panel.Layout.flow('horizontal'),
    style: {
      minHeight: '240px',
      width: '95%',
      margin: '0px',
      padding: '0px',
      position: 'bottom-center',
      shown: false
    },
    widgets: [app.subMapPanel]
  });
  app.promptText = ui.Label({
    style: {shown: false, color: 'red', padding: '8px'}
  });
};

app.init = function() {
  Map.setOptions('HYBRID');
  Map.setCenter(70.43, 34.35, 8);
  app.createConstants();
  app.createHelpers();
  app.initializeGUIElements();
  app.populatePickers();
  Map.add(app.promptText);
  ui.root.insert(0, app.mainPanel);
  ui.root.insert(2, app.chartPanel);
  Map.add(app.mainMapPanel);
  Map.style().set('cursor', 'crosshair');
  Map.onClick(app.mapClicked);
};

app.init();
