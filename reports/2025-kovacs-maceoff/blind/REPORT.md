# Reproduction report (blind): MACE-OFF, test-set errors of MACE-OFF23 S/M/L

- **Paper:** Kovács, D. P., Moore, J. H., Browning, N. J., et al. "MACE-OFF: Short-Range Transferable Machine Learning Force Fields for Organic Molecules". JACS 147(21), 17598–17611 (2025). DOI 10.1021/jacs.4c07099. arXiv 2312.15211.
- **Where the numbers come from:**
  - The version-of-record SI on pubs.acs.org returned HTTP 403 (`logs/get_paper.log`) and was not read.
  - Every published number below comes from **Table S1** of the Supporting Information inside **arXiv v5** (2025-08-22): SI p. 5, MAE block, rows "E (meV/at)" and "Ftotal (meV/Å)". The same values appear in arXiv v1 Table III and v3 Table IV.
  - Test-set counts come from Table 1 of the v5 main text (same in v1, v3 and v4).
- **Weights:** https://github.com/ACEsuit/mace-off @ `91a78c5a9c300d1104700d9352c8bfe449227737` (2025-01-29), files `mace_off23/MACE-OFF23_{small,medium,large}.model`.
  - These files only changed by renames since 2024-04-04.
  - Not used: `MACE-OFF23b_medium.model` and `MACE-OFF24_medium.model`.
- **Test data:** `test_large_neut_all.tar.gz` from Cambridge Apollo, DOI 10.17863/CAM.107498, no login, downloaded 2026-11-09.
  - Bitstream MD5 `bf1f7c7ff1714e6ac6af2cdc642a130a`, which matches the MD5 the repository publishes.
  - xyz SHA-256 `c65a7fcf9140fb127ccc6cc7fce243ab5052665a8741516cde143592a319745e`.
- **Licences:**
  - **The MACE-OFF23 weights are under the Academic Software License (ASL): academic, non-commercial use only.** Filipe Tessaro accepted the ASL on 2026-11-08; the agent accepted nothing.
  - The predictions in `runs/` come from ASL weights and carry the same non-commercial restriction.
  - The Apollo dataset is MIT.
- **Target:** energy MAE (meV/atom) and force MAE (meV/Å) of MACE-OFF23 S, M and L on each subset of the SPICE test set, Table S1.
  - The released file has 7 of the 8 subsets. Tripeptides (898 configs) is missing, so there are 42 claims instead of 48.
- **Verdict, by the pre-registered rule: Partially reproduced (36 of 42 claims inside).**
  - All 6 misses are PubChem, for all 3 models and both metrics.
  - The other 6 subsets reproduce within the printed rounding for all three models.
- **What explains the 6 misses** (extra analysis; it does not change the verdict):
  - The released PubChem set has 209 more configs than the paper counts.
  - 126 of them have reference forces above 15 eV/Å or a net force above 0.1 eV/Å.
  - Dropping those 126 puts all 6 PubChem numbers inside their bands. The medium model's force RMSE then goes from 115.5 to 40.66 meV/Å (published 40.51), and its energy RMSE becomes 2.0202 meV/atom (published 2.02).
- **Date:** 2026-11-09.
- **Hardware:** Ryzen 9 3900X, RTX 2070 SUPER 8 GB, WSL2 Ubuntu. GPU memory capped at 50%, 6 threads, nice 19.

## Results

### Pre-registration

`claims.json` was frozen before any model ran on the test data.
- SHA-256 `7e025a82c2c772e63b1c8504e2d2748319b93f0380902d8ff55289c620fc7cf5`, frozen at 2026-11-09T04:00:09Z (`claims.frozen_at`, `logs/freeze.log`).
- The file's mtime is 01:00:09 local time (UTC−3). The first evaluation log is from 01:02 local and the first prediction chunk from 01:04 local.
- The hash still matched after all runs (`logs/final_checks.log`: `claims.json: OK`), and every analysis log ends with the same hash.

