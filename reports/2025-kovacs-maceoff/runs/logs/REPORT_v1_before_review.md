# Reproduction report: MACE-OFF: Short-Range Transferable Machine Learning Force Fields for Organic Molecules

- Paper: Kovács, D. P.; Moore, J. H.; Browning, N. J.; Batatia, I.; Horton, J. T.; Pu, Y.; Kapil, V.; Witt, W. C.; Magdău, I.-B.; Cole, D. J.; Csányi, G. *J. Am. Chem. Soc.* **2025**, 147 (21), 17598–17611. DOI: 10.1021/jacs.4c07099. Main text read from the publisher-deposited full text in PubMed Central (PMC12123624) and cross-checked against the peer-reviewed accepted version on Apollo (DOI 10.17863/CAM.117939). The Supporting Information PDF on pubs.acs.org answers HTTP 403 to a plain client and the Apollo accepted version does not carry the SI, so SI Table S1 was read from arXiv:2312.15211v5 (22 Aug 2025), which postdates publication. Both files are in `paper/`.
- Code: https://github.com/ACEsuit/mace-off @ 91a78c5a9c300d1104700d9352c8bfe449227737 (2025-01-29). Weights: `mace_off23/MACE-OFF23_small.model`, `_medium.model`, `_large.model`. Their git blob hashes at that commit match the files we ran (`runs/logs/weights_blob_sha.log`).
- Licence: the weights are under the **Academic Software Licence (ASL): academic, non-commercial use only**. Filipe Tessaro accepted it on 2026-11-08 before the download; this agent accepted nothing. Everything in this folder that derives from the weights carries the same non-commercial restriction. The test data on Apollo is CC BY 4.0.
- Data: `test_large_neut_all.tar.gz` from Cambridge Apollo, DOI 10.17863/CAM.107498 (85,448,756 bytes, md5 `bf1f7c7ff1714e6ac6af2cdc642a130a`), downloaded 2026-11-08 with no login. It extracts to one extxyz file of 50,195 configurations.
- Target: the **MAE block of Supporting Information Table S1** — per-atom energy MAE (meV/atom) and total force MAE (meV/Å) for MACE-OFF23 (S), (M) and (L) on the seven SPICE test subsets. 42 numbers.
  - Not Table 1. Table 1 of the published paper is the summary of the training and test sets and holds no error values; the main text shows the test errors as RMSE bar charts in Figure 1 and points at the SI for the numbers. That correction was made before any model was run and is recorded in `claims.json`.
  - Not checked: the RMSE blocks of Table S1, the relative-error blocks, the intermolecular force errors, the Tripeptide column (its 898 configurations are not in the released archive), MACE-OFF24(M) and Table S2, and everything downstream of the test set.
- Verdict: **Reproduced**
- Date: 2026-11-09
- Hardware: Ryzen 9 3900X, RTX 2070 SUPER 8 GB, WSL2 Ubuntu. Inference in float64 on the GPU at half the card memory, 6 CPU threads, nice 19.

All 42 pre-registered claims fall inside their bands, 36 of them within 0.5% of the published value. On the five subsets whose configuration count matches Table 1, every one of our 30 numbers reproduces the published number to the two printed decimals.

We also found what explains issue #7 of the repository: a maximum reference force cut of **10 eV/Å** on the test set reproduces the Table 1 counts exactly, 33,884 and 13,896, and then reproduces all 42 Table S1 values to the printed digits. That cut is nowhere in the paper.

## Results

**Tolerance.** Fixed in `claims.json` before the first model run: `max(5% of the paper value, 0.02 meV/atom, 0.2 meV/Å)`. PubChem and DES370K Dimers got a wider band, `max(15%, same floors)`, because the released set for those two subsets is larger than the one Table S1 was computed on (+209 and +12 configurations) and an MAE moves with a handful of outliers. The verdict rule, also pre-registered: Reproduced needs at least 38 of 42 inside and nothing off by more than 25%.

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

Source: `runs/logs/compare.log`, per-claim table in `runs/out/claims_result.csv`, per-configuration errors in `runs/out/errors_small.csv`, `errors_medium.csv` and `errors_large.csv`.

