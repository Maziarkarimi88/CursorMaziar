/**
 * MODULE 2 — Wheat GCP preprocessing for the Earth Engine Code Editor.
 *
 * Continuation of MODULE 1 (gee/wheat_phenology_app.js).
 * Visualize the agriculture mask and GPS points, optionally merge extra
 * quality-wheat GCPs from Module 1, split 70/30 train/validate, then export.
 *
 * Your asset layout (same as Module 1):
 *   {root}/Admin/{Province}
 *   {root}/IR_RF/{Province}_Ag_{IR|RF}
 *   {root}/GCP/{Province}_{IR|RF}_GCP
 *
 * Optional extra GPS: a folder of point tables, or one FeatureCollection
 * (quality wheat remaining after Module 1). Leave blank to split the
 * province GCP table only.
 *
 * Merged / train / validate assets written under GCP/:
 *   {root}/GCP/{Province}_{IR|RF}_GCP_MERGED
 *   {root}/GCP/{Province}_{IR|RF}_GCP_TRAIN
 *   {root}/GCP/{Province}_{IR|RF}_GCP_VALIDATE
 *
 * How to run:
 * 1. Open https://code.earthengine.google.com/ and sign in.
 * 2. Profile menu > Change Cloud Project > ee-maziarkarimi3
 * 3. If Run/Save/Get Link are gray, register at
 *    https://code.earthengine.google.com/register then reload.
 * 4. Replace the entire editor contents with this script and click Run.
 * 5. Select a province and IR or RF, optionally paste an additional GPS
 *    folder or table, click Merge, then Export. Confirm each task with RUN.
 */

var app = {};