Fixed beforehand:
- **Energy:** mean over the subset's configs of |E_model − E_ref| / N_atoms. Total energies; the model applies its own E0s.
- **Force:** mean of |ΔF| over every Cartesian component of every atom in the subset, pooled. This is MACE's `mae_f`, and aseMolec, which the SI names, also flattens.
- **Precision:** float64.
- **Data:** every config in the released file, no filter.
- **Band:** published ± max(0.01, 1% of published).
- **Verdict rule:** Reproduced at ≥38 of 42, Partially at 21–37, Not reproduced below 21.

### Claim table (primary: all configs in the released file)

Source: `logs/analyse_final.log` and `runs/results.json`.

| Model | Subset (n) | Metric | Published | Ours | Band | Inside |
|---|---|---|---|---|---|---|
| S | PubChem (34093) | E meV/atom | 1.41 | 1.4309 | [1.3959, 1.4241] | **no** |
| S | PubChem | F meV/Å | 35.68 | 36.7961 | [35.3232, 36.0368] | **no** |
| S | DES370K Monomers (889) | E | 1.04 | 1.0369 | [1.0296, 1.0504] | yes |
| S | DES370K Monomers | F | 17.63 | 17.6342 | [17.4537, 17.8063] | yes |
| S | DES370K Dimers (13908) | E | 0.98 | 0.9799 | [0.97, 0.99] | yes |
| S | DES370K Dimers | F | 16.31 | 16.3418 | [16.1469, 16.4731] | yes |
| S | Dipeptides (1025) | E | 0.84 | 0.8370 | [0.83, 0.85] | yes |
| S | Dipeptides | F | 25.07 | 25.0691 | [24.8193, 25.3207] | yes |
| S | Solvated Amino Acids (52) | E | 1.60 | 1.5967 | [1.584, 1.616] | yes |
| S | Solvated Amino Acids | F | 38.56 | 38.5578 | [38.1744, 38.9456] | yes |
| S | Water (84) | E | 1.67 | 1.6700 | [1.6533, 1.6867] | yes |
| S | Water | F | 28.53 | 28.5281 | [28.2447, 28.8153] | yes |
| S | QMugs (144) | E | 1.03 | 1.0268 | [1.0197, 1.0403] | yes |
| S | QMugs | F | 41.45 | 41.4476 | [41.0355, 41.8645] | yes |
| M | PubChem | E | 0.91 | 0.9243 | [0.90, 0.92] | **no** |
| M | PubChem | F | 20.57 | 21.6463 | [20.3643, 20.7757] | **no** |
| M | DES370K Monomers | E | 0.63 | 0.6275 | [0.62, 0.64] | yes |
| M | DES370K Monomers | F | 9.36 | 9.3563 | [9.2664, 9.4536] | yes |
| M | DES370K Dimers | E | 0.58 | 0.5789 | [0.57, 0.59] | yes |
| M | DES370K Dimers | F | 9.02 | 9.0475 | [8.9298, 9.1102] | yes |
| M | Dipeptides | E | 0.52 | 0.5208 | [0.51, 0.53] | yes |
| M | Dipeptides | F | 14.27 | 14.2659 | [14.1273, 14.4127] | yes |
| M | Solvated Amino Acids | E | 1.21 | 1.2092 | [1.1979, 1.2221] | yes |
| M | Solvated Amino Acids | F | 23.26 | 23.2647 | [23.0274, 23.4926] | yes |
| M | Water | E | 0.76 | 0.7592 | [0.75, 0.77] | yes |
| M | Water | F | 15.27 | 15.2651 | [15.1173, 15.4227] | yes |
| M | QMugs | E | 0.69 | 0.6872 | [0.68, 0.70] | yes |
| M | QMugs | F | 23.58 | 23.5813 | [23.3442, 23.8158] | yes |
| L | PubChem | E | 0.88 | 0.9122 | [0.87, 0.89] | **no** |
| L | PubChem | F | 14.75 | 15.8180 | [14.6025, 14.8975] | **no** |
| L | DES370K Monomers | E | 0.59 | 0.5900 | [0.58, 0.60] | yes |
| L | DES370K Monomers | F | 6.58 | 6.5755 | [6.5142, 6.6458] | yes |
| L | DES370K Dimers | E | 0.54 | 0.5454 | [0.53, 0.55] | yes |
| L | DES370K Dimers | F | 6.62 | 6.6480 | [6.5538, 6.6862] | yes |
| L | Dipeptides | E | 0.42 | 0.4154 | [0.41, 0.43] | yes |
| L | Dipeptides | F | 10.19 | 10.1943 | [10.0881, 10.2919] | yes |
| L | Solvated Amino Acids | E | 0.98 | 0.9836 | [0.97, 0.99] | yes |
| L | Solvated Amino Acids | F | 19.43 | 19.4349 | [19.2357, 19.6243] | yes |
| L | Water | E | 0.83 | 0.8267 | [0.82, 0.84] | yes |
| L | Water | F | 13.57 | 13.5684 | [13.4343, 13.7057] | yes |
| L | QMugs | E | 0.45 | 0.4479 | [0.44, 0.46] | yes |
| L | QMugs | F | 16.93 | 16.9317 | [16.7607, 17.0993] | yes |

