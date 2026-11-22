# Builds claims.json from the extracted Table 4 and freezes it. Run before any chain is opened.
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(r'E:\Ciencia\noturno\2023-afzal-nanograv15-newphysics')
TABLE = ROOT / 'table4_extraido.json'
CLAIMS = ROOT / 'claims.json'

table = json.loads(TABLE.read_text(encoding='utf-8'))

primary = []
secondary = []
for model in table['models']:
	for row in model['parameters']:
		for variant in ('np', 'npsmbhb'):
			bayes = row[f'bayes_{variant}']
			if bayes:
				primary.append({
					'id': f"{model['model']}|{row['parameter']}|{variant}|bayes",
					'model': model['model'],
					'parameter': row['parameter'],
					'variant': variant,
					'published_mean': bayes['value'],
					'published_sd': bayes['sd'],
				})
			interval = row[f'ci_{variant}']
			if interval:
				secondary.append({
					'id': f"{model['model']}|{row['parameter']}|{variant}|ci68",
					'model': model['model'],
					'parameter': row['parameter'],
					'variant': variant,
					'published_low': interval['low'],
					'published_high': interval['high'],
					'at_prior_edge': interval['at_prior_edge'],
				})
			peak = row[f'maxpost_{variant}']
			if peak:
				secondary.append({
					'id': f"{model['model']}|{row['parameter']}|{variant}|maxpost",
					'model': model['model'],
					'parameter': row['parameter'],
					'variant': variant,
					'published_value': peak['value'],
					'at_prior_edge': peak['at_prior_edge'],
				})

claims = {
	'paper': 'Afzal et al., The NANOGrav 15 yr Data Set: Search for Signals from New Physics, ApJL 951, L11 (2023), arXiv:2306.16219',
	'target': 'Table 4 (longtable tab:list): Bayes estimators, maximum posterior values and 68% credible intervals for every new-physics model, in both the NP and NP+SMBHB analyses',
	'data': {
		'chains': 'https://zenodo.org/records/8083620/files/chains.gz (concept DOI 10.5281/zenodo.8010909)',
		'bytes': 22440020155,
		'md5': '464a0c2f2645aec4bd72cbd9f1bfb4cf',
		'sha256': 'c9a6db2afdda38e0fc8f48f066fc56d1978505600f026f610ba9f5383a8a9d78',
		'licence': 'CC-BY-4.0, no login and no click-through',
	},

	'frozen_rule': {
		'estimator': (
			'The paper defines it, which is why this target was chosen. Appendix A: the Bayes estimator is the '
			'expectation value of the 1D marginal and the standard deviation is the square root of its variance, '
			'computed in practice as the sample mean and sample standard deviation of the MCMC chain. We compute '
			'exactly that, unweighted, over the samples as deposited.'
		),
		'chain_handling': (
			'Primary reading uses each chain as deposited, with nothing discarded and no thinning, because the '
			'deposit is described as the chains that were analysed. If the deposit turns out to carry an explicit '
			'burn-in column or a documented convention, we follow it and say so.'
		),
		'tolerance': (
			'Table 4 prints two decimals. A claim reproduces when our value rounds to the printed one, that is '
			'when the absolute difference is below 0.005. Differences between 0.005 and 0.05 are reported as near '
			'misses rather than failures, since MCMC sampling noise of a mean is real.'
		),
	},

	'secondary_readings_declared_in_advance': {
		'burn_in': 'the same statistics after discarding the first 25% of each chain, to show whether the printed values depend on that choice',
		'maximum_posterior': (
			'the mode of the 1D marginal needs a density estimate, which the paper does not specify. We use a '
			'Gaussian KDE with Silverman bandwidth on the same samples, and report the bandwidth sensitivity '
			'rather than scoring the cell as a failure.'
		),
		'ci68': 'the equal-tailed 16th-84th percentile interval, and the highest-density interval, both reported; the paper does not say which it printed',
	},

	'out_of_scope': {
		'bayes_factors': (
			'The Bayes factors between models, including the 10 to 100 range favouring several cosmological models '
			'over SMBHBs, come from the evidence and not from the marginals. Recovering them means rerunning the '
			'inference, which is not what a chain recount can do.'
		),
		'k_bound': 'the K ratio of Eq. (10) is a likelihood ratio, not a property of the marginal',
		'caveat': 'recounting from the authors own chains checks the summarising step, not the inference behind it',
	},

	'primary': primary,
	'secondary': secondary,
}

CLAIMS.write_text(json.dumps(claims, indent=1, ensure_ascii=False), encoding='utf-8')
digest = hashlib.sha256(CLAIMS.read_bytes()).hexdigest()
now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
(ROOT / 'claims.sha256').write_text(f'{digest}  claims.json\n', encoding='utf-8')
(ROOT / 'claims.frozen_at.txt').write_text(f'{now}\n', encoding='utf-8')
print(f'{len(primary)} primary and {len(secondary)} secondary claims')
print(f'sha256 {digest}')
print(f'frozen at {now}')
