# Selective-chunk RMSE for the WB2 Fig. 1 claims (definitions fixed in claims.json)
# Usage: wb2_rmse.py <forecast_store> <truth_store> <variable> <level> <out_prefix>
# Reads only the zarr chunks holding the target leads, verifies each GET (size + md5 from x-goog-hash),
# keeps nothing of the forecast on disk. Per-init MSE goes to <out_prefix>.jsonl so a restart skips done work.
import base64
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import numcodecs
import numpy as np
import pandas as pd

BASE = 'https://storage.googleapis.com/'
# WB2_DATA_DIR and WB2_MAX_INITS exist only for the smoke test, so its partial truth cache never mixes with the full run
DATA_DIR = os.environ.get('WB2_DATA_DIR', '/mnt/e/Ciencia/noturno/2024-rasp-weatherbench2/data')
CLIM_STORE = 'gs://weatherbench2/datasets/era5-hourly-climatology/1990-2019_6h_240x121_equiangular_with_poles_conservative.zarr'
TARGET_LEADS_HOURS = [24, 72, 120, 168, 240]
INIT_START = pd.Timestamp('2020-01-01T00')
INIT_STOP = pd.Timestamp('2020-12-31T12')
THREADS = 8

download_bytes = 0


def to_url(store):
	return store.replace('gs://', BASE)


def fetch(url, allow_missing=False):
	"""GET with retries; check body length against Content-Length and md5 against x-goog-hash"""
	global download_bytes
	for attempt in range(8):
		try:
			with urllib.request.urlopen(url, timeout=120) as resp:
				body = resp.read()
				expected_length = int(resp.headers['Content-Length'])
				if len(body) != expected_length:
					raise IOError('size mismatch %d != %d' % (len(body), expected_length))
				goog_hash = resp.headers.get_all('x-goog-hash') or []
				md5_values = [h.split('=', 1)[1] for part in goog_hash for h in part.split(',') if h.strip().startswith('md5=')]
				if md5_values:
					md5_here = base64.b64encode(hashlib.md5(body).digest()).decode()
					if md5_here != md5_values[0].strip():
						raise IOError('md5 mismatch')
				download_bytes += len(body)
				return body, bool(md5_values)
		except urllib.error.HTTPError as error:
			if error.code == 404 and allow_missing:
				return None, False
			if attempt == 7:
				raise
		except Exception:
			if attempt == 7:
				raise
		time.sleep(2 ** attempt)


def load_meta(store):
	return json.loads(fetch(to_url(store) + '/.zmetadata')[0])['metadata']


