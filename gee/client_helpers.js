/**
 * Pure client-side helpers shared by the GEE wheat phenology app.
 * These run in Node tests and are inlined in wheat_phenology_mapping.js
 * because the Earth Engine Code Editor cannot `require()` modules.
 */

function isFolderType(type) {
  if (!type) return false;
  return String(type).toUpperCase() === 'FOLDER';
}

function assetShortName(assetId) {
  if (!assetId) return '';
  var parts = String(assetId).replace(/\/+$/, '').split('/');
  return parts[parts.length - 1];
}

function collectFolderNames(assets) {
  var list = Array.isArray(assets) ? assets : (assets && assets.assets) || [];
  var ids = [];
  for (var i = 0; i < list.length; i++) {
    var element = list[i] || {};
    if (!isFolderType(element.type)) continue;
    var assetId = element.id || element.name || '';
    var name = assetShortName(assetId);
    if (name) ids.push(name);
  }
  return ids;
}

function isProvinceAssetType(type) {
  var t = String(type || '').toUpperCase().replace(/ /g, '_');
  return t === 'FOLDER' || t === 'TABLE' || t === 'FEATURE_COLLECTION' ||
    t === 'FEATURECOLLECTION' || t === 'ASSET';
}

function collectProvinceNames(assets) {
  var list = Array.isArray(assets) ? assets : (assets && assets.assets) || [];
  var ids = [];
  for (var i = 0; i < list.length; i++) {
    var element = list[i] || {};
    if (!isProvinceAssetType(element.type)) continue;
    var name = assetShortName(element.id || element.name || '');
    if (name && ids.indexOf(name) === -1) ids.push(name);
  }
  return ids.sort();
}

function isPointTableType(type) {
  var t = String(type || '').toUpperCase().replace(/ /g, '_');
  return t === 'TABLE' || t === 'FEATURE_COLLECTION' ||
    t === 'FEATURECOLLECTION' || t === 'ASSET';
}

function collectPointTableIds(assets) {
  var list = Array.isArray(assets) ? assets : (assets && assets.assets) || [];
  var ids = [];
  for (var i = 0; i < list.length; i++) {
    var element = list[i] || {};
    if (!isPointTableType(element.type)) continue;
    var assetId = element.id || element.name || '';
    if (assetId && ids.indexOf(assetId) === -1) ids.push(assetId);
  }
  return ids;
}

function buildWheatAssetIds(root, province, irrf) {
  var base = String(root || '').replace(/\/+$/, '');
  var prov = String(province || '');
  var kind = String(irrf || 'IR');
  var gcp = base + '/GCP/' + prov + '_' + kind + '_GCP';
  return {
    aoi: base + '/Admin/' + prov,
    agri: base + '/IR_RF/' + prov + '_Ag_' + kind,
    gcp: gcp,
    gcpMerged: gcp + '_MERGED',
    gcpTrain: gcp + '_TRAIN',
    gcpValidate: gcp + '_VALIDATE',
    gcpQuality: gcp + '_QUALITY'
  };
}

function splitTrainValidateThreshold(ratio) {
  var n = Number(ratio);
  if (!isFinite(n) || n <= 0 || n >= 1) return 0.7;
  return n;
}

function classifyRandomSplit(randomValues, ratio) {
  var threshold = splitTrainValidateThreshold(ratio);
  var values = Array.isArray(randomValues) ? randomValues : [];
  var train = [];
  var validate = [];
  for (var i = 0; i < values.length; i++) {
    var v = Number(values[i]);
    if (!isFinite(v)) continue;
    if (v < threshold) train.push(v);
    else validate.push(v);
  }
  return {train: train, validate: validate, threshold: threshold};
}

function shouldConfirmMerged(mergedExists, additionalSource) {
  return !!mergedExists && String(additionalSource || '').trim() !== '';
}

function exportDescriptions(province, irrf) {
  var prov = String(province || 'Province').replace(/[^\w]+/g, '_');
  var kind = String(irrf || 'IR');
  return {
    merged: prov + '_' + kind + '_GCP_MERGED',
    train: prov + '_' + kind + '_GCP_TRAIN',
    validate: prov + '_' + kind + '_GCP_VALIDATE'
  };
}

function opticalExportDescriptions(province, irrf) {
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
}

function buildOpticalAssetIds(root, province, irrf) {
  var base = String(root || '').replace(/\/+$/, '');
  var names = opticalExportDescriptions(province, irrf);
  var folder = base + '/Optical/';
  return {
    ndviSowing: folder + names.ndviSowing,
    ndviPeak: folder + names.ndviPeak,
    ndsiPeak: folder + names.ndsiPeak,
    ndviHarvest: folder + names.ndviHarvest,
    finalMask: folder + names.finalMask
  };
}

function compositeReducerName(filter) {
  var f = String(filter || 'Median');
  if (f === 'Mean' || f === 'Mode' || f === 'Max' || f === 'Min') return f;
  return 'Median';
}

function ndviPairInRange(minNdvi, maxNdvi, range) {
  var minN = parseNumericField(minNdvi);
  var maxN = parseNumericField(maxNdvi);
  if (isNaN(minN) || isNaN(maxN) || minN > maxN) return false;
  if (!range || range.length < 2) return true;
  return minN >= range[0] && maxN <= range[1];
}

function ndviMinInRange(minNdvi, range) {
  var minN = parseNumericField(minNdvi);
  if (isNaN(minN)) return false;
  if (!range || range.length < 2) return true;
  return minN >= range[0] && minN <= range[1];
}

function opticalSeasonInputsValid(opts) {
  opts = opts || {};
  if (!isValidIsoDate(opts.startDate) || !isValidIsoDate(opts.endDate) ||
      opts.startDate >= opts.endDate) {
    return false;
  }
  var cloudNum = parseNumericField(opts.cloud);
  if (isNaN(cloudNum) || cloudNum < 0 || cloudNum > 100) return false;
  if (!opts.filter) return false;
  if (opts.requireMax) return ndviPairInRange(opts.minNdvi, opts.maxNdvi, opts.range);
  return ndviMinInRange(opts.minNdvi, opts.range);
}

function keepPeakWheatPixel(ndvi, ndsi, minNdvi) {
  return Number(ndvi) > Number(minNdvi) && Number(ndsi) < 0;
}

function chooseFinalMaskLayer(hasHarvest, hasPeak, hasSowing) {
  if (hasHarvest) return 'harvest';
  if (hasPeak) return 'peak';
  if (hasSowing) return 'sowing';
  return null;
}

function normalizeLonLatBox(west, south, east, north) {
  west = parseNumericField(west);
  south = parseNumericField(south);
  east = parseNumericField(east);
  north = parseNumericField(north);
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
}

function flattenLonLatPairs(node, out) {
  out = out || [];
  if (!node) return out;
  if (typeof node[0] === 'number' && typeof node[1] === 'number') {
    out.push([parseNumericField(node[0]), parseNumericField(node[1])]);
    return out;
  }
  if (Array.isArray(node)) {
    for (var i = 0; i < node.length; i++) flattenLonLatPairs(node[i], out);
  }
  return out;
}

function parseMapBounds(source) {
  if (!source) return null;
  if (source.bounds && source.bounds !== source) {
    var fromEvent = parseMapBounds(source.bounds);
    if (fromEvent) return fromEvent;
  }
  if (source.geometry && source.geometry !== source) {
    var fromGeom = parseMapBounds(source.geometry);
    if (fromGeom) return fromGeom;
  }
  if (source.bbox && source.bbox.length >= 4) {
    var fromBbox = normalizeLonLatBox(
      source.bbox[0], source.bbox[1], source.bbox[2], source.bbox[3]
    );
    if (fromBbox) return fromBbox;
  }
  if (source.west != null && source.south != null &&
      source.east != null && source.north != null) {
    return normalizeLonLatBox(source.west, source.south, source.east, source.north);
  }
  if (source.coordinates) {
    var pairs = flattenLonLatPairs(source.coordinates, []);
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
      return normalizeLonLatBox(west, south, east, north);
    }
  }
  if (Array.isArray(source) && source.length === 4 && !Array.isArray(source[0])) {
    return normalizeLonLatBox(source[0], source[1], source[2], source[3]);
  }
  return null;
}

function seasonsFromRange(startIso, endIso) {
  var sy = String(startIso).slice(0, 4);
  var ey = String(endIso).slice(0, 4);
  if (!ey) ey = String(parseInt(sy, 10) + 1);
  return [
    {id: 'sowing', label: 'Sowing', start: sy + '-11-15', end: sy + '-12-31'},
    {id: 'peak', label: 'Peak', start: ey + '-02-01', end: ey + '-03-31'},
    {id: 'harvest', label: 'Harvest', start: ey + '-05-01', end: ey + '-06-15'}
  ];
}

function isValidIsoDate(value) {
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
}

function monthStart(isoDate) {
  var parts = String(isoDate).split('-');
  return parts[0] + '-' + parts[1] + '-01';
}

