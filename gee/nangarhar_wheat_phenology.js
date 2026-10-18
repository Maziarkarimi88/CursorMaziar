/**
 * Nangarhar irrigated-wheat phenology (GEE Code Editor)
 *
 * Method follows Tiwari et al. (2020), Front. Environ. Sci. 8:77:
 * https://www.frontiersin.org/articles/10.3389/fenvs.2020.00077/full
 *
 * Sentinel-2 L1C, cloud < 30%, QA60 mask, seasonal median NDVI
 * at sowing / peak / harvest, sampled on wheat GCPs.
 *
 * How to run:
 * 1. Open https://code.earthengine.google.com/ and sign in.
 * 2. Select Cloud project ee-maziarkarimi3 (profile menu > Change Cloud Project).
 * 3. Paste this file and click Run.
 *
 * Assets (your GEE project):
 *   AOI     projects/ee-maziarkarimi3/assets/Wheat_Mapping/Admin/Nangarhar
 *   Ag IR   projects/ee-maziarkarimi3/assets/Wheat_Mapping/IR_RF/Nangarhar_Ag_IR
 *   GCP     projects/ee-maziarkarimi3/assets/Wheat_Mapping/GCP/Nangarhar_IR_GCP
 *
 * Nangarhar irrigated winter wheat (MAIL / eastern AEZ):
 *   Sowing  mid-Nov to mid-Dec
 *   Peak    Feb to Mar
 *   Harvest May to June
 */

var ASSETS = {
  AOI: 'projects/ee-maziarkarimi3/assets/Wheat_Mapping/Admin/Nangarhar',
  AGRI: 'projects/ee-maziarkarimi3/assets/Wheat_Mapping/IR_RF/Nangarhar_Ag_IR',
  GCP: 'projects/ee-maziarkarimi3/assets/Wheat_Mapping/GCP/Nangarhar_IR_GCP'
};

var CONFIG = {
  S2: 'COPERNICUS/S2_HARMONIZED',
  CLOUD: 30,
  SCALE: 10,
  START: '2016-11-01',
  END: '2017-06-30',
  MAX_GCP_CHART: 40
};

// Season windows for one winter-wheat cycle. Change START/END year above,
// then these relative months stay valid if you keep the same calendar.
var SEASONS = [
  {id: 'sowing', label: 'Sowing', start: '2016-11-15', end: '2016-12-31', color: '#c27a2b'},
  {id: 'peak', label: 'Peak', start: '2017-02-01', end: '2017-03-31', color: '#2e7d32'},
  {id: 'harvest', label: 'Harvest', start: '2017-05-01', end: '2017-06-15', color: '#ef6c00'}
];

var aoi = ee.FeatureCollection(ASSETS.AOI);
var agri = ee.FeatureCollection(ASSETS.AGRI);
var gcp = ee.FeatureCollection(ASSETS.GCP);

function maskS2clouds(image) {
  var qa = image.select('QA60');
  var mask = qa.bitwiseAnd(1 << 10).eq(0).and(qa.bitwiseAnd(1 << 11).eq(0));
  return image.updateMask(mask).copyProperties(image, ['system:time_start']);
}

function addIndices(image) {
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  var ndsi = image.normalizedDifference(['B11', 'B8']).rename('NDSI');
  return image.addBands(ndvi).addBands(ndsi);
}

function s2Collection(start, end, region) {
  return ee.ImageCollection(CONFIG.S2)
    .filterBounds(region)
    .filterDate(start, end)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', CONFIG.CLOUD))
    .map(maskS2clouds)
    .map(addIndices)
    .map(function(image) {
      return image.clip(region);
    });
}

function seasonalMedian(start, end, region) {
  return s2Collection(start, end, region).select(['NDVI', 'NDSI']).median();
}

function sampleSeason(image, points, prefix) {
  return image.reduceRegions({
    collection: points,
    reducer: ee.Reducer.mean(),
    scale: CONFIG.SCALE
  }).map(function(f) {
    return f.set(prefix + '_NDVI', f.get('NDVI'))
      .set(prefix + '_NDSI', f.get('NDSI'));
  });
}

function seasonStats(sampled, prefix) {
  var valid = sampled.filter(ee.Filter.notNull([prefix + '_NDVI']));
  return ee.Dictionary({
    season: prefix,
    count: valid.size(),
    mean: valid.aggregate_mean(prefix + '_NDVI'),
    min: valid.aggregate_min(prefix + '_NDVI'),
    max: valid.aggregate_max(prefix + '_NDVI')
  });
}

function makeTimeSeriesChart(col, region, title) {
  return ui.Chart.image.series({
    imageCollection: col.select('NDVI'),
    region: region,
    reducer: ee.Reducer.mean(),
    scale: CONFIG.SCALE,
    xProperty: 'system:time_start'
  }).setChartType('ScatterChart').setOptions({
    title: title,
    vAxis: {title: 'NDVI', viewWindow: {min: 0, max: 1}},
    hAxis: {title: 'Date'},
    lineWidth: 1,
    pointSize: 3,
    legend: {position: 'none'},
    colors: ['#1b5e20']
  });
}

function makeSeasonBarChart(rows) {
  return ui.Chart.array.values({
    array: rows.map(function(r) { return r.mean; }),
    axis: 0,
    xLabels: rows.map(function(r) { return r.label; })
  }).setChartType('ColumnChart').setOptions({
    title: 'Mean wheat-GCP NDVI at three seasons',
    vAxis: {title: 'NDVI', viewWindow: {min: 0, max: 1}},
    hAxis: {title: 'Phenological stage'},
    legend: {position: 'none'},
    colors: ['#2e7d32']
  });
}

var chartPanel = ui.Panel({
  layout: ui.Panel.Layout.flow('vertical'),
  style: {width: '380px', padding: '8px'}
});
chartPanel.add(ui.Label({
  value: 'Nangarhar wheat NDVI phenology',
  style: {fontWeight: 'bold', fontSize: '16px'}
}));
chartPanel.add(ui.Label(
  'Tiwari et al. 2020: seasonal median NDVI at sowing, peak and harvest, sampled on wheat GCPs.'
));
ui.root.insert(0, chartPanel);

Map.setOptions('HYBRID');
Map.centerObject(aoi, 9);
Map.addLayer(aoi, {color: 'white'}, 'Nangarhar AOI', true);
Map.addLayer(agri, {color: 'ffd468'}, 'Irrigated agriculture', false);
Map.addLayer(gcp, {color: 'red'}, 'Wheat GCP');

aoi.size().evaluate(function(nAoi, errAoi) {
  agri.size().evaluate(function(nAgri, errAgri) {
    gcp.size().evaluate(function(nGcp, errGcp) {
      if (errAoi || errAgri || errGcp || !nAoi || !nAgri || !nGcp) {
        print('Asset load error. Check that these tables exist in your project:');
        print(ASSETS);
        print(errAoi || errAgri || errGcp || 'One collection is empty.');
        chartPanel.add(ui.Label({
          value: 'Could not load AOI, agriculture mask, or GCP assets.',
          style: {color: 'red'}
        }));
        return;
      }
      runPhenology(nGcp);
    });
  });
});