36 of 42 are inside.
- **Subsets whose count matches Table 1** (Monomers, Dipeptides, Solvated Amino Acids, Water, QMugs): all 30 values round to the published number, with a largest gap of 0.0046.
- **DES370K Dimers** (12 configs more than Table 1): ours are 0.003 to 0.03 above the published values, and all 6 claims are inside.

### Set composition (counted before any model ran)

`scripts/count_configs.py`, `logs/count_configs.log`:

| Subset | Table 1 # Test | Released file | Difference |
|---|---|---|---|
| PubChem | 33884 | 34093 | +209 |
| DES370K Monomers | 889 | 889 | 0 |
| DES370K Dimers | 13896 | 13908 | +12 |
| Dipeptides | 1025 | 1025 | 0 |
| Solvated Amino Acids | 52 | 52 | 0 |
| Water | 84 | 84 | 0 |
| QMugs | 144 | 144 | 0 |
| Tripeptides | 898 | absent | −898 |

The decision was written into `claims.json` before any run: evaluate everything in the file, report the filter as an extra analysis, and leave Tripeptides out. The same count gap is raised in mace-off issue #7 (2025-11-10, unanswered). We read that issue before freezing, and our own count reaches the same numbers independently.

### Extra analyses (pre-registered as A1–A4; they do not change the verdict)

**A1, force filter.** This drops any config whose reference forces have an atom above 15 eV/Å or a net force above 0.1 eV/Å (the SPICE-2 filters of SI S1).
- It removes only 126 PubChem configs: 121 by the force limit and 5 by the net-force limit (`logs/filter_breakdown.log`).
- The largest reference force in each removed config has a median of 20.98 eV/Å and a maximum of 55.56 eV/Å.
- No other subset loses a config. PubChem goes from 34093 to 33967, still 83 above Table 1.

| Model | PubChem, after A1 | Published | Band | Inside |
|---|---|---|---|---|
| S | E 1.4125 / F 35.7316 | 1.41 / 35.68 | [1.3959, 1.4241] / [35.3232, 36.0368] | yes / yes |
| M | E 0.9099 / F 20.6118 | 0.91 / 20.57 | [0.90, 0.92] / [20.3643, 20.7757] | yes / yes |
| L | E 0.8884 / F 14.7869 | 0.88 / 14.75 | [0.87, 0.89] / [14.6025, 14.8975] | yes / yes |

With A1, all 42 claims are inside. The PubChem RMSE rows of Table S1, which we did not claim, show the same thing:
- **Force RMSE after A1:** 62.02, 40.66 and 33.49 meV/Å for S, M and L, against 61.83, 40.51 and 33.34 published. Without the filter: 124.9, 115.5 and 113.0.
- **Energy RMSE after A1:** 2.7453, 2.0202 and 2.5162, against 2.74, 2.02 and 2.48 published.

So the PubChem column of Table S1 was almost certainly computed without those high-force configs, and the released file still has them.

