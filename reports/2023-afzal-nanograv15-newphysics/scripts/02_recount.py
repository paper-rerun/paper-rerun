# Recounts the Bayes estimators of Table 4 from the authors' own chains.
# Usage: 02_recount.py <model> [<model> ...]   e.g. 02_recount.py igw sigw_delta
#
# The deposit is a download, so its pickles are untrusted data. We never call pickle.load
# directly: SafeUnpickler refuses every class except the three numpy needs to rebuild an array,
# so a crafted file cannot import or execute anything else.
import gzip
import io
import json
import pickle
import sys
from pathlib import Path

import numpy as np

ROOT = Path(r'E:\Ciencia\noturno\2023-afzal-nanograv15-newphysics')
CHAINS = ROOT / 'extraido' / 'chains' / 'stochastic'
OUT = ROOT / 'runs' / 'out'

ALLOWED = {
	('numpy.core.multiarray', '_reconstruct'),
	('numpy', 'ndarray'),
	('numpy', 'dtype'),
}


class SafeUnpickler(pickle.Unpickler):
	def find_class(self, module, name):
		if (module, name) in ALLOWED:
			return super().find_class(module, name)
		raise pickle.UnpicklingError(f'refused {module}.{name}')


def load(path):
	with gzip.open(path, 'rb') as handle:
		return SafeUnpickler(io.BytesIO(handle.read())).load()


def summarise(path):
	"""One chain file -> per-parameter sample mean and sample standard deviation"""
	blob = load(path)
	# The file is [priors_dict, samples_array] in the order PTArcade writes them
	priors = next(item for item in blob if isinstance(item, dict))
	samples = next(item for item in blob if isinstance(item, np.ndarray))
	names = list(priors.keys())
	if samples.shape[1] != len(names):
		raise SystemExit(f'{path.name}: {samples.shape[1]} columns against {len(names)} names')

	result = {'file': path.name, 'n_samples': int(samples.shape[0]), 'parameters': {}}
	for index, name in enumerate(names):
		column = samples[:, index]
		result['parameters'][name] = {
			'mean': float(column.mean()),
			'sd': float(column.std(ddof=1)),
			'mean_after_25pct_burn_in': float(column[len(column) // 4:].mean()),
			'sd_after_25pct_burn_in': float(column[len(column) // 4:].std(ddof=1)),
			'p16': float(np.percentile(column, 16)),
			'p84': float(np.percentile(column, 84)),
			'min': float(column.min()),
			'max': float(column.max()),
		}
	# nmodel is a hypermodel index, not a physical parameter. If it moves, the chain mixes two
	# hypotheses and the statistics above pool them, which has to be said out loud.
	if 'nmodel' in result['parameters']:
		column = samples[:, names.index('nmodel')]
		values, counts = np.unique(np.round(column).astype(int), return_counts=True)
		result['nmodel_values'] = {int(v): int(c) for v, c in zip(values, counts)}
	return result


OUT.mkdir(parents=True, exist_ok=True)
for model in sys.argv[1:]:
	for variant, suffix in (('np', ''), ('npsmbhb', '_bhb')):
		path = CHAINS / f'{model}{suffix}.pkl.gz'
		if not path.exists():
			print(f'missing {path.name}')
			continue
		summary = summarise(path)
		summary['model'] = model
		summary['variant'] = variant
		target = OUT / f'{model}_{variant}.json'
		target.write_text(json.dumps(summary, indent=1), encoding='utf-8')
		print(f"{path.name}: {summary['n_samples']} samples, {len(summary['parameters'])} columns -> {target.name}")
		if 'nmodel_values' in summary:
			print('   nmodel:', summary['nmodel_values'])
