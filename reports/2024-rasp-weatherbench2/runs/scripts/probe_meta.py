# Print shape, chunks, dims and compressor of every store the claims need
import json, urllib.request
claims = json.load(open('claims.json'))
stores = set()
for c in claims['claims']:
	stores.add(c['conditions']['forecast_store']); stores.add(c['conditions']['truth_store'])
stores.add('gs://weatherbench2/datasets/era5-hourly-climatology/1990-2019_6h_240x121_equiangular_with_poles_conservative.zarr')
for s in sorted(stores):
	url = s.replace('gs://', 'https://storage.googleapis.com/') + '/.zmetadata'
	meta = json.load(urllib.request.urlopen(url))['metadata']
	print(s)
	for k, v in meta.items():
		if k.endswith('/.zarray'):
			name = k[:-8]
			if name in ('geopotential', 'temperature', 'above_ground', 'time', 'prediction_timedelta', 'level', 'latitude', 'longitude', 'hour', 'dayofyear'):
				dims = meta[name + '/.zattrs'].get('_ARRAY_DIMENSIONS')
				print('  ', name, v['shape'], v['chunks'], dims, v['dtype'], v['compressor'] and v['compressor'].get('cname'), v.get('dimension_separator'), v['fill_value'], v['filters'])
