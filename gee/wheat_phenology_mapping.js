/**
 * Wheat crop phenology mapping app for the Earth Engine Code Editor.
 *
 * How to run:
 * 1. Open https://code.earthengine.google.com/ while signed into Google.
 * 2. If Get Link / Save / Run / Reset are gray, Earth Engine is not ready:
 *    click your email in the top-right > Change Cloud Project, or register at
 *    https://code.earthengine.google.com/register
 * 3. Paste this script into the editor and click Run.
 * 4. Point "Geometry Assets Folder" at a folder that contains one
 *    subfolder per province. Each province folder should include:
 *      <Province>_<Ag|Wheat>_<IR|RF>
 *    Example: Hilmand/Hilmand_Wheat_IR
 *
 * You can also zoom in and click the map to chart phenology at a point
 * even if province GPS assets are not available.
 *
 * Fixes versus the original script:
 * - Invalid ui.Label style key used CSS kebab-case instead of fontWeight
 * - Asset folder listing crashed when the folder was missing/denied
 * - Map layers were looked up with a dictionary get call; use getName()
 * - Deprecated Sentinel-2 L1C collection ID replaced with S2_HARMONIZED
 * - GCP list buttons were created disabled, so list clicks did nothing
 * - Client Date objects in monthly composites had timezone / infinite-loop risk
 * - Harmonic / linear reduce ran on unclipped S2 granules (timeouts)
 * - Map-click used empty Feature.first() without a size check
 * - Mixed client/server idList.indexOf after evaluate
 */

var app = {};

app.createConstants = function() {
  app.DEFAULT = {
    ASSET_SOURCE: 'projects/servir-hkh/WheatMapping/2017/Afghanistan',
    S2_COLLECTION: 'COPERNICUS/S2_HARMONIZED',
    CLOUD: 30,
    SCALE: 10,
    CYCLE: 4,
    START: '2016-11-01',
    END: '2017-05-30',
    MAX_FEATURES: 400,
    MAX_MONTHS: 24
  };
  app.LABEL = {
    TITLE: 'Wheat Phenology Mapper',
    ASSET_SOURCE: 'Geometry Assets Folder',
    AGRI_BOUNDS: 'Select Province',
    INIT_BTN: 'Show Overall Phenology',
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
    AGRI: 'Ag',
    WHEAT: 'Wheat'
  };
  app.ERROR = {
    NO_GEOM: 'Please select a province',
    EMPTY_FIELDS: 'Please enter all the required values',
    ZOOM_IN: 'Please zoom in to select points',
    TOO_MANY_FEATURES: 'Please provide a GPS dataset with ' +
      app.DEFAULT.MAX_FEATURES + ' or less points',
    NO_FILES: 'Some files are missing. Check that Ag and Wheat assets exist for this province.',
    NO_FOLDER: 'Could not list provinces. Check the folder path and that you have access.',
    NO_IMAGES: 'No Sentinel-2 images found for these filters.'
  };
};

