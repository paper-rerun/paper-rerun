# Two things the scoring turned up, measured properly.
# 1. The gamma_BHB column of sigw_gauss_bhb runs far past where every other chain stops.
# 2. In three of the four log10_alpha cells, the printed Bayes estimator is our value negated.
import gzip
import io
import json
import pickle
from pathlib import Path

import numpy as np

ROOT = Path(r'E:\Ciencia\noturno\2023-afzal-nanograv15-newphysics')
CHAINS = ROOT / 'extraido' / 'chains' / 'stochastic'
OUT = ROOT / 'runs' / 'out'

ALLOWED = {('numpy.core.multiarray', '_reconstruct'), ('numpy', 'ndarray'), ('numpy', 'dtype')}


class SafeUnpickler(pickle.Unpickler):
	def find_class(self, module, name):
		if (module, name) in ALLOWED:
			return super().find_class(module, name)
		raise pickle.UnpicklingError(f'refused {module}.{name}')


def column(path, wanted):
	with gzip.open(path, 'rb') as handle:
		blob = SafeUnpickler(io.BytesIO(handle.read())).load()
	priors = next(item for item in blob if isinstance(item, dict))
	samples = next(item for item in blob if isinstance(item, np.ndarray))
	names = list(priors.keys())
	return samples[:, names.index(wanted)], priors.get(wanted)


report = {}

# 1. How far outside does that gamma_BHB column go, and how many samples are out there
values, prior = column(CHAINS / 'sigw_gauss_bhb.pkl.gz', 'gw_bhb_np_1')
reference, ref_prior = column(CHAINS / 'sigw_delta_bhb.pkl.gz', 'gw_bhb_np_1')
ceiling = float(reference.max())
outside = values > ceiling
report['gamma_bhb_tail'] = {
	'prior_in_sigw_gauss_file': prior,
	'prior_in_sigw_delta_file': ref_prior,
	'sigw_delta_max': ceiling,
	'sigw_gauss_max': float(values.max()),
	'samples_above_sigw_delta_max': int(outside.sum()),
	'fraction_above': float(outside.mean()),
	'mean_all': float(values.mean()),
	'sd_all': float(values.std(ddof=1)),
	'mean_without_them': float(values[~outside].mean()),
	'sd_without_them': float(values[~outside].std(ddof=1)),
	'published_mean': 4.65,
	'published_sd': 0.34,
}

# 2. Is the printed value exactly our value with the sign turned round
alpha_cells = [
	('pt_bubble.pkl.gz', 'pt-bubble', 'np', -0.26, 0.47),
	('pt_bubble_bhb.pkl.gz', 'pt-bubble', 'npsmbhb', -0.23, 0.52),
	('pt_sound.pkl.gz', 'pt-sound', 'np', -0.22, 0.44),
	('pt_sound_bhb.pkl.gz', 'pt-sound', 'npsmbhb', 0.14, 0.56),
]
report['log10_alpha'] = []
for filename, model, variant, printed_mean, printed_sd in alpha_cells:
	values, prior = column(CHAINS / filename, 'log10_alpha')
	mean = float(values.mean())
	report['log10_alpha'].append({
		'model': model,
		'variant': variant,
		'prior': prior,
		'our_mean': round(mean, 4),
		'our_sd': round(float(values.std(ddof=1)), 4),
		'printed_mean': printed_mean,
		'printed_sd': printed_sd,
		'distance_as_printed': round(abs(mean - printed_mean), 4),
		'distance_if_sign_flipped': round(abs(mean + printed_mean), 4),
		'fraction_of_samples_below_zero': round(float((values < 0).mean()), 4),
	})

(OUT / 'anomalias.json').write_text(json.dumps(report, indent=1), encoding='utf-8')
print(json.dumps(report, indent=1))
