# Reproduction report: PeSTo: parameter-free geometric deep learning for accurate prediction of protein binding interfaces

- Paper: Krapp, L. F., Abriata, L. A., Cortés Rodriguez, F., Dal Peraro, M. Nature Communications 14, 2175 (2023). DOI: 10.1038/s41467-023-37701-8. Text read from Europe PMC (PMC10113261). Supplementary Information and Source Data come from the journal's static content server.
- Code: https://github.com/LBM-EPFL/PeSTo @ ba651aa29aaa839d0ee2c458dee90ca1f934d90a (2023-10-04). Weights: `model/save/i_v4_1_2021-09-07_11-21/model_ckpt.pt`, the file `interface_ppi_benchmark.ipynb` loads. Licence: CC BY-NC-SA 4.0. This report and the scripts in this folder carry the same licence.
- Data:
  - PDB-format biological assemblies (`<id>.pdb<N>.gz`) from https://files.wwpdb.org/pub/pdb/data/biounit/PDB/divided/, downloaded 2026-11-08.
  - MaSIF-site predictions from the repo (`masif-site_benchmark/masif_pred_per_res.json`).
  - The 417 ScanNet-benchmark sids and the authors' per-structure values from Source Data (`41467_2023_37701_MOESM6_ESM.xlsx`).
- Target: Fig. 2b.
  - Primary: PeSTo median ROC AUC of 0.92 on the 53 MaSIF-site benchmark items (C1).
  - Secondary: MaSIF-site median of 0.80 on the same items (C2). PeSTo median of 0.93 on the 417 structures shared with ScanNet (C3).
  - Checks of the authors' own data, with no rerun: ScanNet without MSA 0.87 (C4), and "38 out of 53" (C5).
  - Not done: ScanNet, SPPIDER and PSIVER were not run. The other panels of Fig. 2 and Figs. 3 and 4 were not attempted.
- Verdict: **Reproduced**
- Date: 2026-11-08
- Hardware: Ryzen 9 3900X, WSL2 Ubuntu 24.04. CPU only, 6 threads at nice 19 (the RTX 2070 SUPER was not used).

All five pre-registered claims fall inside their intervals, and both coverage rules are met.

On the MaSIF-site set we rebuilt exactly the authors' 53 items, and every PeSTo AUC matches the value saved in the authors' notebook to its printed 3 decimals. On the ScanNet set, 415 of 416 structures match the Source Data to 0.001.

## Results

**Tolerance.** It was fixed before any run, in claims.json. The paper prints two decimals, and our value has to round or truncate to the printed number. Inference is deterministic, so no wider statistical band was allowed.

### Primary and secondary

| Claim | Set | Paper | Ours | Interval | Result |
|---|---|---|---|---|---|
| C1 PeSTo median ROC AUC | MaSIF-site benchmark, 53 items | 0.92 | 0.9247 | [0.915, 0.930) | inside |
| C2 MaSIF-site median ROC AUC | same 53 items | 0.80 | 0.8002 | [0.795, 0.810) | inside |
| C3 PeSTo median ROC AUC | ScanNet set, 416 of 417 sids | 0.93 (SI Table 1: 0.929) | 0.9299 | [0.925, 0.940) | inside |

Source: `runs/logs/compare.log`. Per-item values are in `runs/out/masif_per_item.csv` and `runs/out/scannet_per_sid.csv`.

On the MaSIF set the means are 0.8565 for PeSTo and 0.7853 for MaSIF-site, against 0.86 and 0.79 in the notebook.

### Per structure, MaSIF set

- **Same items.** We rebuilt exactly the authors' 53 items: same keys (PDB id, biounit, chain, model copy), none extra, none missing.
  - The 53 items come from 47 benchmark ids, because 2F4M, 2AYO, 1W1W and 3SJA show up in more than one biounit or model copy, as in the notebook.
  - All 53 items have a residue count equal to the MaSIF-site prediction length, so all of them enter the median, as in the notebook.
- **Same values.** Our PeSTo AUC is within 0.0005 of the authors' saved value for all 53 items (notebook cell 6, 3 decimals). The largest difference is 0.0005, which is the rounding of the printed value. Table: `runs/out/masif_vs_authors.csv`.
- **Missing ids.** 1NCA_N, 1WDW_H, 3O5T_A and 4BKX_B give no item, here and in the notebook. Their biounits have 8192 atoms or more, so the build skips them (`runs/logs/build_masif.log`): 1nca.pdb1-2, 1wdw.pdb1-3, 3o5t.pdb1 and 4bkx.pdb1 (8524 atoms). The same filter also skipped 1i2m.pdb3.

### Per structure, ScanNet set

- **Coverage.** 416 of the 417 sids give an item with a defined AUC. The 396-sid coverage rule is met.
  - The missing sid is 1FSS_A. Today's 1fss.pdb1 has 9482 atoms, so the build skips it (`runs/logs/build_scannet.log`).
