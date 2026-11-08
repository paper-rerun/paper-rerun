# Reproduction report: SELFormer: molecular representation learning via SELFIES language models

- Paper: Yüksel, A., Ulusoy, E., Ünlü, A., Doğan, T. Machine Learning: Science and Technology 4, 025035 (2023), published 29 June 2023. DOI: 10.1088/2632-2153/acdb30. Numbers were read from the published MLST PDF (`sources/mlst_acdb30.pdf`). arXiv v2 (`sources/arxiv_2304.04662v2.pdf`) is kept alongside it.
- **Table numbers differ between the two versions.** The classification results on scaffold splits are **Table 3** in MLST and Table 5 in arXiv v2; the regression results on scaffold splits are **Table 5** in MLST and Table 7 in arXiv v2. The SELFormer values are identical in both (`runs/logs/read_tables.log`). Our triage note had used the arXiv numbering.
- Code: https://github.com/HUBioDataLab/SELFormer @ 4969ca14dc403ccb6c478ad83e719c0f6bc35d22 (2026-05-06). Licence GPLv3, stated in the README; there is no LICENSE file in the repo. Our `scripts/evaluate_*.py` adapt the authors' code, so they are GPLv3 too. `train_classification_model.py` and `prepare_finetuning_data.py` are byte-identical to commit 8ae5618 (2023-06-17), the last commit before publication (29 June 2023), and to today's HEAD, so the split and the metric are the published ones.
- Weights: `classification_models.zip`, 3 231 394 364 bytes (3.0 GiB), sha256 `4a9bed3e23ccb410f43ba0e3003264b162ee315f56d978a926875e572672bb69`, from the Drive folder the README links (file id `14jLOvTQxzJfkhpY1j9OAzT1qgv8v8CFd`). Plain HTTPS, no Google account. It holds 114 entries, uncompressing to 3 491 196 013 bytes across four model folders: BACE, BBBP, SIDER, Tox21.
- Data: the MoleculeNet CSVs shipped in the repo under `data/finetuning_datasets/classification/`.
- Target: MLST Table 3, scaffold split, ROC AUC.
  - Primary: BBBP 0.902 (C1).
  - Secondary: BACE 0.832 (C2), HIV 0.681 (C3), Tox21 0.653 (C4), SIDER 0.745 (C5).
  - Finding without a run: how the regression RMSE of MLST Table 5 is computed (C6).
  - Not done: nothing was fine-tuned, the random-split tables were not touched, and `regression_models.zip` (4.8 GB) was not downloaded.
- Verdict: **Partially reproduced** — the primary claim (BBBP) lands inside the pre-registered band but not on the printed digits; of the four secondary claims with published weights, three fall outside their bands and the fifth has no model to score.
- Date: 2026-11-08
- Hardware: Ryzen 9 3900X, WSL2 Ubuntu 24.04. CPU for every number in the tables, 6 threads at nice 19. One GPU run on the RTX 2070 SUPER as a device check.

The primary claim lands at 0.8913 against 0.902, inside the band fixed before the runs but not a match to the printed digits. The three secondary tasks with published weights all fall below the table, BACE by 0.12. HIV has no published fine-tuned model, so its number cannot be checked at all.

The split and the metric are not in doubt. On both binary tasks our pipeline reproduces, to float precision, the validation ROC AUC the authors' own TensorBoard logs recorded at the end of their fine-tuning run — logs that ship inside the model folders. Whatever produced Table 3, it is not these checkpoints scored by this code on this split.

## Results

**Tolerance.** Fixed before any run, in `claims.json` (frozen at 2026-11-08T17:37:42Z, `claims.sha256`, verified unchanged afterwards in `runs/logs/claims_hash_check.log`). The paper prints three decimals. A display match means our value rounds or truncates to the printed one, |d| < 0.001. A 0.02 band was allowed on top of that, and only because we rebuild the split ourselves. The metric is (sensitivity + specificity)/2, so on the BBBP test split (155 positives, 50 negatives) one negative molecule moving between splits is worth 0.01 of AUC and one positive 0.0032. The band is about two negative molecules. Inside the band but outside the display band counts as partially reproduced, by the rule written down before we ran.