The only deviations above 1% are the two subsets whose released set is larger than the paper one: PubChem (+1.5% to +3.7% on energy, +3.1% to +7.2% on force) and DES370K Dimers (at most +1.0%). Every other number sits within 0.5%, and 20 of them agree to all printed digits. The worst deviation over the 42 claims is 7.2%, well inside the 25% ceiling of the verdict rule.

### What explains issue #7: the undocumented 10 eV/Å test cut

Issue #7 reports 221 test configurations more than Table 1 states, 209 in PubChem and 12 in DES370K Dimers, and says the force filters in the paper do not account for them. We counted the released file before pre-registering and got the same numbers.

We swept a maximum reference force cut over the released file (`scripts/filter_probe.py`, `runs/logs/filter_probe.log`):

| cut (eV/Å) | PubChem | DES370K Dimers | other five subsets |
|---|---|---|---|
| Table 1 | 33884 | 13896 | match |
| no cut | 34093 | 13908 | match |
| 15 | 34004 | 13908 | match |
| 12 | 33951 | 13907 | match |
| 11 | 33922 | 13898 | match |
| **10** | **33884** | **13896** | **match** |
| 9.5 | 33848 | 13889 | match |

A cut of 10 eV/Å lands on both published counts exactly and leaves the other five subsets untouched. With that cut our numbers become:

| Subset | 23S E / F | 23M E / F | 23L E / F | paper 23S | paper 23M | paper 23L |
|---|---|---|---|---|---|---|
| PubChem | 1.410 / 35.678 | 0.908 / 20.569 | 0.882 / 14.745 | 1.41 / 35.68 | 0.91 / 20.57 | 0.88 / 14.75 |
| DES370K Dimers | 0.979 / 16.305 | 0.578 / 9.022 | 0.545 / 6.623 | 0.98 / 16.31 | 0.58 / 9.02 | 0.54 / 6.62 |

All 42 values then round to the published ones. So Table S1 was computed on a test set filtered at 10 eV/Å on the DFT force magnitude, and the released file is the unfiltered one. The SI describes a 2 eV/Å maximum force *error* cut on the *training* set (808 configurations) and, for SPICE version 2 only, cuts of 15 eV/Å and 0.1 eV/Å. Nothing about 10 eV/Å on the test set. This is an alternative reading, found after the run, so it does not carry the verdict; the pre-registered primary passes on its own.

### Stored MACE columns in the released file

The released test file also carries `MACE_energy` and `MACE_forces` per configuration. Scored against the DFT reference the same way (`scripts/stored_mace_columns.py`), they give PubChem 0.835 meV/atom and 17.592 meV/Å, DES370K Dimers 0.524 and 7.350, Dipeptides 0.449 and 11.369. That is a lower energy error than any released model and a higher force error than 23L, so those columns are not the output of 23S, 23M or 23L. They look like the screening model the SI mentions, and nothing in the archive says what wrote them.

## What it took

1. **The target was not where the task said it was.** Table 1 of the published paper is the dataset summary; the SPICE test errors live in Figure 1 as RMSE and in SI Table S1 as MAE and RMSE. We confirmed this in three places: the PMC full text, the Apollo accepted manuscript, and arXiv v5. The pre-registration states the correction and the exact table it targets.
2. **The published SI is not reachable.** `pubs.acs.org` answers 403 to curl for both the article and the SI PDF, and the Apollo accepted version stops at the references. We used the arXiv v5 SI, whose main text matches the published Table 1 number for number, and we say so in the pre-registration rather than claiming to have read the ACS file.
3. **Repository.** A full `git clone` stalled twice on this connection. The three weight files are plain git blobs, so we fetched them from `raw.githubusercontent.com` at the pinned commit and verified each git blob SHA-1 against the GitHub API listing for that commit. Byte-identical.
4. **Environment.** The repo pins nothing and only says to install the MACE code. We built a Python 3.10 venv with uv, resolved from PyPI with `--exclude-newer 2025-01-29`, the date of the pinned commit: mace-torch 0.3.9, ase 3.23.0, numpy 1.26.4, e3nn 0.4.4, scipy 1.15.1, matscipy 1.1.1. `mace-torch 0.3.10` was published 2025-02-04 and the date filter refused it, which is the filter doing its job. torch 2.5.1+cu121 came from the PyTorch CUDA index, installed separately because that index carries no upload dates. Files: `env/requirements.in`, `env/requirements.freeze.txt`, `env/setup_env.sh`. Log: `runs/logs/setup_env.log`.
   - A first torch install was interrupted and left `torch` as an empty namespace package that imported without error and had no version attribute. Reinstalling with `--reinstall-package torch` fixed it.