- **Agreement.** 415 of 416 sids are within 0.001 of the Source Data `PeSTo_auc` (`runs/out/scannet_vs_source_data.csv`). 410 are identical to floating-point precision (difference below 1e-15), and 5 differ by 1.5e-4 to 6.1e-4.
- **The one exception: 4DX0_A.** We get 0.961, the authors 0.909, a difference of 0.0518.
- **Revisions.** 4DX0 revision 1.2 (2023-12-13) redefined the biological assembly (`pdbx_struct_assembly` and the operator list), after the paper. That is a likely cause of the 4DX0 difference, but we did not prove it. For 1FSS the assembly changed earlier, in revision 1.4 (2021-06-02): biounit 1 now has 9482 atoms, twice the 4741 deposited. The 2024-10 revision of 1FSS touched metadata only. We cannot tell which version the authors downloaded (`runs/logs/rcsb_revisions.log`).
- **Medians on the same 416 sids:** ours 0.9299, Source Data PeSTo 0.9296, Source Data ScanNet-noMSA 0.8703. With the authors' value for 4DX0_A our median becomes 0.9296, equal to the Source Data on the same sids. The rest of the gap to Supplementary Table 1 (0.929) is the missing 1FSS_A. To three decimals we get 0.930 against 0.929.

### Checks of the authors' data

| Claim | Source | Paper | Value | Result |
|---|---|---|---|---|
| C4 ScanNet-noMSA median ROC AUC | Source Data sheet Fig2b-ScanNet, 417 rows | 0.87 | 0.8693 | inside [0.865, 0.880) |
| C5 items where PeSTo beats MaSIF-site, SPPIDER and PSIVER | Source Data sheet Fig2b-comparison, 53 rows | 38 | 38 | exact |

- **Supplementary Table 1.** In the same sheet the PeSTo median is 0.9294 and the ScanNet-with-MSA median is 0.8973, matching Supplementary Table 1 (0.929 and 0.897).
- **Our recount of the 38.** The SPPIDER and PSIVER predictions are in the repo. Scored against our rebuilt labels with the authors' `bc_scoring`, their medians are 0.7345 and 0.6411 (notebook: 0.73 and 0.64), and PeSTo is strictly best of the four methods on 38 of 53 items, the same number as the paper (`scripts/recount_c5.py`, `runs/logs/recount_c5.log`). PeSTo beats MaSIF-site alone on 42 of 53.
- **A side note.** The notebook also holds a ScanNet column for these 53 items, not shown in the paper. Counted with it, PeSTo is best on 33 (cell 11). The paper's 38 is the count over the four methods of the comparison sheet, which is what Fig. 2b shows for this set.

## What it took

1. **Repo.**
   - `git clone` on Windows fails at checkout. 159 files in `pdbs_test/` have ":" in their names (e.g. `AY_2AYO_1_A:0.pdb`). They are outputs of a disabled branch of the notebook (`if False:`).
   - We extracted the tree with `git -c core.protectNTFS=false archive HEAD` and left out `pdbs_test/`.
   - The two `datasets` symlinks in the model folders could not be created on NTFS. Nothing we ran uses them.
2. **Environment.**
   - The repo pins nothing. `requirements.txt` and `pesto.yml` list package names only. The notebook metadata says Python 3.9.12, and the last commit touching the notebook is from 2022-07-12.
   - We built a Python 3.9 venv with uv, resolved from PyPI with `--exclude-newer 2022-07-12`: numpy 1.23.1, pandas 1.4.3, scikit-learn 1.1.1, scipy 1.8.1, gemmi 0.5.5, h5py 3.7.0, openpyxl 3.0.10.
   - torch 1.11.0+cpu (March 2022) came from the official PyTorch CPU index. It was installed separately, because that index has no upload dates and broke the date filter.
   - uv picked Python 3.9.25.
   - Files: `env/requirements.in`, `env/requirements.lock`, `env/requirements.freeze.txt`, `env/setup_env.sh`. Log: `runs/logs/setup_env.log`.
3. **Data.**
   - **The missing h5.** The notebook reads `datasets/contacts_rr5A_64nn_8192.h5`, which is not in the repo (issue #3). The authors build it with `processing/build_dataset.py` from a full rsync of the PDB.
   - **What we downloaded.** Only what the two sets need: every PDB-format biounit of the 50 MaSIF entries (pdb1 to pdbN, until HTTP 404), and pdb1 of the 399 entries behind the 417 ScanNet sids. That is 467 distinct files, 56 MB. There were 478 downloads, because pdb1 of 11 entries was in both lists; the two copies have the same md5.
   - **Checks.** Each file was checked against its Content-Length and fully gunzipped before saving. Manifest with md5: `data/biounits_manifest.tsv`. Log: `runs/logs/download.log`. wwPDB publishes no per-file checksum, so the md5 is ours, kept for the record.
   - **The build.** `scripts/build_subset.py` runs the `__main__` loop of `build_dataset.py` and imports the authors' functions unchanged. What we changed: our file list, CPU instead of CUDA, no DataLoader workers, and sorted order instead of shuffled.
   - **A failed first attempt.** The first MaSIF build failed because some entries were in both download lists and appeared twice in the file list (h5 "name already exists"). The script now removes duplicates from the list. No result comes from that attempt.
4. **Scoring.**
   - `scripts/evaluate.py` is cells 2 to 7 of the notebook, with the device set to CPU. It uses the same checkpoint, the same selection (`select_by_sid`, `select_by_interface_types`), the same labels (column 0, protein) and the same `bc_scoring` AUC. MaSIF-site is scored under the same length condition as in the notebook.
   - For the ScanNet set it keeps biounit 1, model copy 0, one item per sid, as fixed in claims.json. Of 477 selected items, 416 are kept.
   - `scripts/compare.py` checks each claim against its interval.
5. **Runtime and resources** (from `/usr/bin/time -v` in the logs).
   - Download: 10 min 30 s.
   - MaSIF build: 3 min 02 s, peak RSS 1.32 GB. MaSIF scoring: 13 min 48 s, 1.13 GB.
   - ScanNet-set build: 19 min 21 s, 2.30 GB. ScanNet-set scoring: 1 h 00 min 33 s, 2.13 GB.
   - All model work ran at nice 19 with 6 torch/OMP threads. The GPU was not used.
   - The folder takes about 3.5 GB in total (`du`): repo 2.0 GB including .git, env 1.1 GB, data 403 MB (both h5 files included).

## Alternative readings

These never change the verdict.

- **Biounit choice for the ScanNet set.** The repo has no list or code for the 417-structure benchmark. We fixed "biounit 1, model copy 0" before running, and it reproduces the Source Data on 415 of 416 sids. That is strong evidence the authors used the same choice. We did not test other biounits.
- **Rounding of C1.** The authors' rounded per-item values have a median of exactly 0.925, and our unrounded median is 0.9247. "0.92" in the paper is consistent with both rounding and truncation, so this is not a gap.
- **The tolerance rule.** The "round or truncate" rule widens the C1 ceiling from 0.925 to 0.930, and it was written after we had seen the authors' per-item values. The notebook formats with `:.2f`, which rounds. Under rounding alone every claim still passes: 0.9247, 0.8002, 0.9299 and 0.8693. PIPELINE.md asks for a bootstrap band when Source Data exist; we used a narrower fixed band instead, which is stricter, not looser.

## Notes for the authors

Thanks for leaving the weights, the MaSIF-site predictions and the notebook outputs in the repo, and the per-structure values in the Source Data. That made a structure-by-structure check possible, and it matched. A few things we noticed:

1. **Windows checkout.** `pdbs_test/` file names contain ":". This makes `git clone` fail on Windows. Renaming or removing those files would fix it.
2. **Dataset file.** `datasets/contacts_rr5A_64nn_8192.h5` is not in the repo (issue #3). Building only the benchmark subset takes a few minutes from about 56 MB of biounits. A short script or note for that would save people the full PDB rsync.
3. **The ScanNet benchmark.** The 417-structure benchmark has no list or notebook in the repo. The Source Data sheet was enough to rebuild it. Stating "biounit 1, first model copy" in the Methods would remove the guesswork.
4. **Drift in today's PDB files.** Against today's PDB files, 4DX0_A gives 0.961 instead of 0.909; its assembly was redefined in December 2023. 1FSS_A biounit 1 now has 9482 atoms and is dropped by the 8192-atom filter. The medians do not move.
5. **Pinned versions.** No version is pinned in `requirements.txt` or `pesto.yml`. The versions we used are in our lockfile, if that helps.
6. **Small mismatches between code and text.** `build_dataset.py` writes `contacts_rr5A_64nn_8192_wat.h5`, while the notebook reads `contacts_rr5A_64nn_8192.h5`. The Methods describe a limit of 8192 atoms per subunit, but the code drops the whole assembly when it passes 8192 atoms. That filter is what removes 1NCA, 1WDW, 3O5T and 4BKX from the MaSIF-site benchmark. None of this changes the results.

## How this report was made

This reproduction was run by an AI agent (Claude, by Anthropic) on a home computer and will be reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

The claims, definitions and tolerances were pre-registered in claims.json. It was frozen at 2026-11-08T13:10:09Z (claims.sha256), before the first dataset build and the first model run. Its SHA-256 still matched after the runs (`runs/logs/claims_hash_check.log`).

A single agent then did the rest of the work:

- built the environment;
- downloaded the structures;
- rebuilt the dataset;
- ran the model;
- compared the results with the paper;
- wrote this report.

A second agent then reviewed the report adversarially (REVIEW.md). It recomputed every number from the logs and output tables, checked the hash and the order in time, and compared the scripts with the authors' code. It found no change to the verdict. It corrected the count of missing ids (4, not 3), recounted the 38 from the SPPIDER and PSIVER predictions in the repo, removed a note to the authors that pointed at an inconsistency that does not exist, and fixed the PDB revision history of 1FSS and 4DX0. Those corrections are in this version. The order in time rests on file times in this folder; from the next reproduction on, the hash is committed before the run.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues
