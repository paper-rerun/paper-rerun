# Build claims.json from the values read off Fig. 1 of arXiv 2308.15560v2 (page 15, sources/fig1_p15-15.png)
# Run once at pre-registration. After claims.sha256 is written, claims.json must not change
import json
import sys

FIGURE_LOCATION = 'Fig. 1 (Deterministic headline scorecards for upper-level variables), page 15 of arXiv 2308.15560v2'

# Tolerance rules, fixed before any computation on our side
Z500_TOLERANCE = {
	'rule': 'display_consistent',
	'accept_interval': '[paper - 0.5, paper + 1.0) m^2/s^2, i.e. our value rounds OR truncates to the integer printed in the figure',
	'basis': 'Fig. 1 prints Z500 as integers with no stated rounding rule. The authors\' own published per-lead results (sources/*_240x121_2020.nc, recomputed 2026-03-03) match the figure by truncation in 8 of 9 primary cells (e.g. 135.58 -> 135, 124.19 -> 124, 778.23 -> 778) and by rounding in GraphCast 7 d (467.92 -> 468), so both readings are admitted. Same data and same formula should give the same number up to float32 summation order, so no wider statistical tolerance is justified. The % difference is always reported as well.',
}
T850_TOLERANCE = {
	'rule': 'display_consistent',
	'accept_interval': '[paper - 0.005, paper + 0.01) K, i.e. our value rounds OR truncates to the 2 decimals printed in the figure',
	'basis': 'Fig. 1 prints T850 with 2 decimals; same reasoning as Z500. Note: the authors\' 2026 published files (no below-ground mask, see definition below_ground_mask) are 1.5-3% ABOVE the figure for T850 in all four models, so a mismatch under variant V1 is expected and is not by itself evidence of an error; variant V2 tests whether the paper-described mask explains it.',
}

MODELS = {
	'HRES': {
		'row': 'IFS HRES',
		'forecast_store': 'gs://weatherbench2/datasets/hres/2016-2022-0012-240x121_equiangular_with_poles_conservative.zarr',
		'truth_store': 'gs://weatherbench2/datasets/hres_t0/2016-2022-6h-240x121_equiangular_with_poles_conservative.zarr',
		'truth_label': 'HRES analysis (IFS HRES forecast at t=0)',
		'published_file': 'sources/hres_vs_hres_t0_240x121_2020.nc',
	},
	'GraphCast': {
		'row': 'GraphCast',
		'forecast_store': 'gs://weatherbench2/datasets/graphcast/2020/date_range_2019-11-16_2021-02-01_12_hours-240x121_equiangular_with_poles_conservative.zarr',
		'truth_store': 'gs://weatherbench2/datasets/era5/1959-2022-6h-240x121_equiangular_with_poles_conservative.zarr',
		'truth_label': 'ERA5',
		'published_file': 'sources/graphcast_vs_era5_240x121_2020.nc',
	},
	'Pangu': {
		'row': 'Pangu-Weather',
		'forecast_store': 'gs://weatherbench2/datasets/pangu/2018-2022_0012_240x121_equiangular_with_poles_conservative.zarr',
		'truth_store': 'gs://weatherbench2/datasets/era5/1959-2022-6h-240x121_equiangular_with_poles_conservative.zarr',
		'truth_label': 'ERA5',
		'published_file': 'sources/pangu_vs_era5_240x121_2020.nc',
	},
	'PanguOper': {
		'row': 'Pangu-Weather (oper.)',
		'forecast_store': 'gs://weatherbench2/datasets/pangu_hres_init/2020_0012_240x121_equiangular_with_poles_conservative.zarr',
		'truth_store': 'gs://weatherbench2/datasets/hres_t0/2016-2022-6h-240x121_equiangular_with_poles_conservative.zarr',
		'truth_label': 'HRES analysis (see definition truth_per_model, decided from the authors\' published files)',
		'published_file': 'sources/pangu_hres_init_vs_hres_t0_240x121_2020.nc',
	},
	'GraphCastOper': {
		'row': 'GraphCast (oper.)',
		'forecast_store': 'gs://weatherbench2/datasets/graphcast_hres_init/2020/date_range_2019-11-16_2021-02-01_12_hours-240x121_equiangular_with_poles_conservative.zarr',
		'truth_store': 'gs://weatherbench2/datasets/hres_t0/2016-2022-6h-240x121_equiangular_with_poles_conservative.zarr',
		'truth_label': 'HRES analysis (see definition truth_per_model, decided from the authors\' published files)',
		'published_file': 'sources/graphcast_hres_init_vs_hres_t0_240x121_2020.nc',
	},
	'NeuralGCM': {
		'row': 'NeuralGCM 0.7°',
		'forecast_store': 'gs://weatherbench2/datasets/neuralgcm_deterministic/2020-240x121_equiangular_with_poles_conservative.zarr',
		'truth_store': 'gs://weatherbench2/datasets/era5/1959-2022-6h-240x121_equiangular_with_poles_conservative.zarr',
		'truth_label': 'ERA5',
		'published_file': 'sources/neuralgcm_hres_vs_era5_240x121_2020.nc',
	},
}

# Values read from the rendered figure (lead days 1, 3, 5, 7, 10)
FIGURE_Z500 = {
	'HRES': [42, 135, 304, 521, 801],
	'GraphCast': [39, 124, 274, 468, 731],
	'Pangu': [44, 133, 294, 501, 778],
	'PanguOper': [45, 136, 300, 510, 785],
	'GraphCastOper': [40, 124, 277, 477, 751],
	'NeuralGCM': [37, 115, 267, 469, 751],
}
FIGURE_T850 = {
	'HRES': ['0.62', '1.15', '1.79', '2.59', '3.59'],
	'GraphCast': ['0.51', '0.93', '1.53', '2.29', '3.30'],
	'Pangu': ['0.61', '1.03', '1.68', '2.47', '3.50'],
	'NeuralGCM': ['0.53', '0.95', '1.56', '2.34', '3.38'],
}
# Authors' published values (benchmark_results, files dated 2026-03-03), global region, read by scripts/read_published.py
PUBLISHED_Z500 = {
	'HRES': [42.2966, 135.5835, 304.3541, 521.1854, 801.4990],
	'GraphCast': [39.7692, 124.1922, 274.2509, 467.9166, 731.9030],
	'Pangu': [44.3158, 133.8486, 294.3081, 501.1036, 778.2308],
	'PanguOper': [45.4468, 136.4913, 300.2748, 510.0939, 785.7491],
	'GraphCastOper': [40.5333, 124.4117, 276.7414, 477.1722, 754.0177],
	'NeuralGCM': [37.9377, 115.6961, 267.1336, 469.0978, 751.4130],
}
PUBLISHED_T850 = {
	'HRES': [0.6250, 1.1686, 1.8275, 2.6353, 3.6374],
	'GraphCast': [0.5189, 0.9484, 1.5592, 2.3361, 3.3619],
	'Pangu': [0.6201, 1.0556, 1.7133, 2.5166, 3.5485],
	'NeuralGCM': [0.5470, 0.9715, 1.5873, 2.3804, 3.4280],
}
LEAD_DAYS = [1, 3, 5, 7, 10]

claims = []


def add_claim(model_key, variable, lead_index, tier):
	model = MODELS[model_key]
	lead_days = LEAD_DAYS[lead_index]
	if variable == 'Z500':
		paper_value = FIGURE_Z500[model_key][lead_index]
		published = PUBLISHED_Z500[model_key][lead_index]
		unit = 'm^2/s^2 (geopotential, not geopotential height; the figure axis label prints "[kg^2/m^2]", read as a typo for m^2/s^2)'
		tolerance = Z500_TOLERANCE
		level = 500
		store_variable = 'geopotential'
	else:
		paper_value = float(FIGURE_T850[model_key][lead_index])
		published = PUBLISHED_T850[model_key][lead_index]
		unit = 'K'
		tolerance = T850_TOLERANCE
		level = 850
		store_variable = 'temperature'
	claims.append({
		'id': '%s_%s_%dd' % (model_key, variable, lead_days),
		'tier': tier,
		'quantity': 'Global RMSE of %s, %s vs %s, lead %d days (%d h), all 00/12 UTC initializations of 2020, 240x121 grid' % (variable, model['row'], model['truth_label'], lead_days, lead_days * 24),
		'paper_value': paper_value,
		'paper_value_as_printed': str(FIGURE_Z500[model_key][lead_index]) if variable == 'Z500' else FIGURE_T850[model_key][lead_index],
		'unit': unit,
		'location': FIGURE_LOCATION + ', row "%s", column group %s, lead time %d' % (model['row'], 'Pressure (500hPa geopotential)' if variable == 'Z500' else 'Temperature (850hPa temperature)', lead_days),
		'tolerance': tolerance,
		'conditions': {
			'forecast_store': model['forecast_store'],
			'truth_store': model['truth_store'],
			'store_variable': store_variable,
			'level_hPa': level,
			'lead_time_hours': lead_days * 24,
			'init_times': '2020-01-01T00 to 2020-12-31T12, every 12 h (732 inits expected)',
			'grid': '240x121 equiangular with poles (1.5 deg), conservative regridding already applied by the authors in the store',
			'region': 'global, all grid points',
		},
		'authors_published_value_2026': published,
		'authors_published_value_note': 'From %s (WeatherBench-X recomputation by the authors, 2026-03-03, no below-ground mask). Used only to decide ambiguities and as an auxiliary check, never as the target.' % model['published_file'],
	})


# Primary: Z500 at 3, 5, 10 days
for model_key in ('HRES', 'GraphCast', 'Pangu'):
	for lead_index in (1, 2, 4):
		add_claim(model_key, 'Z500', lead_index, 'primary')
# Secondary: Z500 at 1 and 7 days, T850 at all five leads
for model_key in ('HRES', 'GraphCast', 'Pangu'):
	for lead_index in (0, 3):
		add_claim(model_key, 'Z500', lead_index, 'secondary')
	for lead_index in range(5):
		add_claim(model_key, 'T850', lead_index, 'secondary')
# Optional: operational rows (Z500) and NeuralGCM 0.7 (Z500 and T850), only if time and disk allow
for model_key in ('PanguOper', 'GraphCastOper', 'NeuralGCM'):
	for lead_index in range(5):
		add_claim(model_key, 'Z500', lead_index, 'optional')
for lead_index in range(5):
	add_claim('NeuralGCM', 'T850', lead_index, 'optional')

definitions = [
	{
		'id': 'evaluation_period',
		'choice': 'All 00 and 12 UTC initializations from 2020-01-01T00 to 2020-12-31T12 (732 forecasts). Selection is on init time; verifying truth therefore extends to 2021-01-10T12.',
		'quote': 'Evaluation is done on all 00 and 12 UTC initialization times for 2020, i.e. from January 1 2020 00UTC to December 31 12 UTC. This means that some forecasts will extend into 2021.',
		'ambiguity': 'Low. The official commands use --time_start=2020-01-01 --time_stop=2020-12-31 on init time (docs/source/init-vs-valid-time.md at 156e5dc: "For all official WB2 evaluation, the init-time convention is used"). If any store lacks an init in this range, use the inits present, log the count and the missing dates, and do not fill them.',
	},
	{
		'id': 'lead_times',
		'choice': 'Leads 24, 72, 120, 168, 240 h for 1/3/5/7/10 days, selected by value of prediction_timedelta, never by index (HRES starts at 0 h, GraphCast and Pangu at 6 h).',
		'quote': 'Figure 1: Deterministic headline scorecards for upper-level variables. Values show absolute RMSE.',
		'ambiguity': 'Low. The figure axis is "Lead time [days]" with ticks 1, 3, 5, 7, 10; days = 24 h multiples. Pangu text says "The maximum lead time for the data used here is 7 days" (Section 3.6) but the figure prints a 10-day Pangu value and the store has leads up to 240 h, so the sentence is taken as stale and the 240 h lead is used.',
	},
	{
		'id': 'variables_and_units',
		'choice': 'Z500 = store variable "geopotential" at level 500 (m^2/s^2, not divided by g). T850 = store variable "temperature" at level 850 (K).',
		'quote': '500hPa geopotential RMSE [kg²/m²] ... 850hPa temperature RMSE [K] (Fig. 1 column labels)',
		'ambiguity': 'The Z500 unit label in the figure is a typo; the values (~800 at 10 d, climatology 820) are of geopotential in m^2/s^2, consistent with the stores and the authors\' published files.',
	},
	{
		'id': 'truth_per_model',
		'choice': 'IFS HRES vs hres_t0 (HRES t=0 used as analysis). GraphCast, Pangu-Weather and NeuralGCM (ERA5-initialized) vs ERA5. Optional operational rows (Pangu-Weather (oper.), GraphCast (oper.)) vs hres_t0.',
		'quote': 'For evaluating IFS forecasts, we use operational analyses as ground truth rather than ERA5. ... Here, as in Lam et al. (2023) we use the initial conditions, i.e. the IFS HRES forecasts at t=0 as our "analysis".',
		'ambiguity': 'For HRES and the ERA5-initialized models the official commands at 156e5dc agree (hres_vs_analysis uses hres_t0; pangu_vs_era uses era5). For the operational rows the paper does not say which truth is used, and official-evaluation.md lists pangu_hres_init against both. Decided from the authors\' published per-lead files: pangu_hres_init_vs_hres_t0 gives 45.4/136.5/300.3/510.1/785.7, matching the figure 45/136/300/510/785, while vs_era5 gives 48.8/137.5/301.0/510.9/786.9 (no match at 1 and 3 d). GraphCast (oper.) vs hres_t0 gives 40.5/124.4/276.7/477.2/754.0 against the figure 40/124/277/477/751; the 10 d cell does not match either truth (vs_era5 755.1), recorded as a pre-existing discrepancy between figure and published file.',
	},
	{
		'id': 'forecast_and_truth_stores',
		'choice': 'Use the pre-regridded 240x121 zarr stores listed per claim (conditions.forecast_store / truth_store). ERA5 truth is 1959-2022-6h-240x121_equiangular_with_poles_conservative.zarr, as in the official commands; the newer 1959-2023_01_10 store is not used.',
		'quote': 'Before the computation of the metrics, all forecasts and ground truths are first-order conservatively regridded to 1.5 resolution.',
		'ambiguity': 'GraphCast has no command in docs/source/official-evaluation.md at 156e5dc nor at v0.2.0; its store is taken from the bucket listing (datasets/graphcast/2020/, the only 240x121 store there) and the data guide. Regridding was done by the authors; we do not regrid. Stores are read selectively (only the variable, level and lead chunks needed).',
	},
	{
		'id': 'latitude_weights',
		'choice': 'w(i) = (sin(lat_upper) - sin(lat_lower)) normalized to mean 1 over the 121 latitudes; cell bounds are midpoints between grid latitudes, clipped to -90 and +90 at the pole rows (as _latitude_cell_bounds/_cell_area_from_latitude in weatherbench2/metrics.py at 156e5dc). Uniform weight in longitude.',
		'quote': 'All metrics are computed using an area-weighting over grid points. ... The latitude weights w(i) are computed as: [Eq. (1)] where θiu and θil indicate upper and lower latitude bounds, respectively, for the grid cell with latitude index i.',
		'ambiguity': 'Low. Eq. (1) and the code agree; the pole rows of the "with_poles" grid get half-width cells.',
	},
	{
		'id': 'rmse_definition',
		'choice': 'For each init t, spatially weighted mean of squared error (forecast minus truth at valid time = init + lead); average over the 732 inits; then square root. Time mean inside the square root.',
		'quote': 'The RMSE is defined for each variable and level as [Eq. (2): sqrt of (1/TIJ) sum over t,i,j of w(i)(f - o)^2]. Note that this agrees with the definition of the RMSE used by the WMO and ECMWF. In WB1, the time mean was taken outside the square root.',
		'ambiguity': 'Low. The official deterministic config computes "mse" per chunk and averages in time; RMSE = sqrt(mean MSE). The rmse_sqrt_before_time_avg metric (WB1 style) belongs to deterministic_temporal and is NOT the figure quantity.',
	},
	{
		'id': 'below_ground_mask',
		'choice': 'Compute two variants and report both. V1 (public code at 156e5dc and v0.2.0): no below-ground mask. V2 (paper Section 4.2.1, implemented by us): extra spatial weight = ERA5 climatological above_ground fraction from gs://weatherbench2/datasets/era5-hourly-climatology/1990-2019_6h_240x121_equiangular_with_poles_conservative.zarr, selected by the valid time\'s day of year and hour, at the same level; spatial mean = sum(w(i) * a * err^2) / sum(w(i) * a). A claim counts as reproduced if it is display-consistent under V1 or V2, and the report says which. Hypothesis written before computing: Z500 matches under both; T850 matches only under V2.',
		'quote': 'Here, we exclude below ground grid points from the computation of all metrics. To do so, we compute the climatological fraction of above-ground grid points (defined by geopotential > geopotential at surface) for each pressure level using the same doy-tod dependent method described in Section 3.2. We then use this fraction as an additional weight when computing spatial averages.',
		'ambiguity': 'High for T850, low for Z500. The public code never contained the mask (issue #254, author reply: the code was not uploaded and the mask was removed from the website later). Unspecified details fixed here: doy/tod taken from the valid time (truth time), normalization by the combined weight sum, climatology store as above. The authors\' 2026 published files are without the mask and sit 1.5-3% above the figure for T850 and within display rounding for Z500, which is what motivates V2; the files were not used to choose any V2 detail.',
	},
	{
		'id': 'figure_rounding_and_tolerance',
		'choice': 'A computed value matches if it rounds or truncates to the printed value (Z500 integer, T850 two decimals). Also report the absolute and % difference to the printed value and to the authors\' 2026 published value. Auxiliary (not verdict) check: V1 should agree with the authors\' 2026 published value within 0.1% relative; a larger gap is reported as a finding.',
		'quote': 'Values show absolute RMSE. Colors denote % difference to the IFS HRES baseline. (Fig. 1 caption)',
		'ambiguity': 'The rounding rule is not stated. The published files show truncation in most cells and rounding in GraphCast 7 d Z500 (467.92 -> 468) and GraphCast (oper.) 5 d (276.74 -> 277), so both are admitted. The 0.1% auxiliary threshold is set because WeatherBench-X on the same stores and formula should only differ by float32 summation order.',
	},
	{
		'id': 'missing_values',
		'choice': 'No skipping of NaN (skipna=False as in metrics._spatial_average). If a NaN appears in a needed chunk, stop that model, log the init, lead and level, and report it rather than dropping it.',
		'quote': 'Evaluation is done on all 00 and 12 UTC initialization times for 2020',
		'ambiguity': 'The paper does not discuss missing data. Not expected for these stores; any deviation is reported.',
	},
	{
		'id': 'code_version',
		'choice': 'Reference code google-research/weatherbench2 at 156e5dc9eafc18b8f8b215abc3a36b6305c266b8 (arXiv v2 date), variant v0.2.0 (81f1993). Main computation by an own selective-chunk script implementing the definitions above; cross-check with scripts/evaluate.py (official deterministic config) on a subset (one month) for agreement.',
		'quote': 'A regridding tool is available on the WB2 GitHub page.',
		'ambiguity': 'The official command lists are identical at both commits for the forecast/obs paths. The website now uses WeatherBench-X (issue #254), which produced the 2026 published files. Running evaluate.py over the full year would read ~143 GB for Z500 alone, so the full run uses the selective script; the subset cross-check establishes equivalence.',
	},
	{
		'id': 'paper_version',
		'choice': 'Target numbers are read from arXiv 2308.15560v2 (2024-01-26), Fig. 1, page 15 (sources/arxiv-2308.15560v2.pdf, sources/fig1_p15-15.png).',
		'quote': 'Figure 1: Deterministic headline scorecards for upper-level variables. Values show absolute RMSE. Colors denote % difference to the IFS HRES baseline.',
		'ambiguity': 'The JAMES version (2024-06) could not be read (publisher PDF behind Cloudflare; not bypassed). Its Fig. 1 may have been regenerated; the report must say the target is the arXiv v2 figure.',
	},
]