### Primary and secondary

| Claim | Task | Paper | Ours | Interval | Result |
|---|---|---|---|---|---|
| C1 ROC AUC, scaffold test | BBBP | 0.902 | 0.8913 | [0.882, 0.922] | inside band, no display match |
| C2 ROC AUC, scaffold test | BACE | 0.832 | 0.7104 | [0.812, 0.852] | outside band |
| C3 ROC AUC, scaffold test | HIV | 0.681 | — | — | no published model |
| C4 ROC AUC, scaffold test | Tox21 | 0.653 | 0.6131 | [0.633, 0.673] | outside band |
| C5 ROC AUC, scaffold test | SIDER | 0.745 | 0.7180 | [0.725, 0.765] | outside band |

Source: `runs/logs/compare.log`. Per-molecule predictions and the full metric set are in `runs/out/<task>_test.csv` and `.json`.

**The metric is the authors' own.** `train_classification_model.py` computes `roc_auc_score(y_true=test_y, y_score=np.argmax(raw_pred, axis=1))`, that is the ROC AUC of the hard 0/1 prediction, not of a score. With binary input there is a single operating point, so the value is (sensitivity + specificity)/2, which is balanced accuracy, not the area under a curve. The column above uses exactly that, because it is what produced the published table. Scored the standard way, with the class-1 probability, the same test sets give BBBP 0.9295, BACE 0.7628, Tox21 about 0.741 and SIDER about 0.779. On three of the four tasks the printed value sits between our two readings; on BACE it sits above both.

The two binary tasks are exact. The multi-label probability figures are given to three decimals because they depend on the precision the scores are kept at: our run and the blind rerun below agree to 16 digits on the hard-label metric, but differ by 0.002 on SIDER's probability variant, because one run's stored scores saturate in float32 (2,382 of 3,888 cells tie) and the other's do not. Ties cost AUC. Nothing about the verdict depends on this.

### The splits are the authors' splits

| Task | Our train/val/test | Total | Paper Table 1 |
|---|---|---|---|
| BBBP | 1631 / 203 / 205 | 2039 | 2039 |
| BACE | 1210 / 151 / 152 | 1513 | 1513 |
| SIDER | 1141 / 142 / 144 | 1427 | 1427 |
| Tox21 | 6264 / 783 / 784 | 7831 | 7831 |

Every total matches the paper's compound count. No test molecule was lost to SELFIES conversion on any of the four tasks; one molecule is lost on the BBBP validation split, as the authors' pipeline would also lose it.

### The check that settles the pipeline

The published model folders for BBBP and BACE still contain the TensorBoard event files from the authors' fine-tuning on 2023-03-12. They hold a per-epoch `eval/roc-auc` on the validation split, computed by the same metric. We read them with a dependency-free reader (`scripts/read_tfevents.py`) and scored the same validation split ourselves:

| Task | Metric | Authors' log (float32) | Ours (float64) | float32(ours) == log |
|---|---|---|---|---|
| BBBP | eval/roc-auc | 0.7842336297035217 | 0.7842336057404823 | yes |
| BBBP | eval/accuracy | 0.8762376308441162 | 0.8762376237623762 | yes |
| BBBP | eval/f1 | 0.9266862273216248 | 0.9266862170087976 | yes |
| BACE | eval/roc-auc | 0.7907446622848511 | 0.7907446434843696 | yes |
| BACE | eval/accuracy | 0.7947019934654236 | 0.7947019867549668 | yes |
| BACE | eval/f1 | 0.7596899271011353 | 0.7596899224806201 | yes |

Three metrics per task, each equal to the stored float32 bit for bit, at the last logged step (10200 for BBBP, 1900 for BACE), which is the step of the shipped checkpoint. `eval/prc-auc` agrees to six decimals. The two paths do not read each other: the scoring script opens nothing under `runs/`, and the log reader opens nothing under `runs/out/`.

Strictly, this pins the *validation* split. `scaffold_split` builds all three partitions in one deterministic call, so the same validation set implies the same train and test sets. With that, the rebuilt split, the SELFIES conversion, the tokenizer, the forward pass and the metric all match the run that produced these weights.

Two further checks:

- **The shipped weights are the last epoch.** The folder root and the final checkpoint hold the same bytes: sha256 `5074048a7449ff7a…` for both BBBP files and `0d0c1eaef4cfc5ad…` for both BACE files. With `save_total_limit=1` and `load_best_model_at_end` commented out, there is no better-scoring checkpoint in the download, and the last logged eval step (10200 and 1900) is the step those weights come from.
- **The chemprop version does not move the split.** The paper-era requirements file pinned chemprop 1.4.1 and the current one pins 1.5.2. In `chemprop/data/scaffold.py` the only change is an `assert` becoming a `raise ValueError` (`runs/logs/diff_chemprop_scaffold.log`). `chemprop/rdkit.py` and `make_mols` are byte-identical between the two releases, and `chemprop/data/data.py`, which did change, does not change how a plain SMILES becomes a mol. So the scaffold grouping is the same code. We did not install 1.4.1 and rerun the split: the pre-registration made that check conditional on the split differing, and nothing indicates it does.

### Independent blind rerun

The paper was then reproduced a second time, from scratch, by an agent that was not allowed to see this report, its scripts, its pre-registration or its review. It was given the paper, the authors' repository address and the five published numbers, nothing else. It downloaded the archive again, built its own environment, wrote its own evaluation code from the authors' training scripts and froze its own pre-registration (`claims.sha256` `11c9f4eb…bbbc5`, 2026-11-08T19:10:46Z). Its folder is `noturno/2023-yuksel-selformer-cego`.

| Task | This run | Blind rerun |
|---|---|---|
| BBBP | 0.8913 | 0.8913 |
| BACE | 0.7104 | 0.7104 |
| Tox21 | 0.6131 | 0.6131 |
| SIDER | 0.718012171633844 | 0.718012171633844 |

The archive hash matched (`4a9bed3e…2bb69`), the four model folders and the missing HIV model matched, and the split sizes matched. The blind run reached the same conclusion about the metric being balanced accuracy, and it reproduced the authors' recorded validation metrics to 16 digits as well, by reading `trainer_state.json` rather than the TensorBoard files.

It added three things this run had not done:

- **The README command fails on line 200**, after training, on four scikit-learn versions including the authors' pinned one. See note 7 to the authors.
- **The best model was never saved.** BACE's `trainer_state.json` has its best validation at 0.8396 in epoch 53, while the shipped weights are epoch 100 with validation 0.7907. If the table reported the test score of the best epoch, that number is not recoverable from the download. This is not proof: 0.832 does not appear anywhere in BACE's validation history, nor 0.902 in BBBP's, so the table is not simply a validation score either.
- **No threshold saves SIDER.** Sweeping the multi-label threshold from 0.05 to 0.95, SIDER's best is 0.718 against the published 0.745. Tox21 reaches 0.656 only at 0.05, and the authors' own `model_args.json` says 0.5.

It also recovered the per-task fine-tuning hyperparameters from `training_args.bin` and `model_args.json`, which the paper gives only for pre-training and for SIDER: BACE 5e-5 / batch 32 per device / 100 epochs, BBBP 1e-5 / 16 / 200, Tox21 5e-5 / 8 / 25, SIDER 5e-5 / 8 / 200.

One difference between the two runs: the probability-variant AUC for SIDER, 0.7801 here against 0.7781 blind. The stored scores differ by up to 0.003 because one set saturates in float32, which creates ties. The frozen metric, the one that decides the verdict, is identical to 16 digits.

### Validation peaks, for context

From the same authors' logs: BBBP validation ROC AUC peaks at 0.804365 over 200 evaluations and ends at 0.784234; BACE peaks at 0.839568 over 100 and ends at 0.790745 (`runs/logs/tfevents_summary.log`). The BBBP table value of 0.902 is above every validation value the authors' own run ever recorded. The BACE table value of 0.832 is close to that task's validation peak.

### Device check

