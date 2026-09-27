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

function buildWheatAssetIds(root, province, irrf) {
  var base = String(root || '').replace(/\/+$/, '');
  var prov = String(province || '');
  var kind = String(irrf || 'IR');
  return {
    aoi: base + '/Admin/' + prov,
    agri: base + '/IR_RF/' + prov + '_Ag_' + kind,
    gcp: base + '/GCP/' + prov + '_' + kind + '_GCP'
  };
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

function hasRequiredInputs(startDate, endDate, cloud, scale, cycles) {
  var cloudNum = parseNumericField(cloud);
  var scaleNum = parseNumericField(scale);
  var cycleNum = parseNumericField(cycles);
  return isValidIsoDate(startDate) &&
    isValidIsoDate(endDate) &&
    startDate < endDate &&
    !isNaN(cloudNum) && cloudNum >= 0 && cloudNum <= 100 &&
    !isNaN(scaleNum) && scaleNum > 0 &&
    !isNaN(cycleNum) && cycleNum > 0;
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
    var p = (list[i] && list[i].properties) || {};
    var t = parseNumericField(p.time);
    var v = parseNumericField(p.value);
    if (!isFinite(t) || !isFinite(v)) continue;
    rows.push({
      t: t,
      v: v,
      s: String(p.sample == null ? '1' : p.sample)
    });
  }
  rows.sort(function(a, b) {
    if (a.t !== b.t) return a.t - b.t;
    return a.s < b.s ? -1 : a.s > b.s ? 1 : 0;
  });
  return rows;
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
    var cells = [{v: yearFraction(t), f: isoDateFromMillis(t)}];
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
  buildWheatAssetIds: buildWheatAssetIds,
  seasonsFromRange: seasonsFromRange,
  isValidIsoDate: isValidIsoDate,
  monthStart: monthStart,
  addMonths: addMonths,
  monthWindows: monthWindows,
  parseNumericField: parseNumericField,
  hasRequiredInputs: hasRequiredInputs,
  yearFraction: yearFraction,
  isoDateFromMillis: isoDateFromMillis,
  collectChartRows: collectChartRows,
  buildNumericChartTable: buildNumericChartTable
};