function pad2(n) {
  return (n < 10 ? '0' : '') + n;
}

function addMonths(isoDate, n) {
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
  return y + '-' + pad2(m) + '-' + d;
}

function monthWindows(startIso, endIso) {
  var windows = [];
  if (!isValidIsoDate(startIso) || !isValidIsoDate(endIso) || startIso >= endIso) {
    return windows;
  }
  var cursor = monthStart(startIso);
  var endExclusive = addMonths(monthStart(endIso), 1);
  var guard = 0;
  while (cursor < endExclusive && guard < 24) {
    var next = addMonths(cursor, 1);
    windows.push({
      start: cursor,
      end: next,
      label: cursor.slice(0, 7)
    });
    cursor = next;
    guard += 1;
  }
  return windows;
}

function parseNumericField(value) {
  if (value === null || value === undefined || value === '') return NaN;
  return typeof value === 'number' ? value : parseFloat(value);
}

function coerceChartNumber(value, asTime) {
  if (value === null || value === undefined || value === '') return NaN;
  if (typeof value === 'number') return isFinite(value) ? value : NaN;
  if (typeof value === 'boolean') return NaN;
  if (typeof value === 'object') {
    if (typeof value.getTime === 'function') {
      var ms = value.getTime();
      return isFinite(ms) ? ms : NaN;
    }
    if (value.value !== undefined && value.value !== value) {
      return coerceChartNumber(value.value, asTime);
    }
    return NaN;
  }
  var text = String(value).trim();
  var dateCtor = text.match(/^Date\((\d+)\)$/);
  if (dateCtor) return coerceChartNumber(Number(dateCtor[1]), asTime);
  if (asTime && /^\d{4}-\d{2}-\d{2}/.test(text)) {
    var parsed = Date.parse(text);
    return isFinite(parsed) ? parsed : NaN;
  }
  var n = parseFloat(text);
  return isFinite(n) ? n : NaN;
}

function featureProperties(feature) {
  if (!feature) return {};
  if (feature.properties && typeof feature.properties === 'object') return feature.properties;
  return feature;
}

function sortChartRows(rows) {
  rows.sort(function(a, b) {
    if (a.t !== b.t) return a.t - b.t;
    return a.s < b.s ? -1 : a.s > b.s ? 1 : 0;
  });
  return rows;
}

function groupChartRowsBySample(rows) {
  var groups = [];
  var index = {};
  rows = Array.isArray(rows) ? rows : [];
  for (var i = 0; i < rows.length; i++) {
    var s = String(rows[i].s);
    if (index[s] === undefined) {
      index[s] = groups.length;
      groups.push({sample: s, rows: []});
    }
    groups[index[s]].rows.push(rows[i]);
  }
  return groups;
}

function uniqueSampleIds(rows) {
  var ids = [];
  var seen = {};
  rows = Array.isArray(rows) ? rows : [];
  for (var i = 0; i < rows.length; i++) {
    var s = String(rows[i].s);
    if (seen[s]) continue;
    seen[s] = true;
    ids.push(s);
  }
  return ids;
}

function filterChartRowsBySample(rows, sampleId) {
  rows = Array.isArray(rows) ? rows : [];
  if (sampleId === null || sampleId === undefined || sampleId === '') return rows;
  var want = String(sampleId);
  var out = [];
  for (var i = 0; i < rows.length; i++) {
    if (String(rows[i].s) === want) out.push(rows[i]);
  }
  return out;
}

function chartTitle(base, singleSample) {
  return String(base) + (singleSample ? ' (selected sample)' : ' (all samples)');
}

function averageRowsBySampleTime(rows) {
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
  return sortChartRows(out);
}

function hasRequiredInputs(startDate, endDate, cloud, scale, cycles) {
  var cloudNum = parseNumericField(cloud);
  var scaleNum = parseNumericField(scale);
  var cycleNum = parseNumericField(cycles);
  var cyclesOk = cycles === null || cycles === undefined || cycles === '' ||
    (!isNaN(cycleNum) && cycleNum > 0);
  return isValidIsoDate(startDate) &&
    isValidIsoDate(endDate) &&
    startDate < endDate &&
    !isNaN(cloudNum) && cloudNum >= 0 && cloudNum <= 100 &&
    !isNaN(scaleNum) && scaleNum > 0 &&
    cyclesOk;
}

