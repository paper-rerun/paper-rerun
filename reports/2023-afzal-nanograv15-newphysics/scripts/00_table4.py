# Reads Table 4 of arXiv:2306.16219 out of the paper's own LaTeX source into structured claims.
# The ar5iv text dump prints every cell twice and loses the bracket structure, so we parse the
# longtable directly. Output is table4_extraido.json, which 01_claims.py freezes.
import json
import re
from pathlib import Path

TEX = Path(r'E:\Ciencia\noturno\2023-afzal-nanograv15-newphysics\sources\tex\main.tex')
OUT = Path(r'E:\Ciencia\noturno\2023-afzal-nanograv15-newphysics\table4_extraido.json')

# The seven cells after the parameter name, in the order the header declares them
CELLS = ['bayes_np', 'bayes_npsmbhb', 'maxpost_np', 'maxpost_npsmbhb', 'ci_np', 'ci_npsmbhb', 'k_bound']

SECTION = re.compile(r'\\multicolumn\{8\}\{c\}\{(.+?)\}\\\\')
MODEL_TAG = re.compile(r'\\textsc\{\(?([a-z0-9\-]+)\)?\}')
BOLD_NAME = re.compile(r'\\textbf\{(.+?)\}')
PM = re.compile(r'^(-?\d+(?:\.\d+)?)\s*\\pm\s*(-?\d+(?:\.\d+)?)$')
ONE = re.compile(r'^(-?\d+(?:\.\d+)?)$')
INTERVAL = re.compile(r'^\[\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\]$')


def strip_math(cell):
	"""A table cell as plain text: no $, no \\left \\right, no spacing macros"""
	value = re.sub(r'\\\\.*$', '', cell.strip())
	value = value.replace('$', '').replace('\\left', '').replace('\\right', '')
	value = re.sub(r'\\[,;:!]', '', value)
	return re.sub(r'\s+', ' ', value).strip()


def parse_cell(text):
	"""'-0.69 \\pm 0.47' -> value and sd; '-5^*' -> value sitting on the prior edge"""
	at_edge = '^*' in text or '^{*}' in text
	clean = text.replace('^*', '').replace('^{*}', '').strip()
	pm = PM.match(clean)
	if pm:
		return {'value': float(pm.group(1)), 'sd': float(pm.group(2)), 'at_prior_edge': at_edge}
	one = ONE.match(clean)
	if one:
		return {'value': float(one.group(1)), 'at_prior_edge': at_edge}
	interval = INTERVAL.match(clean)
	if interval:
		return {'low': float(interval.group(1)), 'high': float(interval.group(2)), 'at_prior_edge': at_edge}
	return {'raw': text}


text = TEX.read_text(encoding='utf-8', errors='replace')
start = text.index(r'\label{tab:list}')
end = text.index(r'\end{longtable*}', start)
body = text[start:end]

models = []
current = None
skipped = []
for raw_line in body.splitlines():
	line = raw_line.strip()
	if not line or line.startswith('%'):
		continue

	section = SECTION.search(line)
	if section:
		label = section.group(1)
		tag = MODEL_TAG.search(label)
		name = BOLD_NAME.search(label)
		current = {
			'model': tag.group(1) if tag else strip_math(label),
			'title': re.sub(r'\\[a-z]+|[{}]', '', name.group(1)).strip() if name else strip_math(label),
			'parameters': [],
		}
		models.append(current)
		continue

	if current is None or '&' not in line:
		continue

	columns = line.split('&')
	if len(columns) != 8:
		skipped.append(line)
		continue

	entry = {'parameter': strip_math(columns[0])}
	for name, cell in zip(CELLS, columns[1:]):
		raw = strip_math(cell)
		entry[name] = None if raw in ('...', '') else parse_cell(raw)
	current['parameters'].append(entry)

total = sum(len(model['parameters']) for model in models)
OUT.write_text(json.dumps({
	'source': 'arXiv:2306.16219 main.tex, longtable tab:list (Table 4)',
	'cell_order': CELLS,
	'models': models,
}, indent=1), encoding='utf-8')

print(f'{len(models)} models, {total} parameter rows -> {OUT.name}')
for model in models:
	print(' ', model['model'], len(model['parameters']))
if skipped:
	print('rows whose column count was not 8, left out:', len(skipped))
	for line in skipped[:6]:
		print('   ', line[:110])