function runPhenology(nGcp) {
  var region = agri.geometry();
  var points = gcp.limit(400).map(function(f) {
    return f.set('id', f.id());
  });
  var fullCol = s2Collection(CONFIG.START, CONFIG.END, region);

  fullCol.size().evaluate(function(nImg, errImg) {
    if (errImg || !nImg) {
      print('No Sentinel-2 images for', CONFIG.START, CONFIG.END);
      chartPanel.add(ui.Label({
        value: 'No Sentinel-2 images for these dates / cloud filter.',
        style: {color: 'red'}
      }));
      return;
    }
    print('Sentinel-2 images used:', nImg);
    print('Wheat GCPs:', nGcp);

    var tsChart = makeTimeSeriesChart(
      fullCol,
      points.geometry(),
      'NDVI time series at Nangarhar wheat GCPs'
    );
    chartPanel.add(tsChart);

    var agriChart = makeTimeSeriesChart(
      fullCol,
      region,
      'NDVI time series over irrigated agricultural land'
    );
    chartPanel.add(agriChart);

    var sowingImg = seasonalMedian(SEASONS[0].start, SEASONS[0].end, region);
    var peakImg = seasonalMedian(SEASONS[1].start, SEASONS[1].end, region);
    var harvestImg = seasonalMedian(SEASONS[2].start, SEASONS[2].end, region);

    Map.addLayer(sowingImg.select('NDVI'), {min: 0, max: 0.8, palette: ['brown', 'yellow', 'green']}, 'NDVI sowing', false);
    Map.addLayer(peakImg.select('NDVI'), {min: 0, max: 0.8, palette: ['brown', 'yellow', 'green']}, 'NDVI peak', true);
    Map.addLayer(harvestImg.select('NDVI'), {min: 0, max: 0.8, palette: ['brown', 'yellow', 'green']}, 'NDVI harvest', false);

    var sowingPts = sampleSeason(sowingImg, points, 'sowing');
    var peakPts = sampleSeason(peakImg, points, 'peak');
    var harvestPts = sampleSeason(harvestImg, points, 'harvest');

    var table = points
      .map(function(f) { return f.select(['id']); });
    table = joinSeasonSimple(table, sowingPts, 'sowing');
    table = joinSeasonSimple(table, peakPts, 'peak');
    table = joinSeasonSimple(table, harvestPts, 'harvest');

    var summary = ee.FeatureCollection([
      ee.Feature(null, seasonStats(sowingPts, 'sowing')),
      ee.Feature(null, seasonStats(peakPts, 'peak')),
      ee.Feature(null, seasonStats(harvestPts, 'harvest'))
    ]);

    print('Season windows (Nangarhar irrigated wheat)', SEASONS);
    print('Paper-style GCP NDVI summary (use min/max as provincial thresholds)', summary);
    print('Per-GCP NDVI at sowing, peak and harvest', table);

    summary.evaluate(function(info) {
      if (!info || !info.features) return;
      var rows = info.features.map(function(feat) {
        var p = feat.properties || {};
        return {
          label: p.season,
          mean: p.mean == null ? 0 : p.mean,
          min: p.min,
          max: p.max,
          count: p.count
        };
      });
      chartPanel.add(makeSeasonBarChart(rows));
      rows.forEach(function(r) {
        var line = r.label +
          '  mean=' + (r.mean == null ? 'NA' : Number(r.mean).toFixed(3)) +
          '  min=' + (r.min == null ? 'NA' : Number(r.min).toFixed(3)) +
          '  max=' + (r.max == null ? 'NA' : Number(r.max).toFixed(3)) +
          '  n=' + r.count;
        print(line);
        chartPanel.add(ui.Label({
          value: line,
          style: {fontWeight: 'bold'}
        }));
      });
      chartPanel.add(ui.Label(
        'Typical wheat pattern: low NDVI at sowing, highest at peak, decline at harvest.'
      ));
    });

    Export.table.toDrive({
      collection: table,
      description: 'Nangarhar_wheat_GCP_NDVI_sowing_peak_harvest',
      fileFormat: 'CSV'
    });
  });
}

function joinSeasonSimple(base, sampled, prefix) {
  var dict = ee.Dictionary.fromLists(
    sampled.aggregate_array('system:index'),
    sampled.aggregate_array(prefix + '_NDVI')
  );
  var dictSi = ee.Dictionary.fromLists(
    sampled.aggregate_array('system:index'),
    sampled.aggregate_array(prefix + '_NDSI')
  );
  return base.map(function(f) {
    var key = f.get('system:index');
    return f.set(prefix + '_NDVI', dict.get(key))
      .set(prefix + '_NDSI', dictSi.get(key));
  });
}