**A2, force error as the norm of the per-atom vector.** It comes out about 2× the published value on every subset (for example, M Dipeptides 28.56 against 14.27). The paper's definition is per component.

**A4, mean of the per-config force MAEs instead of pooling.** It differs from the pooled value only on Water: S 21.09, M 10.85 and L 9.96, against 28.53, 15.27 and 13.57 published. The pooled value matches, so the paper pools.

**A3, the `MACE_energy` and `MACE_forces` columns already in the test file.** They are not the output of any of the three released models.
- The mean per-component force difference is 8.53 meV/Å against our large model, 18.21 against medium and 31.63 against small.
- Their own errors (PubChem 0.835 meV/atom and 17.59 meV/Å) match no row of Table S1.
- They probably come from an earlier or intermediate model. Nothing in the file or on the Apollo page says which.

## What it took

Commands in order. All of them are in `scripts/` and `env/`, and each writes to `logs/`.

1. **Paper.**
   - `scripts/get_paper.sh` downloaded arXiv v5 and tried the ACS SI page, which returned 403.
   - `scripts/get_paper2.sh` downloaded v1, v3 and v4 and ran `pdftotext -layout`. The PDF SHA-256s are in `logs/get_paper2.log`.
2. **Repo, data page and issues.** `scripts/get_repo.sh` ran `git clone https://github.com/ACEsuit/mace-off.git repo`, fetched the Apollo landing page and queried the GitHub issues API.
   - Issue #7 is about the counts. Issues #1–#3 are about training scripts and do not affect evaluation.
   - Model SHA-256s are in `logs/model_sha256.log`: small `165cce4c…`, medium `4842c52a…`, large `a29e397d…`.
3. **Definition check.** We cloned https://github.com/imagdau/aseMolec @ `6da9a4ca` into `ref/aseMolec`. `pltProps.py` flattens the force arrays, which means per component.
4. **Test data.** `scripts/get_test.sh` downloads from the Apollo REST bitstream URL (`…/bitstreams/cb8351dd-f09c-413f-921c-67a702a7f0c5/content`) and checks the MD5 against the one the repository publishes.
   - TLS stayed on.
   - The 1.6 GB training set was not downloaded.
5. **Counting.** `python -I scripts/count_configs.py data/test/x/test_large_neut_all.xyz` (stdlib only).
6. **Environment.** `env/setup_env.sh` with uv 0.13.4 and Python 3.10.22.
   - Resolved with `--exclude-newer 2024-03-01`, because the models date from late 2023 or early 2024.
   - Versions: mace-torch 0.3.4, torch 2.2.0+cu121, e3nn 0.4.4, ase 3.22.1, numpy 1.26.4.
   - The uv cache and uv's Python install are in `env/uv-cache` and `env/uv-python`.
   - Files: `env/requirements.in`, `env/requirements.lock`, `env/requirements.freeze.txt`.
7. **Freeze.** `scripts/freeze.sh` runs `scripts/make_claims.py`, then `sha256sum`.
8. **Evaluation.** `scripts/run_eval.sh <model> <max_atoms_per_batch>` runs `nice -n 19 /usr/bin/time -v python -I scripts/evaluate.py` with `OMP_NUM_THREADS=6`.
   - Default dtype float64 and `model.double()`. GPU memory capped with `torch.cuda.set_per_process_memory_fraction(0.5)`.
   - Graphs are built with MACE's `AtomicData.from_config` at the model's `r_max`: 4.5 Å for S, 5.0 for M and L, as in Table 2.
   - It writes one `.npz` per 1000 configs, skips chunks that already exist, and writes atomically (temp file plus `os.replace`).
   - On a RuntimeError containing "out of memory", it splits the batch in half.
9. **Analysis.** `scripts/run_analyse.sh small,medium,large final` runs `scripts/analyse.py`.
   - It parses the reference values straight from the xyz text.
   - It asserts that the chunks cover indices 0..50194 exactly once, with the right atom count per config.