5. **Scoring.** `scripts/evaluate.py` builds each configuration with the MACE package own `mace.data.AtomicData.from_config` at the cutoff stored in the model, runs the model with `compute_force=True`, and writes one row per configuration: absolute energy error per atom, the sum of absolute force component errors, the sum of force vector norms, and the reference force diagnostics. `scripts/compare.py` aggregates by `config_type` and checks each claim against its band. Energy MAE is the mean over configurations of `|E_pred - E_ref| / N_atoms`; force MAE is the mean over all atoms and all three Cartesian components, the `mae_f` of the mace codebase. Both definitions were fixed in `claims.json` before running, and a partial run on the small model confirmed them before the full runs started.
   - ASE moves the energy and forces of an extxyz frame into a `SinglePointCalculator` and drops them from `info` and `arrays`. The first run crashed reading them from `info`; the script now reads from whichever place they landed in.
6. **The large model and half an 8 GB card.** MACE-OFF23(L) in float64 at `set_per_process_memory_fraction(0.5)` ran out of memory twice, once at batch size 8 and once at batch size 2. The second time the retry path failed too: a TorchScript module wraps a CUDA OOM in a plain `RuntimeError`, so `except torch.cuda.OutOfMemoryError` never fired. The script now catches `RuntimeError` and tests the message, splits the batch, falls back to the CPU for a single configuration that will not fit, empties the cache every 2000 configurations, and runs with `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`. It also resumes: the large run picked up at configuration 18,507 instead of starting over, which saved about three hours. After the fix no configuration needed the CPU fallback and no OOM occurred. Logs of both failed attempts are kept: `runs/logs/eval_large_oom_attempt1.log` and `eval_large_oom_attempt2.log`.
7. **Runtime and resources** (from `/usr/bin/time -v`).
   - Download of the test archive: 85 MB, under a minute. Weights: 81 MB.
   - 23S: 14 min 40 s, peak RSS 1.35 GB. 23M: 1 h 01 min, 1.35 GB. 23L: 2 h 46 min of compute after the resume, about 5 h of wall clock including the two failed attempts, 1.37 GB.
   - float64 is what makes the large model slow: the GPU sat at 96% utilisation, and FP64 on a 2070 SUPER runs at a thirty-second of FP32. We kept float64 anyway, because the energies are around 10^4 eV and the errors around 10^-3 eV, a relative 10^-7 that float32 cannot hold.
   - The folder takes 6.2 GB: env 5.7 GB, data 331 MB, weights 78 MB, paper 14 MB, runs 18 MB. The limit was 30 GB.

## Alternative readings

These never change the verdict.

- **The 10 eV/Å cut**, above. It is the strongest explanation of issue #7 we can offer, and it was found after the run, so it is reported here and goes to the authors as a question, not as a correction to our own numbers.
- **The SPICE version 2 filters.** Pre-registered as A2: dropping configurations whose reference forces have a maximum magnitude above 15 eV/Å or a net force above 0.1 eV/Å removes 94 PubChem configurations and none from DES370K Dimers, and gives PubChem 1.414 / 35.797 (23S), 0.911 / 20.669 (23M) and 0.891 / 14.845 (23L). Closer than the unfiltered set, still not the published value. Those filters belong to MACE-OFF24, as the SI says, and they are not the cut that was used here.
- **Force MAE as a vector norm.** Pre-registered as A1: averaging the Euclidean norm of the force error per atom instead of the component-wise mean gives almost exactly twice our numbers on every subset, for example PubChem 23L 31.646 against 15.818. The published values match the component-wise definition, so that is the one Table S1 uses.
- **The wide band for PubChem and DES370K Dimers.** It was fixed before running, on the ground that those two subsets hold more configurations than the paper ones. It turned out to be needed only for PubChem force (up to 7.2%), and the 10 eV/Å reading shows the whole gap is the extra configurations and not model drift. Under the narrow 5% band, 40 of 42 claims still pass.
- **Tripeptides.** The Table S1 column exists (23S 1.05 / 32.88, 23M 0.57 / 18.74, 23L 0.38 / 13.20) and we cannot touch it: the 898 recomputed COMP6 tripeptide configurations are in neither of the two Apollo files. Dropped from the pre-registration rather than guessed at.

