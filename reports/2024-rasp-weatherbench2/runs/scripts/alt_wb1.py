# Alternative reading (not verdict): WB1-style RMSE, sqrt per init before the time mean
import json, glob
import numpy as np
for path in sorted(glob.glob('runs/out/*.jsonl')):
	records = [json.loads(line) for line in open(path)]
	row = []
	for hours in (24, 72, 120, 168, 240):
		per_init = {r['init']: r['mse_v1'] for r in records if r.get('lead_hours') == hours}
		row.append('%.4f' % np.mean(np.sqrt(list(per_init.values()))))
	print(path.split('/')[-1].replace('.jsonl', ''), ' '.join(row))
