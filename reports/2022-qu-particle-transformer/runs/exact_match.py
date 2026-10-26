"""For each Rej claim: the range of QCD counts k consistent with the paper integer, and whether our k is in it"""
import json
import math

claims = {c['id']: c for c in json.load(open('../claims.json'))['claims']}
for run in ['ParT_fp32', 'ParT_amp', 'PN_fp32']:
	d = json.load(open(f'full_{run}/score.json'))
	n_exact = 0
	print('==', run, 'accuracy %.8f (3 dp: %.3f)' % (d['accuracy'], d['accuracy']), 'auc %.8f (4 dp: %.4f)' % (d['auc'], d['auc']))
	for cid, v in d['rej'].items():
		paper = claims[cid]['paper_value']
		k_lo = math.floor(2e6 / (paper + 0.5)) + 1
		k_hi = math.floor(2e6 / (paper - 0.5))
		k = int(v['main_f64_ratio']['main_first_point_tpr_ge_X']['k_qcd'])
		inside = k_lo <= k <= k_hi
		n_exact += inside
		print(f'{cid:24s} paper {paper:6d}  k range [{k_lo}, {k_hi}]  ours k {k}  rej {2e6 / k:.1f}  exact {inside}  dk {0 if inside else (k - k_hi if k > k_hi else k - k_lo)}')
	print('exact matches', n_exact, 'of', len(d['rej']))
