# Scores the 112 frozen primary claims against the recounted chains.
# Table 4 names parameters in LaTeX and the chains name them in code, so the mapping is written
# out by hand below and the script stops if any claim fails to map. A silent mapping miss would
# look exactly like a failed claim.
import json
from pathlib import Path

ROOT = Path(r'E:\Ciencia\noturno\2023-afzal-nanograv15-newphysics')
OUT = ROOT / 'runs' / 'out'

# Table 4 writes dw-dr for the domain walls decaying to dark radiation; the deposit calls it dw_ds
MODEL_FILE = {'dw-dr': 'dw_ds'}

PARAMETER = {
	r'\log_{10}T_{\rm rh}/\textrm{GeV}': 'log10_T_rh',
	r'\log_{10}r': 'log10_r',
	'n_t': 'n_t',
	r'\log_{10}A': 'log10_A',
	r'\Delta': 'width',
	r'\log_{10}f_{\rm min}/{\rm Hz}': 'log10_fmin',
	r'\log_{10}f_{\rm max}/{\rm Hz}': 'log10_fmax',
	r'\log_{10}T_{\rm *}/\textrm{GeV}': 'log10_T_star',
	r'\log_{10}\alpha_*': 'log10_alpha',
	r'\log_{10}H_*R_*': 'log10_H_R',
	'a': 'a',
	'b': 'b',
	'c': 'c',
	r'\log_{10}G\mu': 'log10_Gmu',
	r'\sqrt{\kappa}': 'sqrt_kappa',
	r'\log_{10}P': 'log10_P',
	r'\log_{10} \Delta N_{\rm eff}': 'log10_N_eff',
	r'\log_{10}A_{\scriptscriptstyle\rm BHB}': 'gw_bhb_np_0',
	r'\gamma_{\scriptscriptstyle\rm BHB}': 'gw_bhb_np_1',
}

# The peak frequency is spelled differently in the two sigw chains
PER_MODEL = {
	('sigw-delta', r'\log_{10}f_*/{\rm Hz}'): 'log10_f_peak',
	('sigw-gauss', r'\log_{10}f_*/{\rm Hz}'): 'log10_fpeak',
}

TOLERANCE = 0.005   # Table 4 prints two decimals, so this is "rounds to the printed value"
NEAR_MISS = 0.05

claims = json.loads((ROOT / 'claims.json').read_text(encoding='utf-8'))
cache = {}


def chain(model, variant):
	key = (model, variant)
	if key not in cache:
		name = MODEL_FILE.get(model, model.replace('-', '_'))
		cache[key] = json.loads((OUT / f'{name}_{variant}.json').read_text(encoding='utf-8'))
	return cache[key]


rows = []
unmapped = []
for claim in claims['primary']:
	column = PER_MODEL.get((claim['model'], claim['parameter'])) or PARAMETER.get(claim['parameter'])
	if column is None:
		unmapped.append((claim['model'], claim['parameter']))
		continue

	measured = chain(claim['model'], claim['variant'])['parameters'].get(column)
	if measured is None:
		unmapped.append((claim['model'], claim['parameter'] + f' -> {column} absent from the chain'))
		continue

	d_mean = measured['mean'] - claim['published_mean']
	d_sd = measured['sd'] - claim['published_sd']
	worst = max(abs(d_mean), abs(d_sd))
	rows.append({
		'id': claim['id'],
		'model': claim['model'],
		'variant': claim['variant'],
		'column': column,
		'published_mean': claim['published_mean'],
		'published_sd': claim['published_sd'],
		'our_mean': round(measured['mean'], 4),
		'our_sd': round(measured['sd'], 4),
		'd_mean': round(d_mean, 4),
		'd_sd': round(d_sd, 4),
		'our_mean_after_burn_in': round(measured['mean_after_25pct_burn_in'], 4),
		'verdict': 'reproduced' if worst < TOLERANCE else ('near miss' if worst < NEAR_MISS else 'not reproduced'),
	})

if unmapped:
	raise SystemExit(f'{len(unmapped)} claims did not map: {unmapped[:8]}')

counts = {}
for row in rows:
	counts[row['verdict']] = counts.get(row['verdict'], 0) + 1

(OUT / 'score_primary.json').write_text(json.dumps({
	'tolerance': TOLERANCE,
	'near_miss_band': NEAR_MISS,
	'counts': counts,
	'rows': rows,
}, indent=1), encoding='utf-8')

print(f'{len(rows)} primary claims scored')
for verdict, count in sorted(counts.items()):
	print(f'  {verdict}: {count}')
for row in rows:
	if row['verdict'] != 'reproduced':
		print(f"  {row['id']}  ours {row['our_mean']} +- {row['our_sd']}  paper {row['published_mean']} +- {row['published_sd']}")