app.createHelpers = function() {
  app.isFolderType = function(type) {
    if (!type) return false;
    return String(type).toUpperCase() === 'FOLDER';
  };

  app.assetShortName = function(assetId) {
    if (!assetId) return '';
    var parts = String(assetId).replace(/\/+$/, '').split('/');
    return parts[parts.length - 1];
  };

  app.collectFolderNames = function(assets) {
    var list = Array.isArray(assets) ? assets : (assets && assets.assets) || [];
    var ids = [];
    for (var i = 0; i < list.length; i++) {
      var element = list[i] || {};
      if (!app.isFolderType(element.type)) continue;
      var name = app.assetShortName(element.id || element.name || '');
      if (name) ids.push(name);
    }
    return ids;
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

  app.prompt = function(state, text) {
    app.promptText.setValue(text || '');
    app.promptText.style().set('shown', state);
  };

  app.loading = function(state) {
    app.prompt(state, 'Loading...');
    app.widgets.provincePicker.setDisabled(state);
    app.widgets.irRfPicker.setDisabled(state);
    app.widgets.startDate.setDisabled(state);
    app.widgets.endDate.setDisabled(state);
    app.widgets.cloud.setDisabled(state);
    app.widgets.scale.setDisabled(state);
    app.widgets.cycle.setDisabled(state);
    app.widgets.filterPicker.setDisabled(state);
    app.widgets.compute.style().set('shown', !state);
    app.listPanel.style().set('shown', !state);
  };

  app.listFolderAssets = function(folderId, callback) {
    var finished = false;
    var finish = function(assets, error) {
      if (finished) return;
      finished = true;
      callback(assets, error);
    };
    setTimeout(function() {
      finish([], 'Timed out listing the geometry folder');
    }, 20000);
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
    var folderId = app.widgets.assetSource.getValue();
    if (!folderId) {
      app.prompt(true, app.ERROR.NO_FOLDER);
      return;
    }
    app.widgets.provincePicker.setDisabled(true);
    app.prompt(true, 'Loading provinces...');
    app.listFolderAssets(folderId, function(assets, error) {
      app.widgets.provincePicker.setDisabled(false);
      if (error) {
        app.widgets.provincePicker.items().reset([]);
        app.prompt(true, app.ERROR.NO_FOLDER);
        print('Asset folder error:', error);
        return;
      }
      app.prompt(false, '');
      app.widgets.provincePicker.items().reset(app.collectFolderNames(assets));
    });
  };

  app.removeLayers = function(names) {
    var mapLayers = Map.layers();
    var toRemove = [];
    for (var i = 0; i < mapLayers.length(); i++) {
      var layer = mapLayers.get(i);
      if (names.indexOf(layer.getName()) > -1) {
        toRemove.push(layer);
      }
    }
    for (var j = 0; j < toRemove.length; j++) {
      mapLayers.remove(toRemove[j]);
    }
  };

  app.renderList = function(fc) {
    app.prevSelection = app.currentSelection = -1;
    app.widgets.del.style().set({shown: false});
    app.listArea.clear();
    fc.aggregate_array('id').evaluate(function(value, error) {
      if (error || !value) {
        app.idList = [];
        app.loading(false);
        return;
      }
      app.idList = value;
      for (var i = 0; i < value.length; i++) {
        app.listArea.add(ui.Panel({
          style: {padding: '0px', margin: '0px'},
          widgets: [ui.Button({
            label: value[i] + '',
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
    var index = app.idList.indexOf(ind);
    app.activateListItem(index);
    var selfc = app.fc.filter(ee.Filter.eq('id', ind));
    app.showSelectedPoint(ee.Feature(selfc.first()));
  };

  app.activateListItem = function(index) {
    if (index === undefined || index === null || index < 0) return;
    var widgets = app.listArea.widgets();
    if (index >= widgets.length()) return;
    var panel;
    if (app.currentSelection != -1 && app.currentSelection < widgets.length()) {
      app.prevSelection = app.currentSelection;
      panel = widgets.get(app.prevSelection);
      panel.style().set('backgroundColor', 'white');
      var prevBtn = panel.widgets().get(0);
      if (prevBtn && prevBtn.style) prevBtn.style().set('color', 'black');
    }
    app.currentSelection = index;
    panel = widgets.get(index);
    panel.style().set('backgroundColor', '#cfe8ff');
    app.widgets.del.style().set({shown: true});
  };

  app.deactivateListItem = function() {
    if (app.currentSelection != -1) {
      var widgets = app.listArea.widgets();
      if (app.currentSelection < widgets.length()) {
        var panel = widgets.get(app.currentSelection);
        panel.style().set('backgroundColor', 'white');
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
    Map.layers().set(1, ui.Map.Layer(app.fc, {}, 'Wheat GCP'));
    app.renderList(app.fc);
    app.mainMapPanel.style().set({shown: false});
    app.chartArea.clear();
    app.loading(false);
  };

  app.exportClick = function() {
    if (!app.fc) {
      app.prompt(true, app.ERROR.NO_GEOM);
      return;
    }
    var tempfc = app.fc.map(function(feature) {
      return feature.select(feature.propertyNames().remove('id'));
    });
    Export.table.toDrive({
      collection: tempfc,
      description: 'Wheat_QC',
      fileFormat: 'SHP'
    });
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

  app.onProvSelected = function() {
    if (app.widgets.irRfPicker.getValue()) {
      app.onBothSelected();
    }
  };

  app.onIRRFSelected = function() {
    if (app.widgets.provincePicker.getValue()) {
      app.onBothSelected();
    }
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
    app.loading(true);
    app.removeLayers(['Agriculture Mask', 'Wheat GCP', 'Selected']);
    var prov = app.widgets.provincePicker.getValue();
    var irrf = app.widgets.irRfPicker.getValue();
    var prefix = app.widgets.assetSource.getValue() + '/' + prov + '/' + prov + '_';
    var suffix = '_' + irrf;
    var agriId = prefix + app.PATH.AGRI + suffix;
    var wheatId = prefix + app.PATH.WHEAT + suffix;
    app.loadTable(agriId, function(agriFc, agriErr) {
      if (agriErr || !agriFc) {
        app.loading(false);
        app.prompt(true, app.ERROR.NO_FILES);
        return;
      }
      app.loadTable(wheatId, function(wheatFc, wheatErr) {
        if (wheatErr || !wheatFc) {
          app.loading(false);
          app.prompt(true, app.ERROR.NO_FILES);
          return;
        }
        app.geometry = agriFc;
        app.fc = wheatFc.map(function(feature) {
          return feature.set('id', feature.id());
        }).sort('id');
        Map.layers().set(0, ui.Map.Layer(app.geometry, {color: 'ffd468'}, 'Agriculture Mask', false));
        Map.layers().set(1, ui.Map.Layer(app.fc, {}, 'Wheat GCP'));
        Map.centerObject(app.geometry, 8);
        app.renderList(app.fc);
        app.loading(false);
      });
    });
  };

  app.maskS2clouds = function(image) {
    var qa = image.select('QA60');
    var cloudBitMask = 1 << 10;
    var cirrusBitMask = 1 << 11;
    var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
      .and(qa.bitwiseAnd(cirrusBitMask).eq(0));
    return image.updateMask(mask).copyProperties(image, ['system:time_start']);
  };

  app._addVariables = function(image) {
    var timeField = 'system:time_start';
    var startDate = app.widgets.startDate.getValue();
    var date = ee.Date(image.get(timeField));
    var years = date.difference(ee.Date(startDate), 'year');
    return image
      .addBands(image.normalizedDifference(['B8', 'B4']).rename('NDVI'))
      .addBands(ee.Image(years).rename('t'))
      .addBands(ee.Image.constant(1))
      .float();
  };

  app.makeNdviChart = function(imageCollection, region, band, scale, title) {
    return ui.Chart.image.series({
      imageCollection: imageCollection.select(band),
      region: region,
      reducer: ee.Reducer.mean(),
      scale: scale,
      xProperty: 'system:time_start'
    }).setChartType('ScatterChart')
      .setOptions({
        title: title,
        vAxis: {title: band === 'fitted' ? 'Fitted NDVI' : 'NDVI'},
        lineWidth: 1,
        pointSize: 2,
        legend: {position: 'none'}
      });
  };

  app.onShowPhenology = function(fc) {
    app.loading(true);
    app.chartArea.clear();
    var startDate = app.widgets.startDate.getValue();
    var endDate = app.widgets.endDate.getValue();
    var cloud = app.parseNumericField(app.widgets.cloud.getValue());
    var scale = app.parseNumericField(app.widgets.scale.getValue());
    var cycles = app.parseNumericField(app.widgets.cycle.getValue());
    if (!app.hasRequiredInputs(startDate, endDate, cloud, scale, cycles)) {
      app.loading(false);
      app.prompt(true, app.ERROR.EMPTY_FIELDS);
      return;
    }
    var regions = ee.FeatureCollection(fc);
    var roi = regions.geometry();
    var clipGeom = roi.bounds();
    var timeField = 'system:time_start';
    var filteredCollection = ee.ImageCollection(app.DEFAULT.S2_COLLECTION)
      .filterBounds(roi)
      .filterDate(startDate, endDate)
      .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud))
      .map(app.maskS2clouds)
      .map(app._addVariables)
      .map(function(image) {
        return image.clip(clipGeom);
      });
    filteredCollection.size().evaluate(function(n, error) {
      if (error || !n) {
        app.loading(false);
        app.prompt(true, app.ERROR.NO_IMAGES);
        return;
      }
      var timeNDVI = app.makeNdviChart(
        filteredCollection.select('NDVI'), roi, 'NDVI', scale, 'Time series NDVI');
      timeNDVI.style().set({width: '300px'});
      app.chartArea.add(timeNDVI);

      var independents = ee.List(['constant', 't']);
      var dependent = 'NDVI';
      var trend = filteredCollection.select(independents.add(dependent))
        .reduce(ee.Reducer.linearRegression(2, 1));
      var coefficients = trend.select('coefficients')
        .arrayProject([0])
        .arrayFlatten([independents]);
      var detrended = filteredCollection.map(function(image) {
        return image.select(dependent).subtract(
          image.select(independents).multiply(coefficients).reduce('sum'))
          .rename(dependent)
          .copyProperties(image, [timeField]);
      });
      var detrendedChart = app.makeNdviChart(
        detrended, roi, 'NDVI', scale, 'Detrended time series');
      detrendedChart.style().set({width: '300px'});
      app.chartArea.add(detrendedChart);

      var harmonicIndependents = ee.List(['constant', 't', 'cos', 'sin']);
      var harmonicImage = filteredCollection.map(function(image) {
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
      var harmonicNDVI = app.makeNdviChart(
        fittedHarmonic.select('NDVI'), roi, 'NDVI', scale, 'Harmonic model: original values');
      harmonicNDVI.style().set({width: '300px'});
      app.chartArea.add(harmonicNDVI);
      var harmonicFitted = app.makeNdviChart(
        fittedHarmonic.select('fitted'), roi, 'fitted', scale, 'Harmonic model: fitted values');
      harmonicFitted.style().set({width: '300px'});
      app.chartArea.add(harmonicFitted);
      app.loading(false);
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
      app.onShowPhenology(app.fc);
    });
  };

  app.mapClicked = function(latlon) {
    if (Map.getZoom() < 9) {
      app.prompt(true, app.ERROR.ZOOM_IN);
      return;
    }
    app.loading(true);
    var point = ee.Geometry.Point([latlon.lon, latlon.lat]).buffer(3 * Map.getScale());
    if (!app.fc) {
      app.currentSelection = -1;
      app.showSelectedPoint(ee.Feature(ee.Geometry.Point([latlon.lon, latlon.lat])));
      return;
    }
    var hits = app.fc.filterBounds(point);
    hits.size().evaluate(function(n, error) {
      if (error || !n) {
        app.showSelectedPoint(ee.Feature(ee.Geometry.Point([latlon.lon, latlon.lat])));
        return;
      }
      var feat = ee.Feature(hits.first());
      feat.get('id').evaluate(function(id) {
        if (Array.isArray(app.idList) && id != null) {
          app.activateListItem(app.idList.indexOf(id));
        }
      });
      app.showSelectedPoint(feat);
    });
  };

  app.showSelectedPoint = function(selected) {
    app.onShowPhenology(ee.FeatureCollection([selected]));
    app.showMonthlyComposite(selected);
    app.removeLayers(['Selected']);
    Map.layers().set(2, ui.Map.Layer(selected, {color: 'FF0000'}, 'Selected'));
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
  app.chartArea = ui.Panel({
    layout: ui.Panel.Layout.flow('vertical')
  });
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
  Map.setCenter(70.999, 33.98, 6);
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