**Incidents** (all in `logs/`):
- **Small, attempt 1** (batches of 3000 atoms) ran out of memory.
  - The split also failed: it happened inside the `except` block, where the traceback still held the GPU tensors.
  - It exited with no chunk written (`eval_small_attempt1_oom.log`).
- **Small, attempt 2** started with the old code before the fix was saved. It was killed with no chunk written (`eval_small_attempt2_killed_oldcode.log`).
  - Fix: leave the `except` block before splitting.
- **Small, final run:** batches of 1000, no OOM, 12 min 08 s, GPU peak 1.59 GB.
- **Medium:** started with batches of 1000. There were 5 OOMs and the split worked. We stopped it before any chunk was written and restarted at 500 (marked in the log). 55 min 31 s, GPU peak 2.35 GB.
- **Large:** started at 250. There were 3 OOMs and the split worked. We stopped it before any chunk was written and restarted at 120. 3 h 56 min 58 s, GPU peak 3.42 GB.
- Every saved chunk comes from one uninterrupted pass. `analyse.py` checks for gaps and duplicates.
- The folder takes 5.7 GB. No stray folders at the WSL root (`logs/final_checks.log`).

## Notes for the authors

1. **The PubChem test set released on Apollo includes configs that Table S1 seems to exclude.**
   - The file has 34093 PubChem configs; Table 1 says 33884.
   - 126 of them have reference forces above 15 eV/Å (up to 55.6) or a net force above 0.1 eV/Å.
   - With them, our PubChem MAEs are 1.4–7% above Table S1 for all three models, and the force RMSE is about 3× higher.
   - Without them, all six PubChem MAEs and the PubChem RMSEs fall within 1% of Table S1.

   Could you confirm which configs Table S1 used, and publish the indices or a filtered file? This is the same gap raised in mace-off issue #7.
2. **After that filter, 83 PubChem configs and 12 DES370K Dimers configs are still unexplained.** They do not move our numbers beyond the published rounding, but the list of the 33884 + 13896 configs would settle it.
3. **The Tripeptides test set (898 configs) is not in the release,** so the last column of Table S1 cannot be checked.
4. **The `MACE_energy` and `MACE_forces` columns in the test file come from none of the released MACE-OFF23 models.** Even against the large model the mean force difference is 8.5 meV/Å. A line on the Apollo page saying which model produced them would stop people from taking them as the paper's predictions.
5. **Error definitions.** Table S1 does not say whether the force MAE is per component or per atom vector, and the two differ by a factor of 2. Our numbers show it is per component, pooled over the subset. One sentence in S2 would settle this.
6. **Small things.**
   - The SI on pubs.acs.org returned 403 to a plain download, so we used the arXiv v5 SI.
   - The `.tar.gz` carries a macOS `._` file, which is harmless.

## How this report was made

This blind reproduction was run by an AI agent (Claude, by Anthropic) on a home computer and will be reviewed by a human before anything is published.
- **What it could not see:** the agent had no access to the earlier reproduction of this paper, its folder, the queue or the run log.
- **What it did on its own:**
  - found the target table;
  - chose the definitions and tolerances, and froze them with a SHA-256 before running any model on the test data;
  - built the environment;
  - downloaded the data and weights;
  - ran the three models;
  - wrote this report.
- **Where the numbers come from:** every number here comes from a log or output file in this folder (`logs/`, `runs/results.json`). None was typed by hand.

The method is public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md. Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues

---

**Where things are:** everything is in `E:\Ciencia\noturno\2025-kovacs-maceoff-cego\`:
- the pre-registration: `claims.json`, `claims.json.sha256`, `claims.frozen_at`;
- the code: `scripts\`;
- the environment: `env\` (lockfile included);
- the logs: `logs\`, with the main one at `logs\analyse_final.log`;
- the predictions and results: `runs\{small,medium,large}\chunk_*.npz` and `runs\results.json`;
- the paper PDFs and text: `paper\`;
- the authors' repo: `repo\`;
- the test data: `data\test\`.

Nothing was published or posted, and no licence was accepted.