app.createConstants = function() {
  app.DEFAULT = {
    ASSET_SOURCE: 'projects/ee-maziarkarimi3/assets/Wheat_Mapping',
    TRAIN_RATIO: 0.7
  };
  app.LABEL = {
    TITLE: 'Wheat GCP Preprocessing',
    ASSET_SOURCE: 'Geometry Assets Folder',
    PROVINCE: 'Select Province',
    IRRF: 'Select IR or RF',
    ADDITIONAL: 'Select additional GCP folder (optional)',
    ADDITIONAL_HINT: 'Module 1 quality wheat GPS: a folder of point tables, or one table. Leave blank to skip.',
    MERGE: 'Merge all GCP and split to training/validation datasets',
    EXPORT: 'Export'
  };
  app.LAYER = {
    AGRI: 'Agriculture Mask',
    PROVINCE_GPS: 'Sample GCP',
    MERGED: 'Merged GCP',
    TRAIN: 'Training Points',
    VALIDATE: 'Validation Points'
  };
  app.PATH = {
    ADMIN: 'Admin',
    AGRI: 'IR_RF',
    GCP: 'GCP'
  };
  app.ERROR = {
    NO_PROVINCE: 'Please select a province',
    NO_IRRF: 'Please select IR or RF',
    NO_GCP: 'Load a province and IR or RF first so Sample GCP is on the map.',
    STH_WRONG: 'Error!! Something went wrong! Please check data sources',
    MERGED_EXISTS: 'A merged file already exists, proceed regardless?',
    NO_FILES: 'Files not found! Please make sure the required files exist!',
    NO_FOLDER: 'Could not list provinces. Check the folder path and that you have access.',
    NO_ADDITIONAL: 'Additional GPS path was not a table or a folder of point tables. Using province GCP only.'
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

  app.isPointTableType = function(type) {
    var t = String(type || '').toUpperCase().replace(/ /g, '_');
    return t === 'TABLE' || t === 'FEATURE_COLLECTION' ||
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

  app.collectPointTableIds = function(assets) {
    var list = Array.isArray(assets) ? assets : (assets && assets.assets) || [];
    var ids = [];
    for (var i = 0; i < list.length; i++) {
      var element = list[i] || {};
      if (!app.isPointTableType(element.type)) continue;
      var assetId = element.id || element.name || '';
      if (assetId && ids.indexOf(assetId) === -1) ids.push(assetId);
    }
    return ids;
  };

  app.buildWheatAssetIds = function(root, province, irrf) {
    var base = String(root || '').replace(/\/+$/, '');
    var prov = String(province || '');
    var kind = String(irrf || 'IR');
    var gcp = base + '/' + app.PATH.GCP + '/' + prov + '_' + kind + '_GCP';
    return {
      aoi: base + '/' + app.PATH.ADMIN + '/' + prov,
      agri: base + '/' + app.PATH.AGRI + '/' + prov + '_Ag_' + kind,
      gcp: gcp,
      gcpMerged: gcp + '_MERGED',
      gcpTrain: gcp + '_TRAIN',
      gcpValidate: gcp + '_VALIDATE'
    };
  };

  app.splitTrainValidateThreshold = function(ratio) {
    var n = Number(ratio);
    if (!isFinite(n) || n <= 0 || n >= 1) return app.DEFAULT.TRAIN_RATIO;
    return n;
  };

  app.exportDescriptions = function(province, irrf) {
    var prov = String(province || 'Province').replace(/[^\w]+/g, '_');
    var kind = String(irrf || 'IR');
    return {
      merged: prov + '_' + kind + '_GCP_MERGED',
      train: prov + '_' + kind + '_GCP_TRAIN',
      validate: prov + '_' + kind + '_GCP_VALIDATE'
    };
  };

  app.shouldConfirmMerged = function(mergedExists, additionalSource) {
    return !!mergedExists && String(additionalSource || '').trim() !== '';
  };

  app.prompt = function(state, text) {
    app.promptPanel.style().set('shown', state);
    app.promptBox.text.setValue(text || '');
    app.promptBox.text.style().set('shown', state);
  };

  app.loading = function(state) {
    if (state) app.prompt(true, 'Loading...');
    else app.prompt(false, '');
    app.widgets.provincePicker.setDisabled(state);
    app.widgets.irRfPicker.setDisabled(state);
    app.widgets.additionalGPSSource.setDisabled(state);
    app.widgets.mergeGPSBtn.setDisabled(state);
    app.widgets.exportBtn.setDisabled(state);
    app.widgets.mergeGPSBtn.style().set('shown', true);
    app.widgets.exportBtn.style().set('shown', !!app.trainPoints);
  };

  app.confirm = function(text, okBind, cancelBind) {
    app.promptPanel.style().set('shown', true);
    app.promptBox.text.setValue(text);
    app.promptBox.text.style().set('shown', true);
    app.promptBox.ok.style().set('shown', true);
    app.promptBox.cancel.style().set('shown', true);
    app.widgets.mergeGPSBtn.setDisabled(true);
    app.widgets.exportBtn.setDisabled(true);
    app.promptBox.ok.onClick(function() {
      app.promptBox.ok.style().set('shown', false);
      app.promptBox.cancel.style().set('shown', false);
      app.promptPanel.style().set('shown', false);
      okBind();
    });
    app.promptBox.cancel.onClick(function() {
      app.promptBox.ok.style().set('shown', false);
      app.promptBox.cancel.style().set('shown', false);
      app.promptPanel.style().set('shown', false);
      cancelBind();
    });
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
    var mapLayers = Map.layers();
    var toRemove = [];
    for (var i = 0; i < mapLayers.length(); i++) {
      var layer = mapLayers.get(i);
      if (names.indexOf(layer.getName()) > -1) toRemove.push(layer);
    }
    for (var j = 0; j < toRemove.length; j++) mapLayers.remove(toRemove[j]);
  };

  app.currentIds = function() {
    return app.buildWheatAssetIds(
      app.widgets.assetSource.getValue(),
      app.widgets.provincePicker.getValue(),
      app.widgets.irRfPicker.getValue()
    );
  };

  app.populatePickers = function() {
    var root = app.widgets.assetSource.getValue();
    var adminFolder = String(root || '').replace(/\/+$/, '') + '/' + app.PATH.ADMIN;
    app.loading(true);
    app.listFolderAssets(adminFolder, function(assets, error) {
      var names = app.collectProvinceNames(assets);
      if (!names.length) names = ['Nangarhar'];
      app.widgets.provincePicker.items().reset(names);
      app.loading(false);
      if (error && !assets.length) {
        app.prompt(true, app.ERROR.NO_FOLDER + ' Showing Nangarhar as a fallback.');
        print('Admin folder list error:', error);
      }
    });
  };

  app.onProvSelected = function() {
    if (app.widgets.irRfPicker.getValue()) app.onBothSelected();
  };

  app.onIRRFSelected = function() {
    if (app.widgets.provincePicker.getValue()) app.onBothSelected();
  };

  app.onBothSelected = function() {
    var ids = app.currentIds();
    app.loading(true);
    app.mergedGPS = null;
    app.mergedGPSLayer = null;
    app.trainPoints = null;
    app.validatePoints = null;
    app.widgets.exportBtn.style().set('shown', false);
    app.removeLayers([
      app.LAYER.AGRI, app.LAYER.PROVINCE_GPS, app.LAYER.MERGED,
      app.LAYER.TRAIN, app.LAYER.VALIDATE
    ]);
    print('Loading assets', ids);
    app.loadTable(ids.agri, function(agriFc, agriErr) {
      if (agriErr || !agriFc) {
        app.loading(false);
        app.prompt(true, app.ERROR.NO_FILES);
        return;
      }
      app.loadTable(ids.gcp, function(gcpFc, gcpErr) {
        if (gcpErr || !gcpFc) {
          app.loading(false);
          app.prompt(true, app.ERROR.NO_FILES);
          return;
        }
        app.geometry = agriFc;
        app.provinceGPSLayer = gcpFc;
        Map.addLayer(app.geometry, {color: 'ffd468'}, app.LAYER.AGRI, false);
        Map.addLayer(app.provinceGPSLayer, {color: 'red'}, app.LAYER.PROVINCE_GPS);
        Map.centerObject(app.geometry, 8);
        app.loadTable(ids.gcpMerged, function(mergedFc) {
          if (mergedFc) {
            app.mergedGPS = mergedFc;
            Map.addLayer(app.mergedGPS, {color: 'ffd82d'}, app.LAYER.MERGED, false);
            print('Existing merged GCP found', ids.gcpMerged);
          }
          app.provinceGPSLayer.size().evaluate(function(n) {
            print('Sample GCP points loaded:', n);
          });
          app.loading(false);
        });
      });
    });
  };

  app.mergeCollections = function(baseFc, extraIds, index, callback) {
    if (index >= extraIds.length) {
      callback(baseFc);
      return;
    }
    app.loadTable(extraIds[index], function(fc) {
      var next = baseFc;
      if (fc) next = baseFc.merge(fc);
      app.mergeCollections(next, extraIds, index + 1, callback);
    });
  };

  app.mergeAdditionalGps = function(sourceId, baseFc, callback) {
    var extra = String(sourceId || '').trim();
    if (!extra) {
      callback(baseFc, null);
      return;
    }
    app.loadTable(extra, function(fc) {
      if (fc) {
        callback(baseFc.merge(fc), null);
        return;
      }
      app.listFolderAssets(extra, function(assets, error) {
        var ids = app.collectPointTableIds(assets);
        if (!ids.length) {
          print('Additional GPS list error:', error || 'no point tables');
          callback(baseFc, error || 'no additional tables');
          return;
        }
        print('Merging additional GPS tables', ids);
        app.mergeCollections(baseFc, ids, 0, function(merged) {
          callback(merged, null);
        });
      });
    });
  };

  app.splitTrainValidate = function(layer) {
    var threshold = app.splitTrainValidateThreshold(app.DEFAULT.TRAIN_RATIO);
    var withRandom = ee.FeatureCollection(layer).randomColumn('random');
    app.trainPoints = withRandom.filter(ee.Filter.lt('random', threshold));
    app.validatePoints = withRandom.filter(ee.Filter.gte('random', threshold));
    app.removeLayers([app.LAYER.TRAIN, app.LAYER.VALIDATE]);
    Map.addLayer(app.trainPoints, {color: 'red'}, app.LAYER.TRAIN);
    Map.addLayer(app.validatePoints, {color: 'green'}, app.LAYER.VALIDATE);
    app.widgets.exportBtn.style().set('shown', true);
    app.trainPoints.size().evaluate(function(nTrain) {
      app.validatePoints.size().evaluate(function(nVal) {
        app.prompt(true, 'Split complete: ' + nTrain + ' training, ' +
          nVal + ' validation (70/30). Click Export, then RUN each task.');
        print('Training points:', nTrain, 'Validation points:', nVal);
      });
    });
  };

  app.initiateMerge = function() {
    if (!app.provinceGPSLayer) {
      app.prompt(true, app.ERROR.NO_GCP);
      return;
    }
    app.loading(true);
    var extra = app.widgets.additionalGPSSource.getValue();
    app.mergeAdditionalGps(extra, app.provinceGPSLayer, function(merged, err) {
      app.mergedGPSLayer = merged;
      app.removeLayers([app.LAYER.MERGED, app.LAYER.TRAIN, app.LAYER.VALIDATE]);
      Map.addLayer(app.mergedGPSLayer, {color: 'ffd82d'}, app.LAYER.MERGED, false);
      app.loading(false);
      if (err) print(app.ERROR.NO_ADDITIONAL, err);
      app.splitTrainValidate(app.mergedGPSLayer);
    });
  };

  app.mergeGPS = function() {
    if (!app.widgets.provincePicker.getValue()) {
      app.prompt(true, app.ERROR.NO_PROVINCE);
      return;
    }
    if (!app.widgets.irRfPicker.getValue()) {
      app.prompt(true, app.ERROR.NO_IRRF);
      return;
    }
    if (!app.provinceGPSLayer) {
      app.prompt(true, app.ERROR.NO_GCP);
      return;
    }
    var extra = app.widgets.additionalGPSSource.getValue();
    if (app.shouldConfirmMerged(app.mergedGPS, extra)) {
      app.confirm(app.ERROR.MERGED_EXISTS, app.initiateMerge, function() {
        app.mergedGPSLayer = app.mergedGPS;
        app.splitTrainValidate(app.mergedGPSLayer);
      });
      return;
    }
    app.initiateMerge();
  };

  app.export = function() {
    if (!app.mergedGPSLayer || !app.trainPoints || !app.validatePoints) {
      app.prompt(true, 'Merge and split first, then Export.');
      return;
    }
    var ids = app.currentIds();
    var names = app.exportDescriptions(
      app.widgets.provincePicker.getValue(),
      app.widgets.irRfPicker.getValue()
    );
    Export.table.toDrive({
      collection: app.mergedGPSLayer,
      description: names.merged,
      fileFormat: 'SHP'
    });
    Export.table.toDrive({
      collection: app.trainPoints,
      description: names.train,
      fileFormat: 'SHP'
    });
    Export.table.toDrive({
      collection: app.validatePoints,
      description: names.validate,
      fileFormat: 'SHP'
    });
    Export.table.toAsset({
      collection: app.mergedGPSLayer,
      description: names.merged,
      assetId: ids.gcpMerged
    });
    Export.table.toAsset({
      collection: app.trainPoints,
      description: names.train,
      assetId: ids.gcpTrain
    });
    Export.table.toAsset({
      collection: app.validatePoints,
      description: names.validate,
      assetId: ids.gcpValidate
    });
    app.prompt(true, 'Six export tasks queued (Drive SHP + Assets). Open Tasks and click RUN.');
    print('Queued Drive + Asset exports', names, ids);
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
    additionalGPSSource: ui.Textbox({
      value: '',
      placeholder: 'Optional folder or table asset ID',
      style: {stretch: 'horizontal', padding: '0px 0px 20px 0px'}
    }),
    mergeGPSBtn: ui.Button({
      label: app.LABEL.MERGE,
      onClick: app.mergeGPS,
      style: {stretch: 'horizontal'}
    }),
    exportBtn: ui.Button({
      label: app.LABEL.EXPORT,
      onClick: app.export,
      style: {stretch: 'horizontal', shown: false}
    })
  };
  app.promptBox = {
    text: ui.Label({
      value: '',
      style: {shown: true}
    }),
    ok: ui.Button({
      label: 'OK',
      style: {shown: false}
    }),
    cancel: ui.Button({
      label: 'Cancel',
      style: {shown: false}
    })
  };
  app.mainPanel = ui.Panel({
    style: {width: '300px'},
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
      app.widgets.assetSource,
      ui.Label({
        value: app.LABEL.PROVINCE,
        style: {fontWeight: 'bold', margin: '10px 10px 0px 10px'}
      }),
      app.widgets.provincePicker,
      app.widgets.irRfPicker,
      ui.Label({
        value: app.LABEL.ADDITIONAL,
        style: {margin: '10px 10px 0px 10px'}
      }),
      ui.Label({
        value: app.LABEL.ADDITIONAL_HINT,
        style: {margin: '0px 10px 0px 10px', fontSize: '11px', color: 'gray'}
      }),
      app.widgets.additionalGPSSource,
      app.widgets.mergeGPSBtn,
      app.widgets.exportBtn
    ]
  });
  app.promptPanel = ui.Panel({
    style: {shown: false, textAlign: 'center'},
    widgets: [
      app.promptBox.text,
      ui.Panel({
        layout: ui.Panel.Layout.flow('horizontal'),
        widgets: [app.promptBox.ok, app.promptBox.cancel]
      })
    ]
  });
};

app.init = function() {
  Map.setOptions('HYBRID');
  Map.setCenter(70.999, 33.98, 6);
  app.createConstants();
  app.createHelpers();
  app.initializeGUIElements();
  app.populatePickers();
  Map.add(app.promptPanel);
  ui.root.insert(0, app.mainPanel);
};

app.init();