The BBBP test split on the GPU, half the card, batch 16, gives 0.8912903225806452 and a probability AUC of 0.929483870967742, the same as CPU (`runs/logs/eval_bbbp_test_gpu.log`). The logits themselves are not identical: 171 of 205 differ in `logit0` and 174 in `logit1`, by at most 1.2e-4. No prediction flips and no rank changes, so both AUCs are unmoved. Every number in the tables above was produced on CPU.

### C6: the regression RMSE

No run, a reading of `train_regression_model.py` lines 126 to 130. With `--scaler=2`, the value in the README's single regression example command, the code does:

```python
train_df["target"] = StandardScaler().fit_transform(...)
validation_df["target"] = StandardScaler().fit_transform(...)
test_df["target"] = StandardScaler().fit_transform(...)
```

A separate scaler is fitted on each split, the test split included, and nothing is inverted before the RMSE is printed. Read literally, that RMSE would be in units of the test split's own standard deviation. The published values look like they are not: 0.682, 2.797, 0.735 and 1.488 are 0.33, 0.73, 0.61 and 0.86 of each dataset's raw target standard deviation, and FreeSolv 2.797 sits next to D-MPNN's 2.082 kcal/mol. In units of standard deviation, FreeSolv would mean an error of 2.8 standard deviations, almost three times worse than predicting the test mean. So Table 5 is probably in the properties' own units and came from a different path than this flag. It goes to the authors as a question. We did not change this and we did not rerun it; the regression weights were not downloaded.

## What it took

1. **Repo.** `git clone` works, 330 MB. Nothing exotic.
2. **Weights.** The README's Drive folder holds two archives, listed with plain `curl` from the folder page: `classification_models.zip` (3.0 G) and `regression_models.zip` (4.8 G). Only the first was downloaded, with the confirm token the share page returns — no account, no terms accepted. It unpacks to four model folders, 3.3 GB. **There is no HIV model in it**, though HIV is one of the five columns of Table 3.
3. **Environment.** Two versions of the pin file exist. The paper-era `data/requirements.yml` (commit 8ae5618, June 2023) is a full conda freeze: python 3.8.12, pytorch 1.10.1, transformers 4.15.0, datasets 1.18.3, simpletransformers 0.63.6, chemprop 1.4.1, numpy 1.21.2, pandas 1.3.4. The current file (rewritten in 4969ca1, May 2026) pins python 3.10, pytorch 1.13.1, transformers 4.26.1, datasets 2.9.0, chemprop 1.5.2, simpletransformers 0.63.9. **We followed the current file**, plus rdkit 2023.3.1 and torch 2.0.1, with uv resolving the rest under `--exclude-newer 2023-06-29`. So our stack is newer than the one that produced the published weights, on python, torch, transformers, datasets, simpletransformers and chemprop.
   - **Why that does not sink the result:** under this stack our validation run reproduces the authors' own March 2023 logs bit for bit on three metrics per task (see above). Whatever the version drift costs, it costs nothing on these forward passes.
   - Files: `env/requirements.in`, `env/requirements.lock`, `env/requirements.freeze.txt`, `env/setup_env.sh`. Log: `runs/logs/setup_env.log`.
   - The verification line of `setup_env.sh` first used `simpletransformers.__version__`, which that package does not define; it now reads the version from package metadata. The failure was in the check, not in the install.
4. **Scoring.** `scripts/evaluate_binary.py` and `scripts/evaluate_multilabel.py` are the test blocks of `train_classification_model.py` and `train_classification_multilabel_model.py` with the training removed. They import `prepare_finetuning_data` from the repo unchanged, so the split, the shuffle, the `fillna(0)` and the SELFIES conversion are the authors' code. What differs: the binary script runs a plain torch loop instead of `transformers.Trainer`, since nothing is trained and padding is fixed at `max_length=128`, so batching cannot move a logit; and it coerces the label column with `pd.to_numeric`. That second change is not cosmetic — see note 7 to the authors. For the multi-label tasks we also set `eval_batch_size=32` and `silent=True` (the shipped `model_args.json` has 8 and false); `max_seq_length=128` and `threshold=0.5` come from the authors' saved args, and simpletransformers pads to `max_seq_length`, so the batch size cannot move a logit there either. `scripts/compare.py` checks each claim against its interval. The copy of `evaluate_binary.py` on disk is not literally the file that produced the four CPU numbers: after those runs we added the GPU memory cap for the device check. The prints and the JSON keys of the earlier logs match the current file.
5. **Runtime and resources** (`/usr/bin/time -v`, in the logs).
   - BBBP 1 min 04 s, peak RSS 1.19 GB. BACE 0 min 56 s, 1.19 GB. SIDER 1 min 25 s, 1.29 GB. Tox21 1 min 54 s, 1.37 GB.
   - The 3.0 GiB download took 1 min 49 s at 28 MB/s; the environment install about 25 minutes, most of it writing torch and the CUDA wheels onto the project drive.
   - Everything ran at nice 19 with 6 threads. The folder holds 11.6 GB: `env` 5.0 GB, `data` 3.3 GB, `dl` 3.1 GB, `repo` 330 MB.

## Alternative readings

These do not change the verdict.

- **The probability AUC.** Reading the metric the standard way puts BBBP at 0.9295, above the printed 0.902, and still leaves BACE at 0.7628, well below 0.832. No single consistent choice of metric reproduces all four columns.
- **Rounding.** No rounding convention closes a 0.12 gap on BACE, so the question only matters for BBBP, where 0.8913 does not round or truncate to 0.902 either way.
- **A different split instance.** If the authors had produced Table 3 from a run whose scaffold split differed from ours, their validation AUC would differ from ours too. It does not, on either binary task, to seven decimals. So the table was not produced by this checkpoint on a different split either.
- **Multi-label averaging.** For Tox21 and SIDER the authors' code flattens the whole label matrix before scoring, so the reported value is a micro average over label cells. We kept that. A macro average over labels is a different number and was not computed.
- **Numbers that look like neighbours.** Three cheap readings we noticed but did not test. BACE's Table 3 value (0.832) is close to its random-split value in Table 4 (0.836) and to its own validation peak (0.839568); BBBP has no such neighbour, since its random split gives 0.863 and its validation peak 0.804365. SIDER is printed as 0.745 in both Table 3 and Table 4, which may be a three-decimal coincidence. And the README trains BBBP with `--num_epochs=25`, while the published BBBP model logs 200 evaluations and its last step is 10200; the SIDER args also say 200 and Tox21's say 25, so the README command does not rebuild the published model on three of the four tasks.

## Notes for the authors

Thanks for publishing the fine-tuned weights, the datasets and, as it turns out, the TensorBoard logs inside the model folders. Those logs are what let us check our pipeline against your run instead of guessing. A few things we noticed:

1. **ROC AUC is computed from hard predictions.** In `train_classification_model.py` the metric is `roc_auc_score(y_true, np.argmax(raw_pred, axis=1))`. With 0/1 input this is the balanced-accuracy form of AUC, not the usual score-based ROC AUC, which is presumably what the competing methods in Table 3 report. Scoring with the class-1 probability changes the BBBP value from 0.8913 to 0.9295. It would help to state which one Table 3 holds.
2. **The published checkpoints do not give the Table 3 values.** On the rebuilt scaffold test splits we get BBBP 0.8913 against 0.902, BACE 0.7104 against 0.832, Tox21 0.6131 against 0.653 and SIDER 0.7180 against 0.745, using your code and your metric. Our validation numbers match your own logs exactly (0.7842336 against your 0.784234 for BBBP, 0.7907446 against 0.790745 for BACE), so the split and the metric are right. Were the table values produced by a different run, or by a model selected on validation rather than the last epoch? `load_best_model_at_end` and `metric_for_best_model` are commented out in the training script, so the saved model is the final epoch.
3. **No HIV model in the download.** `classification_models.zip` has BACE, BBBP, SIDER and Tox21. HIV is in Table 3 but its fine-tuned model is not published, so that column cannot be checked.
4. **Which scaler produced the Table 5 RMSE?** In `train_regression_model.py`, `--scaler=2` (the value in the README's example command) fits a separate `StandardScaler` on each split, the test split included, and nothing is inverted before the RMSE is printed. Read literally, that RMSE would be in units of the test split's own standard deviation. The published values look like they are not: 0.682, 2.797, 0.735 and 1.488 are 0.33, 0.73, 0.61 and 0.86 of each dataset's raw target standard deviation, and FreeSolv 2.797 sits next to D-MPNN's 2.082 kcal/mol. So Table 5 is probably in the properties' own units and came from a different path. Could you say which scaler setting produced it? We did not download the regression weights and did not rerun this.
5. **Pinned versions moved.** `data/requirements.yml` was rewritten in May 2026: at publication it pinned python 3.8.12, pytorch 1.10.1, transformers 4.15.0 and chemprop 1.4.1, and it now pins python 3.10, pytorch 1.13.1, transformers 4.26.1 and chemprop 1.5.2. Anyone reading the repo today gets the newer stack, as we did. It would help to say in the README which versions produced the published weights and splits.
6. **`simpletransformers` has no `__version__`.** Not your code, just a note for anyone scripting the environment check.
7. **The published scaffold command does not run, and it fails on the line that prints the table's number.** In `train_classification_model.py`, the scaffold branch builds the dataframes with `np.column_stack([test_smiles, test.targets()])`, which makes the `target` column `dtype=object`. Two things then break. `SELFIESTransfomers_Dataset` calls `torch.tensor(labels, dtype=torch.long)` on string labels, which raises `ValueError: too many dimensions 'str'`. And after training completes, line 200, `roc_auc_score(y_true=test_y, y_score=y_pred)`, raises `ValueError: unknown format is not supported`, because `type_of_target` returns `'unknown'` for an object column. We ran the README command end to end to see it: it trains, prints "Training completed", runs prediction on 205 examples and dies at line 200. The same frame raises the same error on scikit-learn 1.0.2, 1.1.3, 1.2.1 (the version the authors pin) and 1.3.2, so this is not version drift: the scaffold branch of this script has never been able to print a test ROC AUC. The random-split branch does not go through `column_stack` and works. The multi-label script is also fine, because it converts with `dtype=np.float32`. So whatever produced the scaffold column of Table 3 differs from this file as published, and that difference may be the same one behind the gap.

## How this report was made

This reproduction was run by an AI agent (Claude, by Anthropic) on a home computer and will be reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

The claims, definitions and tolerances were pre-registered in `claims.json`, frozen at 2026-11-08T17:37:42Z (`claims.sha256`) before any split was rebuilt and before any model was loaded. Its SHA-256 still matched after the runs (`runs/logs/claims_hash_check.log`). The band that decides the verdict, and the rule that an in-band miss is only a partial reproduction, were written there before the first number existed. The time order rests on file times inside this folder, and the hash sits in the folder it protects; from the next reproduction on, the pre-registration and its hash are committed before the run.

Two defects of the pre-registration are worth recording, since the file itself is frozen and was left alone. It lists three files as changed after commit 8ae5618, while the full diff has seven, including the 2026 rewrite of `data/requirements.yml` — that omission is why the environment section first described the current pin file as the authors' own. And it cites a log file that was only created 26 minutes after the freeze; the reading it describes did happen before, but the log did not exist yet. The pre-registration also fixed only how the primary claim decides the verdict, not how the secondary claims aggregate into it. That rule goes into the pre-registration next time.

A single agent then built the environment, downloaded the weights, rebuilt the splits, scored the four published models, read the authors' own training logs, and wrote this report. The checks against those logs, the checkpoint comparison, the chemprop diff and the device comparison were all added after the first result came in, to test explanations for the gap rather than to change the target.

An adversarial review by a second agent (`REVIEW.md`) then checked the hash and the time order, recomputed every number from the output files, re-read the TensorBoard logs with an independent reader, hashed the checkpoints and the archive, and compared the paper-era and current pin files. Its corrections are applied here: the environment section, the archive size, the device check, the commit date, the regression note, the label cast and the verdict line all changed.

A third agent then reproduced the paper blind, as described above: new folder, new download, its own environment, its own scoring code, its own pre-registration, and no access to this report or anything derived from it. Both runs agree. Blind recomputation before publication became a fixed step of our method on this paper's account, and it now applies to every paper, not only the ones whose result contradicts the paper.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues
