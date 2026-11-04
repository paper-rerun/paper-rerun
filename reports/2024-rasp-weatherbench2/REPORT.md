# Reproduction report: WeatherBench 2: A Benchmark for the Next Generation of Data-Driven Global Weather Models

- Paper: Rasp, S., Hoyer, S., Merose, A., Langmore, I., Battaglia, P., Russell, T., Sanchez-Gonzalez, A., Yang, V., Carver, R., Agrawal, S., Chantry, M., Ben Bouallegue, Z., Dueben, P., Bromberg, C., Sisk, J., Barrington, L., Bell, A., Sha, F. Journal of Advances in Modeling Earth Systems 16(6), e2023MS004019, 2024. DOI: 10.1029/2023MS004019. The numbers come from arXiv 2308.15560v2 (2024-01-26). The AGU PDF is behind Cloudflare and we did not try to get around it.
- Code: https://github.com/google-research/weatherbench2 @ 156e5dc9eafc18b8f8b215abc3a36b6305c266b8 (the commit of arXiv v2). v0.2.0 (81f1993) has the same official commands for these stores.
- Data: the public bucket gs://weatherbench2, read over https://storage.googleapis.com/weatherbench2/ with no login. We used the 240x121 stores of IFS HRES, hres_t0, ERA5, GraphCast, Pangu-Weather, Pangu-Weather and GraphCast started from HRES, NeuralGCM 0.7°, and the ERA5 1990-2019 hourly climatology.
- Target: Fig. 1 of arXiv v2 (the deterministic headline scorecard on page 15), global RMSE in 2020. We computed 6 of its 12 model rows.
  - Primary: Z500 at 3, 5 and 10 days for IFS HRES, GraphCast and Pangu-Weather (9 cells).
  - Secondary: Z500 at 1 and 7 days and T850 at 1 to 10 days for the same three models (21 cells).
  - Optional: Z500 for the Pangu-Weather (oper.) and GraphCast (oper.) rows, Z500 and T850 for NeuralGCM 0.7° (20 cells).
  - Not computed: the IFS ENS Mean, ERA5 Forecasts, Keisler (2022), FuXi, SphericalCNN and NeuralGCM ENS Mean rows, T850 for the two (oper.) rows, and the humidity and wind columns.
- Verdict: **Reproduced**
- Date: 2026-11-04
- Hardware: Ryzen 9 3900X, 31 GB RAM visible to WSL2 Ubuntu 24.04, CPU only (the RTX 2070 SUPER was not needed)

All 50 pre-registered cells match the figure within the pre-registered tolerance, on the full set of 732 initialisations of 2020.

- The 9 primary cells match with the public code as it is, with no below-ground mask.
- The T850 cells match only with the below-ground mask described in Section 4.2.1 of the paper. That mask is not in the public code. We implemented it from the paper text and fixed its details before any run.

## Results

**Tolerance.** It was fixed before any run, in claims.json. Our value has to round or truncate to the number printed in the figure. That means [paper - 0.5, paper + 1) for Z500 and [paper - 0.005, paper + 0.01) for T850.

**Variants and units.**
- V1 uses latitude weights only, as the public code does.
- V2 multiplies the latitude weights by the ERA5 climatological above-ground fraction at the valid time (paper Section 4.2.1).
- "Authors 2026" is the value in the authors' own `benchmark_results/*_240x121_2020.nc` files. They were recomputed with WeatherBench-X on 2026-03-03, without the mask. They are an extra check, not the target.
- Z500 is in m²/s² and T850 in K.

### Primary (Z500, 3/5/10 days)

| Quantity | Paper | Ours V1 | Ours V2 | Diff V1 | Authors 2026 | V1 vs 2026 | Match |
|---|---|---|---|---|---|---|---|
| IFS HRES Z500 3 d | 135 | 135.5835 | 135.5837 | +0.43% | 135.5835 | +0.000% | yes (V1) |
| IFS HRES Z500 5 d | 304 | 304.3541 | 304.3545 | +0.12% | 304.3541 | -0.000% | yes (V1) |
| IFS HRES Z500 10 d | 801 | 801.4990 | 801.5000 | +0.06% | 801.4990 | -0.000% | yes (V1) |
| GraphCast Z500 3 d | 124 | 124.2145 | 124.2146 | +0.17% | 124.1922 | +0.018% | yes (V1) |
| GraphCast Z500 5 d | 274 | 274.3602 | 274.3606 | +0.13% | 274.2509 | +0.040% | yes (V1) |
| GraphCast Z500 10 d | 731 | 731.6540 | 731.6550 | +0.09% | 731.9030 | -0.034% | yes (V1) |
| Pangu-Weather Z500 3 d | 133 | 133.8486 | 133.8488 | +0.64% | 133.8486 | +0.000% | yes (V1) |
| Pangu-Weather Z500 5 d | 294 | 294.3081 | 294.3085 | +0.10% | 294.3081 | +0.000% | yes (V1) |
| Pangu-Weather Z500 10 d | 778 | 778.2308 | 778.2319 | +0.03% | 778.2308 | +0.000% | yes (V1) |

