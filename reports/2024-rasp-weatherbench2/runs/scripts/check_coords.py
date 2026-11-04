# Check coordinate decoding of every store against xarray's own decoding
import json, sys
sys.path.insert(0, 'runs/scripts')
import wb2_rmse as w
import xarray as xr
claims = json.load(open('claims.json'))
stores = sorted(set(c['conditions'][k] for c in claims['claims'] for k in ('forecast_store', 'truth_store')))
for s in stores + [w.CLIM_STORE]:
	meta = w.load_meta(s)
	print(s.split('/')[-2], {k: v for k, v in meta.items() if k in ('time/.zattrs', 'prediction_timedelta/.zattrs', 'dayofyear/.zattrs', 'hour/.zattrs')})
	ds = xr.open_zarr(s, storage_options={'token': 'anon'})
	for name in ('time', 'prediction_timedelta', 'level', 'latitude', 'hour', 'dayofyear'):
		if name + '/.zarray' in meta:
			mine = w.read_coord(s, meta, name)
			theirs = ds[name].values
			import numpy as np
			same = np.array_equal(np.asarray(mine, dtype=theirs.dtype) if theirs.dtype.kind in 'Mm' else np.asarray(mine), theirs)
			print('   ', name, len(theirs), same, theirs[:2], theirs[-1])