function yearFraction(millis) {
  var t = Number(millis);
  if (!isFinite(t)) return NaN;
  var d = new Date(t);
  var y = d.getUTCFullYear();
  var start = Date.UTC(y, 0, 1);
  var end = Date.UTC(y + 1, 0, 1);
  return y + (t - start) / (end - start);
}

function isoDateFromMillis(millis) {
  var d = new Date(Number(millis));
  if (isNaN(d.getTime())) return '';
  var y = d.getUTCFullYear();
  var m = d.getUTCMonth() + 1;
  var day = d.getUTCDate();
  return y + '-' + (m < 10 ? '0' : '') + m + '-' + (day < 10 ? '0' : '') + day;
}

function collectChartRows(features) {
  var rows = [];
  var list = Array.isArray(features) ? features : [];
  for (var i = 0; i < list.length; i++) {
    var p = featureProperties(list[i]);
    var t = coerceChartNumber(p.time != null ? p.time : p.millis, true);
    var v = coerceChartNumber(
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
  return sortChartRows(rows);
}

function collectChartRowsFromArrays(times, values, samples) {
  times = Array.isArray(times) ? times : [];
  values = Array.isArray(values) ? values : [];
  samples = Array.isArray(samples) ? samples : [];
  var rows = [];
  var n = Math.min(times.length, values.length);
  for (var i = 0; i < n; i++) {
    var t = coerceChartNumber(times[i], true);
    var v = coerceChartNumber(values[i], false);
    if (!isFinite(t) || !isFinite(v)) continue;
    rows.push({
      t: t,
      v: v,
      s: String(samples[i] == null ? String(i + 1) : samples[i])
    });
  }
  return sortChartRows(rows);
}

function collectChartRowsFromGetRegion(table, band) {
  if (!Array.isArray(table) || table.length < 2 || !Array.isArray(table[0])) return [];
  var header = table[0];
  var timeIdx = header.indexOf('time');
  if (timeIdx < 0) timeIdx = 3;
  var valueIdx = -1;
  if (band) valueIdx = header.indexOf(band);
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
    var t = coerceChartNumber(r[timeIdx], true);
    var v = coerceChartNumber(r[valueIdx], false);
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
  return averageRowsBySampleTime(rows);
}

function buildNumericChartTable(rows) {
  rows = Array.isArray(rows) ? rows : [];
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

  var cols = [{id: 'x', label: 'Date', type: 'date', role: 'domain'}];
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
    var cells = [{v: 'Date(' + Math.round(t) + ')', f: isoDateFromMillis(t)}];
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
}

module.exports = {
  isFolderType: isFolderType,
  assetShortName: assetShortName,
  collectFolderNames: collectFolderNames,
  isProvinceAssetType: isProvinceAssetType,
  collectProvinceNames: collectProvinceNames,
  isPointTableType: isPointTableType,
  collectPointTableIds: collectPointTableIds,
  buildWheatAssetIds: buildWheatAssetIds,
  splitTrainValidateThreshold: splitTrainValidateThreshold,
  classifyRandomSplit: classifyRandomSplit,
  shouldConfirmMerged: shouldConfirmMerged,
  exportDescriptions: exportDescriptions,
  opticalExportDescriptions: opticalExportDescriptions,
  buildOpticalAssetIds: buildOpticalAssetIds,
  compositeReducerName: compositeReducerName,
  ndviPairInRange: ndviPairInRange,
  ndviMinInRange: ndviMinInRange,
  opticalSeasonInputsValid: opticalSeasonInputsValid,
  keepPeakWheatPixel: keepPeakWheatPixel,
  chooseFinalMaskLayer: chooseFinalMaskLayer,
  normalizeLonLatBox: normalizeLonLatBox,
  parseMapBounds: parseMapBounds,
  seasonsFromRange: seasonsFromRange,
  isValidIsoDate: isValidIsoDate,
  monthStart: monthStart,
  addMonths: addMonths,
  monthWindows: monthWindows,
  parseNumericField: parseNumericField,
  hasRequiredInputs: hasRequiredInputs,
  yearFraction: yearFraction,
  isoDateFromMillis: isoDateFromMillis,
  coerceChartNumber: coerceChartNumber,
  collectChartRows: collectChartRows,
  collectChartRowsFromArrays: collectChartRowsFromArrays,
  collectChartRowsFromGetRegion: collectChartRowsFromGetRegion,
  uniqueSampleIds: uniqueSampleIds,
  groupChartRowsBySample: groupChartRowsBySample,
  filterChartRowsBySample: filterChartRowsBySample,
  chartTitle: chartTitle,
  buildNumericChartTable: buildNumericChartTable
};