document = {
	'paper': 'Rasp, S. et al. "WeatherBench 2: A Benchmark for the Next Generation of Data-Driven Global Weather Models". JAMES 16(6), e2023MS004019 (2024). DOI 10.1029/2023MS004019. Numbers from arXiv 2308.15560v2.',
	'code': 'https://github.com/google-research/weatherbench2 @ 156e5dc9eafc18b8f8b215abc3a36b6305c266b8 (variant v0.2.0 = 81f1993ee6a1a156611c32dd85deeb3f3059b486)',
	'stage': 'pre-registration; no model run and no result computed on our side',
	'claim_counts': {
		'primary': sum(1 for c in claims if c['tier'] == 'primary'),
		'secondary': sum(1 for c in claims if c['tier'] == 'secondary'),
		'optional': sum(1 for c in claims if c['tier'] == 'optional'),
	},
	'sources_downloaded': {
		'arxiv-2308.15560v2.pdf': '28,480,050 B, HTTP 200 (size matches server)',
		'benchmark_results/*.nc': '8 files from https://storage.googleapis.com/weatherbench2/benchmark_results/, each size and md5 checked against the GCS object metadata (x-goog-hash / JSON API md5Hash); values in sources/published_values.txt',
		'code files at 156e5dc': 'official-evaluation.md, metrics.py, evaluate.py, init-vs-valid-time.md, data-guide.ipynb (raw.githubusercontent.com, HTTP 200)',
	},
	'claims': claims,
	'definitions': definitions,
}

with open(sys.argv[1], 'w', encoding='utf-8', newline='\n') as output_file:
	json.dump(document, output_file, ensure_ascii=False, indent=1)
	output_file.write('\n')
print('claims:', document['claim_counts'])
