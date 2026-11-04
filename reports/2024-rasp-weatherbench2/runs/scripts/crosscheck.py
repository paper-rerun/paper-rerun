# Compare the official evaluate.py output (January 2020 inits) with our per-init MSE restricted to the same inits
import json
import sys

import numpy as np
import xarray as xr

ROOT = '/mnt/e/Ciencia/noturno/2024-rasp-weatherbench2/'
CASES = [
	('runs/official/hres_vs_analysis_2020jan_z500_deterministic.nc', 'runs/out/hres_z500.jsonl', 'geopotential', 500),
	('runs/official/pangu_vs_era_2020jan_t850_deterministic.nc', 'runs/out/pangu_t850.jsonl', 'temperature', 850),
	# Added in the revision: the two GraphCast stores
	('runs/official/graphcast_vs_era_2020jan_z500_deterministic.nc', 'runs/out/graphcast_z500.jsonl', 'geopotential', 500),
	('runs/official/graphcastoper_vs_analysis_2020jan_z500_deterministic.nc', 'runs/out/graphcastoper_z500.jsonl', 'geopotential', 500),
]
for official_path, ours_path, variable, level in CASES:
	try:
		official = xr.open_dataset(ROOT + official_path)
		records = [json.loads(line) for line in open(ROOT + ours_path)]
	except FileNotFoundError as error:
		print('missing', error)
		continue
	print(official_path, dict(official.sizes))
	for hours in (24, 72, 120, 168, 240):
		rows = {r['init']: r for r in records if r.get('lead_hours') == hours and r['init'].startswith('2020-01')}
		if len(rows) != 62:
			print('  lead %d: only %d January inits in our file yet' % (hours, len(rows)))
			continue
		ours = float(np.sqrt(np.mean([r['mse_v1'] for r in rows.values()])))
		selection = dict(metric='mse', region='global', lead_time=np.timedelta64(hours, 'h'))
		if 'level' in official[variable].dims:
			selection['level'] = level
		theirs = float(np.sqrt(official[variable].sel(**selection).values))
		print('  lead %3d h  official %.6f  ours %.6f  rel diff %.2e' % (hours, theirs, ours, (ours - theirs) / theirs))
