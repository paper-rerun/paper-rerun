# Reproduction report: MACE-OFF: Short-Range Transferable Machine Learning Force Fields for Organic Molecules

- Paper: Kovács, D. P.; Moore, J. H.; Browning, N. J.; Batatia, I.; Horton, J. T.; Pu, Y.; Kapil, V.; Witt, W. C.; Magdău, I.-B.; Cole, D. J.; Csányi, G. *J. Am. Chem. Soc.* **2025**, 147 (21), 17598–17611. DOI: 10.1021/jacs.4c07099. Main text read from the publisher-deposited full text in PubMed Central (PMC12123624) and cross-checked against the peer-reviewed accepted version on Apollo (DOI 10.17863/CAM.117939).
- Supporting Information: the version-of-record SI is listed in PMC (`ja4c07099_si_001.pdf`, 853,967 bytes) but sits behind a browser check we did not pass, and pubs.acs.org answers 403. We read Table S1 from arXiv:2312.15211v5 (22 Aug 2025) and **have not confirmed it is identical to the published SI**. arXiv v4 carries no SI. Table 1 agrees across arXiv v4, v5 and PMC.
- Code: https://github.com/ACEsuit/mace-off @ 91a78c5a9c300d1104700d9352c8bfe449227737 (2025-01-29). Weights: `mace_off23/MACE-OFF23_small.model`, `_medium.model`, `_large.model`. Their git blob hashes at that commit match the files we ran (`runs/logs/weights_blob_sha.log`).
- Licence: Filipe Tessaro accepted the ASL on 2026-11-08; the agent downloaded the weights on his instruction under that acceptance and accepted no licence of its own. The weights are not redistributed with this report; outputs derived from them are for academic non-commercial use only. The test data on Apollo is under the MIT licence (the record's `dc.rights` field). We wrote to Gábor Csányi before publishing to ask whether releasing the report and the scripts, without the weights and without the raw predictions, was acceptable to him. He answered on 2026-11-16: "I'm happy for you to publish your results." This report is published under that permission and keeps the weights and the per-configuration predictions out of the repository.
- Data: `test_large_neut_all.tar.gz` from Cambridge Apollo, DOI 10.17863/CAM.107498 (85,448,756 bytes, md5 `bf1f7c7ff1714e6ac6af2cdc642a130a`), downloaded 2026-11-08 with no login. It extracts to one extxyz file of 50,195 configurations.
- Target: the **MAE block of Supporting Information Table S1**: per-atom energy MAE (meV/atom) and total force MAE (meV/Å) for MACE-OFF23 (S), (M) and (L) on the seven SPICE test subsets. 42 numbers.
  - Not Table 1. Table 1 of the published paper is the summary of the training and test sets and holds no error values; the main text shows the test errors as RMSE bar charts in Figure 1 and points at the SI. That correction was made before any model was run and is recorded in `claims.json`.
  - Not checked: the RMSE blocks of Table S1, the relative-error blocks, the intermolecular force errors, the Tripeptide column (its 898 configurations are not in the test archive), MACE-OFF24(M) and Table S2, and everything downstream of the test set.
- Verdict: **Reproduced** under our pre-registered band. The blind recount, with a tighter band, says **Partially reproduced (36 of 42)**; both runs get the same 42 numbers, and all 6 claims it fails are PubChem (section "Independent blind rerun").
- Date: 2026-11-09
- Hardware: Ryzen 9 3900X, RTX 2070 SUPER 8 GB, WSL2 Ubuntu. Inference in float64 on the GPU at half the card memory, 6 CPU threads, nice 19.

All 42 pre-registered claims fall inside their pre-registered bands. Under the 5% band applied to every subset, 40 of 42 pass. The two that need the wider band are PubChem force for 23M (+5.2%) and 23L (+7.2%), and they were given that band because we already knew from issue #7 that the released PubChem set is larger than the one in the paper, so those two passes are not independent agreement.

34 of the 42 values are within 0.5% of the published value, and 32 of 42 round to it. All 30 values on the five subsets whose configuration count matches Table 1 round to the published value. Outside PubChem and DES370K Dimers every value is within 0.5% except 23L Dipeptides energy (0.4154 against 0.42, −1.1%), which still rounds to 0.42.

We also found a cut that is consistent with issue #7: removing configurations whose **largest absolute Cartesian force component** (max over atoms and x, y, z) exceeds 10 eV/Å reproduces the Table 1 counts exactly, 33,884 and 13,896, and then all 42 Table S1 values round to the published ones. The paper does not mention that cut.

## Results

**Tolerance.** Fixed in `claims.json` before the first model run: `max(5% of the paper value, 0.02 meV/atom, 0.2 meV/Å)`. PubChem and DES370K Dimers got a wider band, `max(15%, same floors)`, because issue #7 had already shown that the released set for those two subsets is larger than the one Table S1 was computed on (+209 and +12 configurations). The verdict rule, also pre-registered: Reproduced needs at least 38 of 42 inside and nothing off by more than 25%.

### Energy MAE, meV/atom

| Subset | n | 23S paper | 23S ours | 23M paper | 23M ours | 23L paper | 23L ours |
|---|---|---|---|---|---|---|---|
| PubChem | 34093 | 1.41 | 1.431 | 0.91 | 0.924 | 0.88 | 0.912 |
| DES370K Monomers | 889 | 1.04 | 1.037 | 0.63 | 0.627 | 0.59 | 0.590 |
| DES370K Dimers | 13908 | 0.98 | 0.980 | 0.58 | 0.579 | 0.54 | 0.545 |
| Dipeptides | 1025 | 0.84 | 0.837 | 0.52 | 0.521 | 0.42 | 0.415 |
| Solvated Amino Acids | 52 | 1.60 | 1.597 | 1.21 | 1.209 | 0.98 | 0.984 |
| Water | 84 | 1.67 | 1.670 | 0.76 | 0.759 | 0.83 | 0.827 |
| QMugs | 144 | 1.03 | 1.027 | 0.69 | 0.687 | 0.45 | 0.448 |

### Force MAE, meV/Å

| Subset | n | 23S paper | 23S ours | 23M paper | 23M ours | 23L paper | 23L ours |
|---|---|---|---|---|---|---|---|
| PubChem | 34093 | 35.68 | 36.796 | 20.57 | 21.646 | 14.75 | 15.818 |
| DES370K Monomers | 889 | 17.63 | 17.634 | 9.36 | 9.356 | 6.58 | 6.576 |
| DES370K Dimers | 13908 | 16.31 | 16.342 | 9.02 | 9.047 | 6.62 | 6.648 |
| Dipeptides | 1025 | 25.07 | 25.069 | 14.27 | 14.266 | 10.19 | 10.194 |
| Solvated Amino Acids | 52 | 38.56 | 38.558 | 23.26 | 23.265 | 19.43 | 19.435 |
| Water | 84 | 28.53 | 28.528 | 15.27 | 15.265 | 13.57 | 13.568 |
| QMugs | 144 | 41.45 | 41.448 | 23.58 | 23.581 | 16.93 | 16.932 |

Source: `runs/logs/compare.log` and `runs/logs/revise_checks.log` (values to four decimals), per-claim table in `runs/out/claims_result.csv`, per-configuration errors in `runs/out/errors_small.csv`, `errors_medium.csv` and `errors_large.csv`. The 23L Monomers force value is 6.5755; `compare.log` prints it as 6.575 because it rounds to four decimals and then prints three.

Deviations above 0.5% (`revise_checks.log`): energy PubChem +1.49%, +1.57%, +3.66%; force PubChem +3.13%, +5.23%, +7.24%; 23L DES370K Dimers energy +1.00%; 23L Dipeptides energy −1.10%. The worst over the 42 claims is 7.2%, inside the 25% ceiling of the verdict rule.

### A cut consistent with issue #7

Issue #7 reports 221 test configurations more than Table 1 states, 209 in PubChem and 12 in DES370K Dimers. We counted the released file before pre-registering and got the same numbers.

The per-configuration CSVs keep `ref_max_abs_f_eV_A`, which is `np.abs(f_ref).max()`: the largest absolute Cartesian component of the DFT forces, over all atoms and x, y, z. It is not the per-atom force norm. Sweeping a cut on it (`scripts/filter_probe.py`, `runs/logs/filter_probe.log`):

| cut on largest component (eV/Å) | PubChem | DES370K Dimers | other five subsets |
|---|---|---|---|
| Table 1 | 33884 | 13896 | — |
| no cut | 34093 | 13908 | unchanged |
| 15 | 34004 | 13908 | unchanged |
| 12 | 33951 | 13907 | unchanged |
| 11 | 33922 | 13898 | unchanged |
| **10** | **33884** | **13896** | **unchanged** |
| 9.5 | 33848 | 13889 | unchanged |

In those two subsets the largest kept component is 9.9970 eV/Å and the smallest removed one is 10.0023 eV/Å, so any cut in [9.997, 10.002) gives both published counts (`runs/logs/revise_checks.log`). With the cut at 10:

| Subset | 23S E / F | 23M E / F | 23L E / F | paper 23S | paper 23M | paper 23L |
|---|---|---|---|---|---|---|
| PubChem | 1.4104 / 35.6775 | 0.9079 / 20.5687 | 0.8825 / 14.7453 | 1.41 / 35.68 | 0.91 / 20.57 | 0.88 / 14.75 |
| DES370K Dimers | 0.9785 / 16.3055 | 0.5781 / 9.0220 | 0.5447 / 6.6230 | 0.98 / 16.31 | 0.58 / 9.02 | 0.54 / 6.62 |

All 42 values then round to the published ones.

A cut on the per-atom force norm does not do the same. At 10 eV/Å it keeps 33,722 PubChem, 13,884 Dimers and 1,023 Dipeptides configurations and 31 of 42 values round to the published ones. A per-atom norm cut at 11.6265 eV/Å, a non-round value, also hits both counts, but the kept set differs from the component cut in 56 configurations and three PubChem force values miss: 35.65, 20.55 and 14.72 against 35.68, 20.57 and 14.75. So the component cut at 10 is the one consistent with Table S1.

The SI describes a 2 eV/Å cut on the maximum force *error* on the training set and, for SPICE version 2 only, cuts of 15 eV/Å and 0.1 eV/Å. It says nothing about a 10 eV/Å cut on the test set. This reading was found after the run, so it does not carry the verdict; the pre-registered primary passes on its own. The blind recount did not test it (section above).

### Stored MACE columns in the released file

The released test file also carries `MACE_energy` and `MACE_forces` per configuration. Scored against the DFT reference the same way (`scripts/stored_mace_columns.py`, `runs/logs/stored_mace_columns.log`), they give PubChem 0.835 meV/atom and 17.592 meV/Å, DES370K Dimers 0.524 and 7.350, Dipeptides 0.449 and 11.369. That is a lower energy error than 23L and a higher force error, so those columns are not the output of 23S, 23M or 23L. `MACE-OFF23b_medium.model`, also in the repository, was not tested. Nothing in the archive says what wrote them.

### Per-snapshot split (issue #7, point 3)

`claims.json` promised to report this, unscored. Issue #7 says every hydrogen-mapped SMILES of the test set also appears in the training set, which would mean the split was by snapshot and not by molecule as Section 2.2 says. We did not download the training archive, so we cannot check the overlap. On the test side alone (`runs/logs/revise_checks.log`), the 34,093 PubChem configurations hold 12,931 distinct SMILES, DES370K Dimers 13,908 and 1,877, Dipeptides 1,025 and 389. Several conformers per molecule in the test set is compatible with either kind of split. The question stays open, and it does not touch the claims checked here.

## Independent blind rerun

A second agent redid the work in a separate folder (published here as `blind/`) without access to this folder, this report or our pre-registration. It found Table S1 on its own, wrote and froze its own `claims.json` (SHA-256 `7e025a82c2c772e63b1c8504e2d2748319b93f0380902d8ff55289c620fc7cf5`, 2026-11-09T04:00:09Z) before any model ran, built an older stack (mace-torch 0.3.4, torch 2.2.0, resolved with `--exclude-newer 2024-03-01`, against our 0.3.9 and 2.5.1), downloaded the same test file (same md5) and wrote its own scoring code. It read issue #7 before freezing, as we did.

**The numbers agree.** All 42 of its values match ours to every digit either report prints, for example PubChem force 36.7961 / 21.6463 / 15.8180 (S/M/L) here and there.

**The verdict does not, and the difference is the band.** It pre-registered published ± max(0.01, 1%) for every claim, with Reproduced at 38 of 42 or more. Under that band 36 of 42 pass, so its verdict is Partially reproduced. The 6 misses are the PubChem energy and force values of all three models, 1.4% to 7.2% above the table. Our band was 5% everywhere and 15% on PubChem and DES370K Dimers, widened because we already knew from issue #7 that those two released subsets are larger than the ones in the paper. Both readings are honest. What they say together: on the five subsets whose size matches Table 1 the table reproduces to the printed digit, and the PubChem column was computed on a set that is not the released one.

**What it found about the extra configurations.** It applied the SPICE version 2 filters with the per-atom force norm (drop a configuration if any atom exceeds 15 eV/Å or the net force exceeds 0.1 eV/Å). That removes 126 PubChem configurations, the number in issue #7, and gives 1.4125 / 35.7316, 0.9099 / 20.6118 and 0.8884 / 14.7869, the same values as our own check of that filter. Under its 1% band all six fall inside, and the PubChem force RMSE drops from 124.9 / 115.5 / 113.0 to 62.02 / 40.66 / 33.49 meV/Å against 61.83 / 40.51 / 33.34 published. It leaves 83 PubChem and 12 Dimers configurations unexplained.

**The 10 eV/Å component cut was not found independently.** The blind run did not try it. Its filter explains most of the gap but does not reproduce the counts and leaves the PubChem values a little off the printed digit (for example 35.73 against 35.68); our component cut at 10 eV/Å gives both counts exactly and rounds to every published value. So the cut remains a finding of this run alone, consistent with the blind run's numbers but not confirmed by it, and it goes to the authors as a question, not as a result.

It also agrees with us on three side points, each found on its own:
- the force MAE is per Cartesian component, pooled over the subset (the per-atom norm gives about twice the value);
- the `MACE_energy` and `MACE_forces` columns of the test file come from none of the three released models (PubChem 0.835 meV/atom and 17.59 meV/Å, the same as ours);
- the Tripeptides set is not in the release.

One finding it had and we did not: averaging the force MAE per configuration instead of pooling changes only the Water subset (S 21.09 against 28.53 published), so the table pools.

## What it took

1. **The target was not where the task said it was.** Table 1 of the published paper is the dataset summary; the SPICE test errors live in Figure 1 as RMSE and in SI Table S1 as MAE and RMSE. We confirmed this in the PMC full text, the Apollo accepted manuscript and arXiv v5. The pre-registration states the correction and the exact table it targets.
2. **The published SI.** pubs.acs.org answers 403 to curl, the Apollo accepted version stops at the references, and the PMC copy of the SI sits behind a browser check. We used the arXiv v5 SI and say so in the pre-registration. Whether its Table S1 is identical to the version of record is not checked.
3. **Repository.** A full `git clone` stalled twice on this connection. The three weight files are plain git blobs, so we fetched them from `raw.githubusercontent.com` at the pinned commit and verified each git blob SHA-1 against the GitHub API listing for that commit. Byte-identical.
4. **Environment.** The repo pins nothing and only says to install the MACE code. We built a Python 3.10 venv with uv, resolved from PyPI with `--exclude-newer 2025-01-29`, the date of the pinned commit: mace-torch 0.3.9, ase 3.23.0, numpy 1.26.4, e3nn 0.4.4, scipy 1.15.1, matscipy 1.1.1. `mace-torch 0.3.10` was published 2025-02-04 and the date filter refused it. torch 2.5.1+cu121 came from the PyTorch CUDA index, installed separately because that index carries no upload dates. Files: `env/requirements.in`, `env/requirements.freeze.txt`, `env/setup_env.sh`. Log: `runs/logs/setup_env.log`.
   - A first torch install was interrupted and left `torch` as an empty namespace package that imported without error and had no version attribute. Reinstalling with `--reinstall-package torch` fixed it.
5. **Scoring.** `scripts/evaluate.py` builds each configuration with the MACE package own `mace.data.AtomicData.from_config` at the cutoff stored in the model, runs the model with `compute_force=True`, and writes one row per configuration. `scripts/compare.py` aggregates by `config_type` and checks each claim against its band. Energy MAE is the mean over configurations of `|E_pred - E_ref| / N_atoms`; force MAE is the mean over all atoms and all three Cartesian components, the `mae_f` of the mace codebase. Both were fixed in `claims.json` before running, and a partial run on the small model confirmed them before the full runs.
   - ASE moves the energy and forces of an extxyz frame into a `SinglePointCalculator` and drops them from `info` and `arrays`. The first run crashed reading them from `info`; the script now reads from whichever place they landed in.
6. **The large model and half an 8 GB card.** MACE-OFF23(L) in float64 at `set_per_process_memory_fraction(0.5)` ran out of memory twice, once at batch size 8 and once at batch size 2. The second time the retry path failed too: a TorchScript module wraps a CUDA OOM in a plain `RuntimeError`, so `except torch.cuda.OutOfMemoryError` never fired. The script now catches `RuntimeError` and tests the message, splits the batch, falls back to the CPU for a single configuration that will not fit, empties the cache every 2000 configurations, and runs with `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`. It also resumes: the large run picked up at configuration 18,507, the 150-atom water cluster that had failed, and scored it on the GPU at the same memory fraction. No configuration needed the CPU fallback (`runs/logs/eval_large.log`), so the failures were fragmentation, not capacity. Logs of both failed attempts: `runs/logs/eval_large_oom_attempt1.log` and `eval_large_oom_attempt2.log`.
7. **Runtime and resources** (from `/usr/bin/time -v`).
   - 23S: 14 min 40 s, peak RSS 1.35 GB. 23M: 1 h 01 min, 1.35 GB. 23L: 2 h 46 min after the resume; 4 h 33 min of wall clock including the two failed attempts (2 min 01 s and 1 h 44 min 50 s), 1.37 GB.
   - The folder takes 6.2 GB: env 5.7 GB, data 331 MB, weights 78 MB, paper 14 MB, runs 18 MB. The limit was 30 GB.

## Alternative readings

These never change the verdict.

- **The 10 eV/Å component cut**, above. Found after the run, so reported here and sent to the authors as a question.
- **The SPICE version 2 filters.** Pre-registered as A2. `compare.py` applied them to the largest reference force component: dropping configurations whose largest component exceeds 15 eV/Å or whose net force exceeds 0.1 eV/Å removes 94 PubChem configurations and none from DES370K Dimers, and gives PubChem 1.4141 / 35.7968 (23S), 0.9113 / 20.6693 (23M), 0.8909 / 14.8453 (23L). With the per-atom norm, as in issue #7, the same filters remove 126 PubChem configurations, the issue number, and give 1.4125 / 35.7316, 0.9099 / 20.6118, 0.8884 / 14.7869 (`runs/logs/revise_checks.log`). Neither reaches the published values. Of those 126, 121 are among the 209 the component cut at 10 removes; the other 88 removed configurations pass the version 2 filters (`runs/logs/revise_checks2.log`).
- **Force MAE as a vector norm.** Pre-registered as A1: averaging the Euclidean norm of the force error per atom gives about twice our numbers on every subset, for example PubChem 23L 31.646 against 15.818. The published values match the component-wise definition.
- **The 5% band everywhere.** 40 of 42 pass; the two that fail are the PubChem force values of 23M and 23L, the ones the wide band was designed to absorb.
- **Tripeptides.** The Table S1 column exists (23S 1.05 / 32.88, 23M 0.57 / 18.74, 23L 0.38 / 13.20) and we cannot touch it: the 898 tripeptide configurations are not in the test archive. Dropped from the pre-registration rather than guessed at.

## Notes for the authors

Thanks for releasing the three checkpoints and the test file. With both in hand the MAE table can be checked on a home GPU in a few hours, and it checks out. A few things we ran into:

1. **The test set the table was computed on seems not to be the released test file.** The released `test_large_neut_all.xyz` holds 34,093 PubChem and 13,908 DES370K Dimers configurations, against 33,884 and 13,896 in Table 1 (issue #7). Removing configurations whose largest absolute Cartesian DFT force component (max over atoms and x, y, z) exceeds 10 eV/Å gives both published counts exactly, leaves the other five subsets untouched, and then every value of Table S1 rounds to the published one for all three models. The same cut on the per-atom force norm gives 33,722 and 13,884 instead. Is that the cut you used? On the counts in issue #7: the 126 there come from the per-atom norm with the version 2 filters; the same filters on the largest component remove 94. One sentence in the SI, or the filtered file beside the unfiltered one, would close the issue.
2. **The tripeptide test set is not in the test archive.** Table 1 lists 898 tripeptide test configurations and Table S1 reports errors for them, but `test_large_neut_all.tar.gz` does not contain them (the paper uses them for testing only; we did not open the training archive). They are the only column of Table S1 nobody outside the group can check.
3. **`MACE_energy` and `MACE_forces` in the released test file.** Scored against the DFT reference they give PubChem 0.835 meV/atom and 17.592 meV/Å, a smaller energy error than MACE-OFF23(L) and a larger force error, so they are not the output of 23S, 23M or 23L (we did not test 23b_medium). A line saying what wrote them would stop someone reading them as the predictions of the paper.
4. **Pinned versions.** mace-torch 0.3.9 with torch 2.5.1 loads all three checkpoints and reproduces the table; our lockfile is in `env/` if it helps.

## Adversarial review

A second agent reviewed the first draft of this report (`REVIEW.md`, scratch in `review_scratch/`). It recomputed all 42 MAEs from the per-configuration CSVs and found them equal to `compare.log`, checked the hash and the order in time (freeze before the weight download and before the first model run), confirmed the splice of the resumed large run is clean (indices 0 to 50,194, no gaps or duplicates), and ran a CPU spot check through a different code path (`MACECalculator`) that agrees with the GPU rows to within 1e-12 eV/atom. Its verdict: sound with corrections. What it found, and what changed in this version:

- the 10 eV/Å cut was described as a cut on the force magnitude; it is on the largest Cartesian component, and the norm version does not reproduce the table;
- the A2 alternative used the component column while issue #7 uses the per-atom norm (94 against 126); both are now reported;
- three counts in the summary were wrong or not in any log (36 within 0.5% is 34; "20 agree to all printed digits" was unsupported; 23L Dipeptides energy is −1.1%); every count now comes from `runs/logs/revise_checks.log`, which this agent ran itself;
- the summary now says that two passes depend on the wide band and why that band was chosen;
- the version-of-record SI exists in PMC and was not compared with arXiv v5;
- the claim that the stored MACE columns come from a screening model was unsupported and is gone;
- the note to the authors about memory was contradicted by the logs and is gone;
- the licence line was reworded;
- smaller fixes: the 6.575/6.576 rounding, four decimals in the cut table, the wall clock, two unlogged figures removed, and the per-snapshot split question that `claims.json` promised to report.

The verdict did not change.

## How this report was made

This reproduction was run by an AI agent (Claude, by Anthropic) on a home computer and will be reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

The claims, definitions and tolerances were pre-registered in `claims.json` and frozen before the first model run, SHA-256 `a57a3de75759ea377cfbdda2e8ba4e8a999dade90794740d002932de9b4853b7` (`claims.json.sha256`). The hash was written at 2026-11-08T21:26:03Z (`claims.frozen_at.txt`); the `frozen_at` field inside `claims.json` says 21:26:00Z because it was typed before hashing. The hash still matched after the runs (`runs/logs/claims_hash_check.log`). The pre-registration records the correction from Table 1 to SI Table S1, the counts we found in the released file, our reading of issue #7, the metric definitions, the bands, the verdict rule and the alternative readings. None of it was touched afterwards.

The agent then built the environment, downloaded the data and the weights, ran the three models over the whole released test set, compared the results with the published table and wrote the first draft. A second agent reviewed it as described above, and the first agent revised it, recomputing on the CPU every number it quotes.

A blind recount by a third agent, which saw none of this, got the same 42 numbers (section above). Its tighter band gives Partially reproduced, and it did not test the 10 eV/Å cut, so that finding rests on this run alone.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues
