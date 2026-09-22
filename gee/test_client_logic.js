/**
 * Node tests for wheat phenology client logic and static checks
 * against the Earth Engine Code Editor script.
 */
var assert = require('assert');
var fs = require('fs');
var path = require('path');
var helpers = require('./client_helpers');

var failures = 0;
function check(name, fn) {
  try {
    fn();
    console.log('PASS  ' + name);
  } catch (err) {
    failures += 1;
    console.log('FAIL  ' + name);
    console.log('      ' + err.message);
  }
}

check('folder type accepts legacy and Cloud API values', function() {
  assert.strictEqual(helpers.isFolderType('Folder'), true);
  assert.strictEqual(helpers.isFolderType('FOLDER'), true);
  assert.strictEqual(helpers.isFolderType('Table'), false);
  assert.strictEqual(helpers.isFolderType(undefined), false);
});

check('assetShortName uses the last path segment', function() {
  assert.strictEqual(
    helpers.assetShortName('projects/servir-hkh/WheatMapping/2017/Afghanistan/Hilmand'),
    'Hilmand'
  );
  assert.strictEqual(
    helpers.assetShortName('projects/servir-hkh/assets/WheatMapping/2017/Afghanistan/Hilmand/'),
    'Hilmand'
  );
});

check('collectFolderNames handles getList arrays and listAssets objects', function() {
  var fromGetList = helpers.collectFolderNames([
    {type: 'Folder', id: 'projects/x/Afghanistan/Hilmand'},
    {type: 'Table', id: 'projects/x/Afghanistan/notes'}
  ]);
  var fromListAssets = helpers.collectFolderNames({
    assets: [
      {type: 'FOLDER', name: 'projects/x/assets/Afghanistan/Kabul'},
      {type: 'TABLE', name: 'projects/x/assets/Afghanistan/Kabul_Wheat_IR'}
    ]
  });
  assert.deepStrictEqual(fromGetList, ['Hilmand']);
  assert.deepStrictEqual(fromListAssets, ['Kabul']);
  assert.deepStrictEqual(helpers.collectFolderNames(null), []);
  assert.deepStrictEqual(helpers.collectFolderNames(undefined), []);
});

check('null/undefined asset lists do not throw (original getList crash)', function() {
  assert.doesNotThrow(function() {
    helpers.collectFolderNames(null);
  });
});

check('month windows cover the default Afghanistan wheat season', function() {
  var windows = helpers.monthWindows('2016-11-01', '2017-05-30');
  assert.strictEqual(windows.length, 7);
  assert.strictEqual(windows[0].start, '2016-11-01');
  assert.strictEqual(windows[0].end, '2016-12-01');
  assert.strictEqual(windows[0].label, '2016-11');
  assert.strictEqual(windows[6].start, '2017-05-01');
  assert.strictEqual(windows[6].end, '2017-06-01');
});

check('invalid dates produce no month windows and no infinite loop', function() {
  assert.deepStrictEqual(helpers.monthWindows('bad', '2017-05-30'), []);
  assert.deepStrictEqual(helpers.monthWindows('2017-05-30', '2016-11-01'), []);
});

check('required inputs reject empty, inverted, and non-numeric values', function() {
  assert.strictEqual(helpers.hasRequiredInputs('2016-11-01', '2017-05-30', 30, 10, 4), true);
  assert.strictEqual(helpers.hasRequiredInputs('2016-11-01', '2017-05-30', '30', '10', '4'), true);
  assert.strictEqual(helpers.hasRequiredInputs('', '2017-05-30', 30, 10, 4), false);
  assert.strictEqual(helpers.hasRequiredInputs('2017-05-30', '2016-11-01', 30, 10, 4), false);
  assert.strictEqual(helpers.hasRequiredInputs('2016-11-01', '2017-05-30', '', 10, 4), false);
  assert.strictEqual(helpers.hasRequiredInputs('2016-13-40', '2017-05-30', 30, 10, 4), false);
});

check('cloud cover of 0 is allowed (original truthiness bug)', function() {
  assert.strictEqual(helpers.hasRequiredInputs('2016-11-01', '2017-05-30', 0, 10, 4), true);
});

var scriptPath = path.join(__dirname, 'wheat_phenology_mapping.js');
var src = fs.readFileSync(scriptPath, 'utf8');

check('script does not use invalid GEE style key font-weight', function() {
  assert.strictEqual(src.indexOf('font-weight') === -1, true);
  assert.strictEqual(src.indexOf('fontWeight') > -1, true);
});

check('script uses layer.getName() instead of layer.get("name")', function() {
  assert.strictEqual(/layer\.get\s*\(/.test(src), false);
  assert.strictEqual(src.indexOf('getName()') > -1, true);
});

check('script uses harmonized Sentinel-2, not deprecated COPERNICUS/S2', function() {
  assert.strictEqual(src.indexOf("COPERNICUS/S2_HARMONIZED") > -1, true);
  assert.strictEqual(/['"]COPERNICUS\/S2['"]/.test(src), false);
});

check('script lists assets with error handling, not raw getList().map', function() {
  assert.strictEqual(src.indexOf('listAssets') > -1, true);
  assert.strictEqual(/list\.map\s*\(\s*populateProvinceIDs/.test(src), false);
});

check('script enables GCP list buttons so clicks work', function() {
  assert.strictEqual(src.indexOf('disabled: true') === -1, true);
});

check('script clips regression images to the region of interest', function() {
  assert.strictEqual(src.indexOf('.clip(') > -1, true);
});

check('script constructors use camelCase GEE style keys only', function() {
  var styleBlocks = src.match(/style\s*:\s*\{[^}]+\}/g) || [];
  styleBlocks.forEach(function(block) {
    assert.strictEqual(/['"][a-z]+-[a-z]+['"]\s*:/.test(block), false, block);
  });
});

if (failures) {
  console.log('\n' + failures + ' test(s) failed');
  process.exit(1);
}
console.log('\nAll tests passed');
