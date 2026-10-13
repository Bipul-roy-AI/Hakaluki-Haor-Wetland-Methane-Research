// HAKALUKI HAOR — Google Earth Engine JavaScript Code Editor quicklook
// Caution: This is a screening-grade visualization, not a validated flood map.
// The rectangle below represents a government-reported approximate geographic
// envelope, NOT an official wetland boundary. Replace with a verified EE asset.
var VERIFIED_ASSET_ID = ''; // e.g. 'projects/YOUR_PROJECT/assets/hakaluki_verified'
var envelope = ee.Geometry.Rectangle([92+1/60, 24+35/60, 92+9/60, 24+44/60]);
var roi = VERIFIED_ASSET_ID ? ee.FeatureCollection(VERIFIED_ASSET_ID).geometry() : envelope;
Map.centerObject(roi, 11);
Map.addLayer(roi,{color:'FF8800'},VERIFIED_ASSET_ID?'User supplied boundary':'APPROXIMATE study envelope – NOT wetland boundary');

// Hold pass consistent; full Jupyter pipeline chooses the modal relative orbit.
var s1 = ee.ImageCollection('COPERNICUS/S1_GRD')
  .filterBounds(roi).filter(ee.Filter.eq('instrumentMode','IW'))
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation','VV'))
  .filter(ee.Filter.eq('orbitProperties_pass','DESCENDING')).select('VV');

function lowVV(start,end) {
  var subset=s1.filterDate(start,end);
  print('S1 scenes '+start,subset.size());
  // Fixed -17 dB is a subjective demonstration threshold, NOT calibrated.
  return subset.median().focal_median(30,'circle','meters').lt(-17).rename('openWaterScreen');
}
var march = lowVV('2022-03-01','2022-04-01');
var june = lowVV('2022-06-01','2022-07-01');
Map.addLayer(march.selfMask(),{palette:['55b4ef']},'March 2022 low-VV screen');
Map.addLayer(june.selfMask(),{palette:['073cca']},'June 2022 low-VV screen');
Map.addLayer(june.and(march.not()).selfMask(),{palette:['ed3e51']},
             'Additional low-VV water March–June (seasonal difference, not attributed)');

var methane = ee.ImageCollection('COPERNICUS/S5P/OFFL/L3_CH4')
  .filterDate('2022-01-01','2023-01-01')
  .filterBounds(roi.buffer(30000))
  .select('CH4_column_volume_mixing_ratio_dry_air_bias_corrected');
print('S5P L3 tiled scene count (NOT independent methane footprints)',methane.size());
Map.addLayer(methane.mean(),{min:1800,max:1960,palette:['1a4699','7bc9c7','f0e45d','e35147']},
             '2022 regional atmosphere XCH4 (ppb) — coarse retrieval support',false);

// For export from Code Editor (replace boundary first):
// Export.image.toDrive({image:june.toByte(),description:'Hakaluki_2022_June_SAR_screen',
//   folder:'Hakaluki_Haor_Study',region:roi,scale:30,maxPixels:1e10});