## Notes for the authors

Thanks for releasing the three checkpoints and the test file. With both in hand the whole MAE table checks out on a home GPU in a few hours, and it checks out. A few things we ran into:

1. **The test set the table was computed on is not the test set you released.** The released `test_large_neut_all.xyz` holds 34,093 PubChem and 13,908 DES370K Dimers configurations, against 33,884 and 13,896 in Table 1 (this is issue #7). A maximum DFT force cut of 10 eV/Å lands on both published counts exactly, leaves the other five subsets untouched, and then reproduces every value of Table S1 to the printed digits, for all three models. Is that the cut you used? The SI mentions 2 eV/Å on the maximum force *error* for the training set, and 15 eV/Å plus 0.1 eV/Å for SPICE version 2, but nothing about the test set of version 1. One sentence in the SI, or the filtered file beside the unfiltered one, would close the issue.
2. **The tripeptide test set is not in the archive.** Table 1 lists 898 tripeptide test configurations and Table S1 reports errors for them, but neither Apollo file contains them. They are the only column of Table S1 nobody outside the group can check.
3. **`MACE_energy` and `MACE_forces` in the released test file.** Scored against the DFT reference they give PubChem 0.835 meV/atom and 17.592 meV/Å, which is a smaller energy error than MACE-OFF23(L) and a larger force error, so they are not the output of any released checkpoint. We take them to be the screening model of SI S1. A line saying what wrote them would stop someone reading them as the predictions of the paper.
4. **Where the MAE table lives.** The main text reports RMSE in Figure 1 and the MAE numbers only in SI Table S1. Anyone asked to check the energy and force MAE in the paper looks at Table 1 first and finds the dataset summary. A pointer in the Figure 1 caption would help.
5. **No pinned versions.** The repository says to install the MACE code and nothing else. mace-torch 0.3.9 with torch 2.5.1 loads all three checkpoints and reproduces the table; the full lockfile is in `env/` if it helps.
6. **The large model needs float64 and more than 4 GB.** MACE-OFF23(L) in float64 will not score a 150-atom water cluster inside 4 GB of VRAM at batch size 2. float32 is not an option for the energy MAE, since the relative precision needed is about 10^-7. A note on the expected memory would save people the OOM.

## How this report was made

This reproduction was run by an AI agent (Claude, by Anthropic) on a home computer and will be reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

The claims, definitions and tolerances were pre-registered in `claims.json` and frozen at 2026-11-08T21:26:03Z, SHA-256 `a57a3de75759ea377cfbdda2e8ba4e8a999dade90794740d002932de9b4853b7` (`claims.json.sha256`), before the first model run. The hash still matched after the runs (`runs/logs/claims_hash_check.log`). The pre-registration records the correction from Table 1 to SI Table S1, the counts we found in the released file, our reading of issue #7, the metric definitions, the bands and the verdict rule, and the three alternative readings. None of it was touched afterwards.

The agent then built the environment, downloaded the data and the weights, ran the three models over the whole released test set, compared the results with the published table, and wrote this report.

**The blind recount is still owed.** Our method requires an independent agent, in its own folder, to redo the download, the environment, the scoring and its own pre-registration without seeing this report, its scripts or its pre-registration, before anything is published or sent to the authors. That has not happened yet for this paper. Until it does, this report is a draft: the verdict stands on one run, and the 10 eV/Å finding in particular should be confirmed by someone who has not seen it before it reaches the authors.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues
