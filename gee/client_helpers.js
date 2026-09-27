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
  hasRequiredInputs: hasRequiredInputs
};