### Secondary

| Quantity | Paper | Ours V1 | Ours V2 | Diff V1 | Diff V2 | Authors 2026 | Match |
|---|---|---|---|---|---|---|---|
| IFS HRES Z500 1 d | 42 | 42.2966 | 42.2966 | +0.71% | +0.71% | 42.2966 | yes (V1) |
| IFS HRES Z500 7 d | 521 | 521.1854 | 521.1861 | +0.04% | +0.04% | 521.1854 | yes (V1) |
| GraphCast Z500 1 d | 39 | 39.7752 | 39.7752 | +1.99% | +1.99% | 39.7692 | yes (V1) |
| GraphCast Z500 7 d | 468 | 468.0296 | 468.0302 | +0.01% | +0.01% | 467.9166 | yes (V1) |
| Pangu-Weather Z500 1 d | 44 | 44.3158 | 44.3158 | +0.72% | +0.72% | 44.3158 | yes (V1) |
| Pangu-Weather Z500 7 d | 501 | 501.1036 | 501.1043 | +0.02% | +0.02% | 501.1036 | yes (V1) |
| IFS HRES T850 1 d | 0.62 | 0.6250 | 0.6209 | +0.80% | +0.15% | 0.6250 | yes (V1 and V2) |
| IFS HRES T850 3 d | 1.15 | 1.1686 | 1.1534 | +1.62% | +0.30% | 1.1686 | V2 only |
| IFS HRES T850 5 d | 1.79 | 1.8275 | 1.7984 | +2.09% | +0.47% | 1.8275 | V2 only |
| IFS HRES T850 7 d | 2.59 | 2.6353 | 2.5973 | +1.75% | +0.28% | 2.6353 | V2 only |
| IFS HRES T850 10 d | 3.59 | 3.6374 | 3.5948 | +1.32% | +0.13% | 3.6374 | V2 only |
| GraphCast T850 1 d | 0.51 | 0.5192 | 0.5129 | +1.80% | +0.57% | 0.5189 | yes (V1 and V2) |
| GraphCast T850 3 d | 0.93 | 0.9489 | 0.9322 | +2.04% | +0.23% | 0.9484 | V2 only |
| GraphCast T850 5 d | 1.53 | 1.5602 | 1.5309 | +1.97% | +0.06% | 1.5592 | V2 only |
| GraphCast T850 7 d | 2.29 | 2.3373 | 2.2943 | +2.07% | +0.19% | 2.3361 | V2 only |
| GraphCast T850 10 d | 3.30 | 3.3630 | 3.3057 | +1.91% | +0.17% | 3.3619 | V2 only |
| Pangu-Weather T850 1 d | 0.61 | 0.6201 | 0.6108 | +1.66% | +0.14% | 0.6201 | V2 only |
| Pangu-Weather T850 3 d | 1.03 | 1.0556 | 1.0350 | +2.48% | +0.49% | 1.0556 | V2 only |
| Pangu-Weather T850 5 d | 1.68 | 1.7133 | 1.6834 | +1.98% | +0.20% | 1.7133 | V2 only |
| Pangu-Weather T850 7 d | 2.47 | 2.5166 | 2.4761 | +1.89% | +0.25% | 2.5166 | V2 only |
| Pangu-Weather T850 10 d | 3.50 | 3.5485 | 3.5088 | +1.39% | +0.25% | 3.5485 | V2 only |

### Optional

| Quantity | Paper | Ours V1 | Ours V2 | Diff V1 | Diff V2 | Authors 2026 | Match |
|---|---|---|---|---|---|---|---|
| Pangu-Weather (oper.) Z500 1 d | 45 | 45.4468 | 45.4468 | +0.99% | +0.99% | 45.4468 | yes (V1) |
| Pangu-Weather (oper.) Z500 3 d | 136 | 136.4913 | 136.4914 | +0.36% | +0.36% | 136.4913 | yes (V1) |
| Pangu-Weather (oper.) Z500 5 d | 300 | 300.2748 | 300.2752 | +0.09% | +0.09% | 300.2748 | yes (V1) |
| Pangu-Weather (oper.) Z500 7 d | 510 | 510.0939 | 510.0946 | +0.02% | +0.02% | 510.0939 | yes (V1) |
| Pangu-Weather (oper.) Z500 10 d | 785 | 785.7491 | 785.7501 | +0.10% | +0.10% | 785.7491 | yes (V1) |
| GraphCast (oper.) Z500 1 d | 40 | 40.2964 | 40.2964 | +0.74% | +0.74% | 40.5333 | yes (V1) |
| GraphCast (oper.) Z500 3 d | 124 | 124.1390 | 124.1391 | +0.11% | +0.11% | 124.4117 | yes (V1) |
| GraphCast (oper.) Z500 5 d | 277 | 277.1196 | 277.1199 | +0.04% | +0.04% | 276.7414 | yes (V1) |
| GraphCast (oper.) Z500 7 d | 477 | 477.2840 | 477.2846 | +0.06% | +0.06% | 477.1722 | yes (V1) |
| GraphCast (oper.) Z500 10 d | 751 | 751.5208 | 751.5218 | +0.07% | +0.07% | 754.0177 | yes (V1) |
| NeuralGCM 0.7° Z500 1 d | 37 | 37.9377 | 37.9377 | +2.53% | +2.53% | 37.9377 | yes (V1) |
| NeuralGCM 0.7° Z500 3 d | 115 | 115.6961 | 115.6962 | +0.61% | +0.61% | 115.6961 | yes (V1) |
| NeuralGCM 0.7° Z500 5 d | 267 | 267.1336 | 267.1340 | +0.05% | +0.05% | 267.1336 | yes (V1) |
| NeuralGCM 0.7° Z500 7 d | 469 | 469.0978 | 469.0984 | +0.02% | +0.02% | 469.0978 | yes (V1) |
| NeuralGCM 0.7° Z500 10 d | 751 | 751.4130 | 751.4141 | +0.05% | +0.06% | 751.4130 | yes (V1) |
| NeuralGCM 0.7° T850 1 d | 0.53 | 0.5470 | 0.5358 | +3.21% | +1.09% | 0.5470 | V2 only |
| NeuralGCM 0.7° T850 3 d | 0.95 | 0.9715 | 0.9541 | +2.27% | +0.43% | 0.9715 | V2 only |
| NeuralGCM 0.7° T850 5 d | 1.56 | 1.5873 | 1.5601 | +1.75% | +0.01% | 1.5873 | V2 only |
| NeuralGCM 0.7° T850 7 d | 2.34 | 2.3804 | 2.3430 | +1.73% | +0.13% | 2.3804 | V2 only |
| NeuralGCM 0.7° T850 10 d | 3.38 | 3.4280 | 3.3835 | +1.42% | +0.10% | 3.4280 | V2 only |

### Totals

| Tier | Cells | Match under V1 | Match under V1 or V2 |
|---|---|---|---|
| Primary | 9 | 9 | 9 |
| Secondary | 21 | 8 | 21 |
| Optional | 20 | 15 | 20 |

- **Z500:** every cell matches with or without the mask. In most cells the mask moves Z500 by less than 0.001 m²/s².
- **T850:** 18 of the 20 cells match only with the mask. The other 2 (HRES and GraphCast at 1 day) match either way. Claims.json stated this hypothesis before any run.
- **Rounding or truncation.** All 50 cells match under truncation. Under rounding alone, 15 would not match, counting the variant that matches each cell:
  - 8 Z500 cells under V1, for example HRES 3 d at 135.58 and NeuralGCM 1 d at 37.94;
  - 7 T850 cells under V2, for example HRES 5 d at 1.7984, Pangu-Weather 10 d at 3.5088 and NeuralGCM 1 d at 0.5358.

  With V2 for Z500 too it is 16, because HRES 10 d under V2 is 801.50005. So the figure seems to truncate. Every V2 T850 value sits above the printed number, by +0.007% to +1.09%, which fits truncation. Our mask therefore matches the figure at its printed precision, but that does not show it is the same as the authors' implementation.
- **Data checks:**
  - Every lead has 732 initialisations, no NaN and no missing chunk.
  - Every forecast chunk carried an md5 in `x-goog-hash` and passed it, plus the Content-Length check (`all_md5_checked` in each `runs/out/*.summary.json`).
  - Truth and climatology chunks went through the same check, which fails on a mismatch, but whether an md5 was present was not logged.
  - The evaluate.py cross-check runs read through gcsfs without our checks.

### Cross-check with the official code

We ran scripts/evaluate.py at 156e5dc (deterministic config, in-memory runner) on the same 62 initialisations of January 2020. We compared it with our per-initialisation results for those dates. The flags come from docs/source/official-evaluation.md, narrowed to one variable, one level and that month.

The two GraphCast cases were added during the revision of this report, for two reasons:
- their stores have a different layout: GraphCast has 37 levels per chunk and 886 initialisation times, GraphCast (oper.) has 13 levels and 732 times;
- they are the only stores where our values and the authors' 2026 files differ by more than 0.006%.

| Case | Lead | evaluate.py | Ours | Rel. diff |
|---|---|---|---|---|
| IFS HRES vs hres_t0, Z500 | 1 / 3 / 5 / 7 / 10 d | 43.474845 / 130.380264 / 283.875051 / 487.014288 / 787.601938 | 43.474845 / 130.380264 / 283.875050 / 487.014288 / 787.601938 | below 1.5e-9 |
| Pangu-Weather vs ERA5, T850 | 1 / 3 / 5 / 7 / 10 d | 0.614560 / 1.030281 / 1.659354 / 2.424182 / 3.592461 | same to 6 decimals | below 2.2e-10 |
| GraphCast vs ERA5, Z500 | 1 / 3 / 5 / 7 / 10 d | 39.562942 / 119.585331 / 255.233463 / 431.763843 / 696.047390 | same to 6 decimals | below 1.7e-9 |
| GraphCast (oper.) vs hres_t0, Z500 | 1 / 3 / 5 / 7 / 10 d | 40.028199 / 120.900381 / 261.438932 / 443.772502 / 726.729305 | same to 6 decimals | below 1.7e-9 |

On January 2020, our script gives the same V1 numbers as evaluate.py for these four cases, up to float rounding (`runs/logs/crosscheck.log`). The cross-check does not cover the other eleven months, GraphCast T850, Pangu-Weather (oper.) or NeuralGCM.

## What it took

1. **Environment.**
   - Python 3.11 venv built with uv, resolved with `--exclude-newer 2024-01-26` (the arXiv v2 date) from the setup.py pins at 156e5dc.
   - Main versions: xarray 2023.7.0, pandas 2.0.3, zarr 2.16.1, apache-beam 2.53.0, plus gcsfs. weatherbench2 was installed from the clone with `--no-deps`.
   - Lockfile `env/requirements.lock`, setup script `env/setup_env.sh`, inputs `env/requirements.in`.
   - We did not change the authors' code. The only file in `patches/` is a diff of our own script (step 6).
2. **Main computation (`runs/scripts/wb2_rmse.py`).**
   - The script fetches only the zarr chunks that hold the 24, 72, 120, 168 and 240 h leads, picked by the value of `prediction_timedelta`.
   - Each zarr chunk holds 8 lead times, so picking leads saved little. The script read 5 of 5 lead chunks for Pangu-Weather and GraphCast and 5 of 6 for HRES: 266.5 GB for the six primary runs, against an estimated 286 GB for evaluate.py.
   - What the script did add:
     - a size check and an md5 check on every chunk (Content-Length and the md5 in `x-goog-hash`);
     - restartability;
     - no forecast data on disk, since chunks are decompressed in memory.
   - We did not run evaluate.py on the full year. It is checked on January 2020 only (above), where each case took 4 to 9 minutes. A full-year run was feasible.
   - Latitude weights copy `metrics.get_lat_weights` at 156e5dc.
   - For each initialisation the script stores the spatially weighted MSE (V1 and V2). RMSE is then sqrt(mean over the 732 initialisations), as in Eq. (2) of the paper.
   - The truth fields for the needed valid times and the above-ground fraction were cached in `data/` during the run and deleted afterwards.
3. **Below-ground mask (V2).** The public code does not have it (issue #254), so we implemented it from Section 4.2.1:
   - weight = latitude weight × `above_ground` from `era5-hourly-climatology/1990-2019_6h_240x121_equiangular_with_poles_conservative.zarr`;
   - the fraction is taken at the valid time's day of year and hour, at the same pressure level;
   - the weighted mean is normalised by the sum of the combined weights.

   These details were fixed in claims.json before the run and not tuned afterwards.
4. **Driver and outputs.**
   - The driver `runs/scripts/run_all.sh` can be restarted: results per initialisation go to `runs/out/*.jsonl`, and work already done is skipped.
   - Exit codes in `runs/logs/run_all.log` mean nothing. In `echo "$(date -Is) end $name exit $?"`, the `$(date)` substitution resets `$?`, so every line says `exit 0`, including the one right after the `Killed` line.
     - Completion is shown by each `runs/out/*.summary.json` and the per-model log.
     - The driver now saves `rc=$?` before the echo, as `run_one.sh` does. It was not re-run after that change.
   - The head of run_all.log was lost. It starts with a "No such file or directory" line from an earlier call, and it has no start lines for hres_z500, pangu_z500 or the first GraphCast Z500 attempt. We take the start of the run, about 21:45, from `hres_z500.log` (999 s, ending at 22:02).
   - Per-model results are in `runs/out/*.summary.json`.
   - The comparison with the paper is in `runs/results.csv` and `runs/logs/compare.log`.
   - The cross-check is in `runs/official/`, `runs/logs/official_subset.log`, `runs/logs/official_subset_graphcast.log` and `runs/logs/crosscheck.log`.
5. **Runtime and download.**
   - 2 h 44 min wall clock, from about 21:45 to 00:28:59 local. That includes the incident in step 6 and the GraphCast Z500 rerun at 00:10. The per-run logs show 21 to 69 MB/s.
   - 418.8 GB of forecast chunks read from the bucket, per the "downloaded this run" line of each log:

     | Model | Z500 | T850 |
     |---|---|---|
     | IFS HRES | 24.60 GB | 25.21 GB |
     | Pangu-Weather | 29.40 GB | 29.41 GB |
     | GraphCast (37 levels per chunk) | 78.44 GB | 79.47 GB |
     | Pangu-Weather (oper.) | 27.96 GB | not needed |
     | GraphCast (oper.) | 27.91 GB | not needed |
     | NeuralGCM 0.7° | 47.87 GB | 48.49 GB |

     The truth fields, the climatology and the evaluate.py runs read more on top of that. Those sizes were not logged.
   - RAM and CPU use of the main runs were not logged (see step 6).
   - The two evaluate.py runs added in the revision peaked at 2.96 GB and 2.40 GB RSS and took 8 min 47 s and 4 min 12 s (`/usr/bin/time -v` in `official_subset_graphcast.log`). They capped dask at 8 workers.
   - The January runs from 21:46 to 21:55 did not cap dask, so it used its default of one thread per logical CPU (24 in WSL).
   - Free space on E: was 107 GB after the Z500 runs and 106 GB at the end of the last run (run_all.log). The drive is shared with another job.
   - After `data/` was emptied, free space was 107 GB (`runs/logs/disk_after_cleanup.log`). Only scripts, logs and scores remain.
6. **A bug in our own script, now fixed.**
   - **First attempt.** The first GraphCast Z500 run, inside run_all.sh from 22:16 to 22:24:51, died with no traceback while loading the cached ERA5 truth. The only trace is the `Killed` line in run_all.log.
   - **Cause.** The script indexed an `np.load` NpzFile inside a dict comprehension. Each of the 750 accesses re-read the whole 87 MB array, i.e. up to about 65 GB (a projection, not a measurement). The kernel killed the process, so our 10 GB RAM limit was exceeded.
   - **Second attempt.** We started it by hand with `run_one.sh` at 22:31:56, and it hit the same problem.
     - `run_one.log` has no end line for it.
     - Its `/usr/bin/time -v` output was lost: the driver re-ran graphcast_z500 at 00:10 and overwrote the log with `>`.
     - What we saw live was not logged: WSL swapped about 1 GB and stopped responding, and we stopped the process.
   - **Thread limit.** From 22:31:56 the second attempt ran next to the driver (hres_t850, then pangu_t850 from 22:38). Two 8-thread processes overlapped, so the 8-thread limit was also exceeded. The stop time was not logged.
   - **Fix.** Read the array once. The script was edited at 22:46:01.
     - hres_t850 and pangu_t850 ran on the earlier version. They built their caches (`truth cached` lines in their logs), so the edited lines never ran for them. Every earlier run also built its cache.
     - No copy of the earlier source was kept. The only earlier copy is the bytecode cache `runs/scripts/__pycache__/wb2_rmse.cpython-311.pyc` from 21:42.
     - Compared with the final script (`runs/logs/pyc_diff.log`), that cache differs in two places only: the cache-loading lines of `load_truth`, and two smoke-test options (`WB2_DATA_DIR`, `WB2_MAX_INITS`, no-ops by default) added after 21:42.
     - The rebuilt diff is in `patches/wb2_rmse_cache_fix.diff`.
   - **Rerun.** GraphCast Z500 then ran from scratch at 00:10 with the fixed script (3660 jobs, 0 already done). No reported number comes from a run with the bug.
   - **For next time.** Peak RSS goes into a log that is appended to and never overwritten.

## Alternative readings

These never change the verdict.

- **WB1-style RMSE.** This is the `rmse_sqrt_before_time_avg` metric: the square root of each initialisation's MSE, then the mean over time. It gives Z500 at 10 days of 796.39 (HRES), 725.50 (GraphCast) and 771.94 (Pangu-Weather), against 801, 731 and 778 in the figure. So the figure takes the time mean inside the square root, as Eq. (2) says (`runs/logs/alt_wb1.log`).
- **Other definitions.** We found no reason to doubt the rest of the pre-registered definitions. The authors' 2026 files and the figure disagree only where we expected: T850, which needs the mask, and the GraphCast (oper.) row (see the Notes).

## Notes for the authors

Thanks for the public bucket and the list of official commands. Everything we needed was there. The 50 pre-registered Z500 and T850 cells of Fig. 1 (6 of its 12 model rows) came out on a home machine in under 3 hours. A few things we noticed:

1. **Below-ground mask.** The Fig. 1 T850 values only come out with the mask from Section 4.2.1.
   - Without it, our values are 0.8 to 3.2% higher than the figure, and they match your 2026 benchmark_results files.
   - Issue #254 already says the mask code was never released. A short note in the docs would help: the paper figures use the mask, while the current website and files do not. Then people comparing against the paper know which version they are looking at.
   - Our reading of the mask matches every T850 cell at the figure's printed precision, assuming the figure truncates. That reading is: the valid time's day of year and hour, normalised by the combined weight sum.
   - All our masked values sit 0.007% to 1.09% above the printed numbers, so this does not show the two implementations are the same. If yours was different, it would be good to know.
2. **GraphCast (oper.) in the 2026 files.**
   - Our value for this row matches the figure in all 5 cells (10 d: 751.52 against 751). We used `graphcast_hres_init/2020/date_range_2019-11-16_2021-02-01_12_hours-240x121...zarr` against hres_t0.
   - It differs from `graphcast_hres_init_vs_hres_t0_240x121_2020.nc` by up to 0.58%.
   - 4 of the 5 cells exceed the 0.1% auxiliary threshold we pre-registered for this comparison (1/3/5/10 d: -0.58/-0.22/+0.14/-0.33%). All other 46 cells are within it.
   - For every other row, the files and our values agree within 0.061%.
3. **GraphCast (ERA5) in the 2026 files.** Same pattern, smaller:
   - our values differ from `graphcast_vs_era5_240x121_2020.nc` by 0.015 to 0.061%;
   - HRES, Pangu-Weather and NeuralGCM agree to 0.006% or better.

   This does not affect the figure. On January 2020, evaluate.py at 156e5dc gives the same Z500 numbers as our script for both GraphCast stores (to 1.7e-9), so the gap is not in how we read these stores. It sits between evaluate.py run on the stores named in the docs and the 2026 WeatherBench-X files. We cannot tell whether it comes from the stores, the time selection or WeatherBench-X itself.
4. **Small things in the paper text.**
   - The Fig. 1 axis label for Z500 reads "kg²/m²", but the values are geopotential in m²/s².
   - Section 3.6 says the Pangu-Weather data goes to 7 days, but the figure and the store go to 10 days.
   - GraphCast has no command in docs/source/official-evaluation.md. We took its store from the bucket listing and the data guide.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder. The two exceptions are marked as such in step 6: the 65 GB figure is a projection, and what we saw live during the incident was not logged.

The claims, definitions and tolerances were pre-registered in claims.json. It was frozen at 2026-11-04T00:34:26Z (claims.sha256), before the first run at about 00:45Z, and its SHA-256 still matched after the run. A single agent then did the rest of the work on a Ryzen 9 3900X, using only the CPU (the RTX 2070 SUPER was not used):

- built the environment;
- ran the computation;
- cross-checked it against the authors' evaluate.py;
- compared the results with the paper;
- wrote this report.

A reviewer agent then checked the report against the logs. A reviser agent corrected it and ran the two GraphCast cross-checks. A human will read it before publication. There has been no blind recomputation by a second agent yet.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues