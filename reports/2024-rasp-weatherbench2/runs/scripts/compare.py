# Compare our RMSE (runs/out/*.summary.json) with every claim in claims.json, using the pre-registered tolerance
# Writes runs/results.csv and prints a markdown table
import csv
import json
import os

ROOT = '/mnt/e/Ciencia/noturno/2024-rasp-weatherbench2'
TASK_BY_STORE = {
	('hres/', 'hres_t0'): 'hres', ('/pangu/', 'era5/'): 'pangu', ('/graphcast/', 'era5/'): 'graphcast',
	('pangu_hres_init', 'hres_t0'): 'panguoper', ('graphcast_hres_init', 'hres_t0'): 'graphcastoper', ('neuralgcm', 'era5/'): 'neuralgcm',
}


def task_name(conditions):
	for (forecast_key, truth_key), name in TASK_BY_STORE.items():
		if forecast_key in conditions['forecast_store'] and truth_key in conditions['truth_store']:
			suffix = 'z500' if conditions['store_variable'] == 'geopotential' else 't850'
			return name + '_' + suffix
	raise KeyError(conditions['forecast_store'])


def display_consistent(value, paper, decimals):
	# Accept interval [paper - half unit, paper + one unit): value rounds or truncates to the printed number
	unit = 10 ** -decimals
	return paper - unit / 2 <= value < paper + unit


def main():
	claims = json.load(open(os.path.join(ROOT, 'claims.json')))
	rows = []
	for claim in claims['claims']:
		conditions = claim['conditions']
		decimals = len(claim['paper_value_as_printed'].split('.')[1]) if '.' in claim['paper_value_as_printed'] else 0
		path = os.path.join(ROOT, 'runs/out', task_name(conditions) + '.summary.json')
		row = {'id': claim['id'], 'tier': claim['tier'], 'paper': claim['paper_value'], 'authors_2026': claim['authors_published_value_2026']}
		if not os.path.exists(path):
			row['status'] = 'not computed'
			rows.append(row)
			continue
		summary = json.load(open(path))
		lead = summary['leads'][str(conditions['lead_time_hours'])]
		v1, v2 = lead['rmse_v1'], lead['rmse_v2']
		match_v1 = display_consistent(v1, claim['paper_value'], decimals)
		match_v2 = display_consistent(v2, claim['paper_value'], decimals)
		row.update({'n_inits': lead['n_inits'], 'v1': v1, 'v2': v2, 'match_v1': match_v1, 'match_v2': match_v2,
			'diff_v1_pct': 100 * (v1 - claim['paper_value']) / claim['paper_value'],
			'diff_v2_pct': 100 * (v2 - claim['paper_value']) / claim['paper_value'],
			'v1_vs_authors2026_pct': 100 * (v1 - claim['authors_published_value_2026']) / claim['authors_published_value_2026'],
			'any_nan': lead['any_nan'], 'any_chunk_missing': lead['any_chunk_missing'], 'all_md5_checked': lead['all_md5_checked'],
			'status': 'reproduced (V1)' if match_v1 else ('reproduced (V2 only)' if match_v2 else 'not reproduced')})
		rows.append(row)
	fields = ['id', 'tier', 'paper', 'v1', 'v2', 'diff_v1_pct', 'diff_v2_pct', 'match_v1', 'match_v2', 'authors_2026', 'v1_vs_authors2026_pct',
		'n_inits', 'any_nan', 'any_chunk_missing', 'all_md5_checked', 'status']
	with open(os.path.join(ROOT, 'runs/results.csv'), 'w', newline='') as out:
		writer = csv.DictWriter(out, fields)
		writer.writeheader()
		writer.writerows(rows)
	print('| Claim | Tier | Paper | Ours V1 (no mask) | Ours V2 (mask) | Diff V1 | Diff V2 | Authors 2026 | V1 vs 2026 | n | Status |')
	print('|---|---|---|---|---|---|---|---|---|---|---|')
	for r in rows:
		if 'v1' not in r:
			print('| %s | %s | %s | | | | | %s | | | %s |' % (r['id'], r['tier'], r['paper'], r['authors_2026'], r['status']))
			continue
		print('| %s | %s | %s | %.4f | %.4f | %+.2f%% | %+.2f%% | %s | %+.3f%% | %d | %s |' % (r['id'], r['tier'], r['paper'], r['v1'], r['v2'],
			r['diff_v1_pct'], r['diff_v2_pct'], r['authors_2026'], r['v1_vs_authors2026_pct'], r['n_inits'], r['status']))
	for tier in ('primary', 'secondary', 'optional'):
		group = [r for r in rows if r['tier'] == tier]
		print('%s: %d claims, V1 match %d, V1-or-V2 match %d, not computed %d' % (tier, len(group), sum(1 for r in group if r.get('match_v1')),
			sum(1 for r in group if r.get('match_v1') or r.get('match_v2')), sum(1 for r in group if 'v1' not in r)))


if __name__ == '__main__':
	main()