def read_coord(store, meta, name):
	"""Read a 1-D coordinate array (all its chunks) and decode times/timedeltas"""
	zarray = meta[name + '/.zarray']
	zattrs = meta[name + '/.zattrs']
	codec = numcodecs.get_codec(zarray['compressor'])
	chunk_count = -(-zarray['shape'][0] // zarray['chunks'][0])
	parts = [np.frombuffer(codec.decode(fetch(to_url(store) + '/' + name + '/' + str(i))[0]), dtype=zarray['dtype']) for i in range(chunk_count)]
	values = np.concatenate(parts)[:zarray['shape'][0]]
	units = zattrs.get('units', '')
	if ' since ' in units:
		step, origin = units.split(' since ')
		return pd.Timestamp(origin) + pd.to_timedelta(values, unit=step[0] if step != 'hours' else 'h')
	if units in ('hours', 'days', 'minutes', 'seconds', 'nanoseconds'):
		return pd.to_timedelta(values, unit={'hours': 'h', 'days': 'D', 'minutes': 'm', 'seconds': 's', 'nanoseconds': 'ns'}[units])
	return values


class ChunkReader:
	def __init__(self, store, meta, variable):
		self.store = store
		self.variable = variable
		self.zarray = meta[variable + '/.zarray']
		self.codec = numcodecs.get_codec(self.zarray['compressor'])
		self.separator = self.zarray.get('dimension_separator') or '.'

	def read(self, chunk_index):
		key = self.separator.join(str(i) for i in chunk_index)
		body, had_md5 = fetch(to_url(self.store) + '/' + self.variable + '/' + key, allow_missing=True)
		shape = self.zarray['chunks']
		if body is None:
			return np.full(shape, np.nan, dtype='float32'), False, True
		raw = self.codec.decode(body)
		return np.frombuffer(raw, dtype=self.zarray['dtype']).reshape(shape), had_md5, False


def latitude_weights(latitude_degrees):
	# Same as weatherbench2.metrics.get_lat_weights at 156e5dc
	points = np.deg2rad(latitude_degrees)
	bounds = np.concatenate([[-np.pi / 2], (points[:-1] + points[1:]) / 2, [np.pi / 2]])
	assert np.all(np.diff(bounds) > 0)
	weights = np.sin(bounds[1:]) - np.sin(bounds[:-1])
	return weights / weights.mean()


def load_truth(truth_store, variable, level, valid_times):
	"""Cache one level of the truth for the needed valid times in data/ (npy), return dict time -> field"""
	tag = truth_store.rstrip('/').split('/')[-2] + '_' + variable + str(level)
	cache_path = os.path.join(DATA_DIR, 'truth_' + tag + '.npz')
	if os.path.exists(cache_path):
		cached = np.load(cache_path)
		times = pd.to_datetime(cached['times'])
		# Read the array once: every cached['fields'] access re-reads the whole array (that cost 65 GB of RAM and killed the first GraphCast run)
		fields = cached['fields']
		return {t: fields[i] for i, t in enumerate(times)}, cached['latitude']
	meta = load_meta(truth_store)
	times = read_coord(truth_store, meta, 'time')
	levels = list(read_coord(truth_store, meta, 'level'))
	latitude = read_coord(truth_store, meta, 'latitude')
	reader = ChunkReader(truth_store, meta, variable)
	time_chunk, level_chunk = reader.zarray['chunks'][0], reader.zarray['chunks'][1]
	level_index = levels.index(level)
	time_positions = {t: i for i, t in enumerate(times)}
	needed_positions = sorted(time_positions[t] for t in valid_times)
	chunk_ids = sorted(set(p // time_chunk for p in needed_positions))

	def read_one(chunk_id):
		data, _, missing = reader.read((chunk_id, level_index // level_chunk, 0, 0))
		return chunk_id, data, missing

	fields = {}
	with ThreadPoolExecutor(THREADS) as pool:
		for chunk_id, data, missing in pool.map(read_one, chunk_ids):
			if missing:
				raise RuntimeError('truth chunk missing %s %d' % (tag, chunk_id))
			for offset in range(time_chunk):
				position = chunk_id * time_chunk + offset
				if position < len(times) and times[position] in valid_times:
					fields[times[position]] = np.array(data[offset, level_index % level_chunk], dtype='float32')
	ordered = sorted(fields)
	np.savez(cache_path, times=np.array(ordered, dtype='datetime64[ns]'), fields=np.stack([fields[t] for t in ordered]), latitude=latitude)
	print('truth cached', tag, len(ordered), 'times from', len(chunk_ids), 'chunks', flush=True)
	return fields, latitude


def load_above_ground(level):
	"""ERA5 climatological above_ground fraction at one level, shape (hour 4, dayofyear 366, lon, lat)"""
	cache_path = os.path.join(DATA_DIR, 'above_ground_%d.npz' % level)
	if os.path.exists(cache_path):
		cached = np.load(cache_path)
		return cached['fraction'], list(cached['hours']), list(cached['days'])
	meta = load_meta(CLIM_STORE)
	levels = list(read_coord(CLIM_STORE, meta, 'level'))
	hours = list(read_coord(CLIM_STORE, meta, 'hour'))
	days = list(read_coord(CLIM_STORE, meta, 'dayofyear'))
	reader = ChunkReader(CLIM_STORE, meta, 'above_ground')
	hour_chunk, day_chunk, level_chunk = reader.zarray['chunks'][:3]
	level_index = levels.index(level)
	fraction = np.empty((len(hours), len(days), 240, 121), dtype='float32')
	for day_block in range((len(days) + day_chunk - 1) // day_chunk):
		data, _, missing = reader.read((0, day_block, level_index // level_chunk, 0, 0))
		assert not missing
		count = min(day_chunk, len(days) - day_block * day_chunk)
		fraction[:, day_block * day_chunk:day_block * day_chunk + count] = data[:, :count, level_index % level_chunk]
	np.savez(cache_path, fraction=fraction, hours=hours, days=days)
	return fraction, hours, days


def main():
	forecast_store, truth_store, variable, level, out_prefix = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
	os.makedirs(DATA_DIR, exist_ok=True)
	started = time.time()
	meta = load_meta(forecast_store)
	init_times = read_coord(forecast_store, meta, 'time')
	leads = list(read_coord(forecast_store, meta, 'prediction_timedelta'))
	levels = list(read_coord(forecast_store, meta, 'level'))
	latitude = read_coord(forecast_store, meta, 'latitude')
	reader = ChunkReader(forecast_store, meta, variable)
	lead_chunk, level_chunk = reader.zarray['chunks'][1], reader.zarray['chunks'][2]
	assert reader.zarray['chunks'][0] == 1 and reader.zarray['chunks'][3:] == [240, 121]
	level_index = levels.index(level)

	# Inits selected by value: all 00/12 UTC of 2020
	wanted_inits = pd.date_range(INIT_START, INIT_STOP, freq='12h')
	init_positions = {t: i for i, t in enumerate(init_times)}
	missing_inits = [t for t in wanted_inits if t not in init_positions]
	present_inits = [t for t in wanted_inits if t in init_positions][:int(os.environ.get('WB2_MAX_INITS', '100000'))]
	# Leads selected by value, never by index
	lead_positions = {int(l / pd.Timedelta('1h')): i for i, l in enumerate(leads)}
	target_lead_positions = {h: lead_positions[h] for h in TARGET_LEADS_HOURS if h in lead_positions}
	lead_chunks = sorted(set(p // lead_chunk for p in target_lead_positions.values()))
	print('store', forecast_store, 'var', variable, level, 'inits present', len(present_inits), 'missing', [str(t) for t in missing_inits],
		'leads', target_lead_positions, 'lead chunks', lead_chunks, flush=True)

	valid_times = set(t + pd.Timedelta(hours=h) for t in present_inits for h in target_lead_positions)
	truth, truth_latitude = load_truth(truth_store, variable, level, valid_times)
	assert np.allclose(truth_latitude, latitude)
	fraction, clim_hours, clim_days = load_above_ground(level)
	lat_weights = latitude_weights(np.asarray(latitude))[np.newaxis, :] * np.ones((240, 1))

	# Restart: skip (init, lead chunk) pairs already in the jsonl
	out_path = out_prefix + '.jsonl'
	done = set()
	if os.path.exists(out_path):
		for line in open(out_path):
			record = json.loads(line)
			done.add((record['init'], record['lead_chunk']))
	jobs = [(t, c) for t in present_inits for c in lead_chunks if (str(t), c) not in done]
	print('jobs to do', len(jobs), 'already done', len(done), flush=True)

	def work(job):
		init_time, chunk_id = job
		data, had_md5, missing = reader.read((init_positions[init_time], chunk_id, level_index // level_chunk, 0, 0))
		records = []
		for hours, position in target_lead_positions.items():
			if position // lead_chunk != chunk_id:
				continue
			forecast_field = data[0, position % lead_chunk, level_index % level_chunk].astype('float64')
			valid_time = init_time + pd.Timedelta(hours=hours)
			error_squared = (forecast_field - truth[valid_time].astype('float64')) ** 2
			# V1: latitude weights only (public code). V2: times climatological above-ground fraction of the valid time
			mse_v1 = float((lat_weights * error_squared).sum() / lat_weights.sum())
			above = fraction[clim_hours.index(valid_time.hour), clim_days.index(valid_time.dayofyear)].astype('float64')
			combined = lat_weights * above
			mse_v2 = float((combined * error_squared).sum() / combined.sum())
			records.append({'init': str(init_time), 'lead_chunk': chunk_id, 'lead_hours': hours, 'mse_v1': mse_v1, 'mse_v2': mse_v2,
				'nan': bool(np.isnan(forecast_field).any()), 'chunk_missing': missing, 'md5_checked': had_md5})
		if not records:
			return [{'init': str(init_time), 'lead_chunk': chunk_id, 'lead_hours': None}]
		return records

	with open(out_path, 'a') as out_file, ThreadPoolExecutor(THREADS) as pool:
		for count, records in enumerate(pool.map(work, jobs), 1):
			for record in records:
				out_file.write(json.dumps(record) + '\n')
			out_file.flush()
			if count % 100 == 0:
				elapsed = time.time() - started
				print('%d/%d chunks, %.1f GB, %.1f MB/s' % (count, len(jobs), download_bytes / 1e9, download_bytes / 1e6 / elapsed), flush=True)

	# Aggregate: mean of per-init MSE over all inits, then sqrt (Eq. 2)
	records = [json.loads(line) for line in open(out_path)]
	records = [r for r in records if r.get('lead_hours') is not None]
	summary = {'forecast_store': forecast_store, 'truth_store': truth_store, 'variable': variable, 'level': level,
		'inits_present': len(present_inits), 'inits_missing': [str(t) for t in missing_inits], 'leads': {}}
	for hours in target_lead_positions:
		rows = {r['init']: r for r in records if r['lead_hours'] == hours}
		mse_v1 = np.array([rows[k]['mse_v1'] for k in sorted(rows)])
		mse_v2 = np.array([rows[k]['mse_v2'] for k in sorted(rows)])
		summary['leads'][hours] = {'n_inits': len(rows), 'rmse_v1': float(np.sqrt(mse_v1.mean())), 'rmse_v2': float(np.sqrt(mse_v2.mean())),
			'any_nan': any(r['nan'] for r in rows.values()), 'any_chunk_missing': any(r['chunk_missing'] for r in rows.values()),
			'all_md5_checked': all(r['md5_checked'] for r in rows.values())}
	json.dump(summary, open(out_prefix + '.summary.json', 'w'), indent=1)
	print(json.dumps(summary, indent=1))
	print('downloaded this run %.2f GB in %.0f s' % (download_bytes / 1e9, time.time() - started), flush=True)


if __name__ == '__main__':
	main()
