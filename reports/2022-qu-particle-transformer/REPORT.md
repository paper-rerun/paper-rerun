# Reproduction report: Particle Transformer for Jet Tagging

- Paper: Huilin Qu, Congqiao Li, Sitian Qian, ICML 2022 (PMLR 162:18281-18292; PMLR assigns no DOI). arXiv DOI: 10.48550/arXiv.2202.03772 (arXiv 2202.03772 v3; its Table 1 is identical to the PMLR version)
- Code: https://github.com/jet-universe/particle_transformer @ 2925bdb249e8ef78560cc2b9b651eda3615da8c7. Model and inference code come from weaver-core 0.4.17 (git 9b92955bc89ecada29f5d4e6b9a21f4f0a28f8c5).
- Data: JetClass v1.0.0, https://zenodo.org/records/6619768 (DOI 10.5281/zenodo.6619768, CC-BY-4.0). We used the file `JetClass_Pythia_test_20M.tar`.
- Target: Table 1, ParT row (full input) with the released checkpoint `models/ParT_full.pt`, on the full 20 M-jet test set. Primary claims: accuracy and AUC. Secondary claims: the 9 background rejections. Optional: the ParticleNet row with `models/ParticleNet_full.pt`.
- Verdict: **Reproduced**
- Date: 2026-10-25
- Hardware: Ryzen 9 3900X, 31 GB RAM available to WSL2, RTX 2070 SUPER 8 GB, WSL2 Ubuntu 24.04

## Results

All claims, definitions and tolerances were fixed in `claims.json` before any model ran or any test data was downloaded. Its sha256 is 9d2c955c3b2482b3de2e88702f20d7a622c58aec4c941c96f3dad1b467e8ce5b and it still matches `claims.sha256`, so it was not edited afterwards. The verdict comes from the main run: weaver-core 0.4.17, fp32 inference, all 20,000,000 test jets. Pass or fail for every row uses the pre-registered tolerance. For accuracy and AUC that means agreement at the printed precision. For each rejection it is the Poisson band 1/sqrt(k).

Before scoring we checked the test set. It has exactly 2,000,000 jets in each of the 10 classes and 20,000,000 in total. In all 20 M jets the `label_*` branch agrees with the file name.

How to read the Rej rows:

- k is the number of QCD jets (out of 2,000,000) that pass the cut at the target signal efficiency, so Rej = 2,000,000 / k.
- **Pre-reg. k** is the single k that `claims.json` derived from the published integer. **Exact (pre-reg.)** says whether our k equals it. This is the pre-registered exact-match test.
- **Post-hoc range** is every whole k that rounds to the published integer, worked out after the runs in `runs/exact_match.py` (output in `runs/exact_match.txt`). **In range (post-hoc)** says whether our k falls in it. This criterion was not pre-registered.
- Why the single pre-registered k was a poor choice for small rejections: about 2,000,000/Rej² values of k round to the same integer. That is more than one below Rej ≈ 1,400 and 7 or more below Rej ≈ 550. For H→gg (123) the range is 16195–16326, so a single k = 16260 tests a precision the paper never printed.

**ParT, main run (fp32, weaver-core 0.4.17)**

| Quantity | Paper | Pre-reg. k | Ours | Diff | Exact (pre-reg.) | Post-hoc range | In range (post-hoc) | Status |
|---|---|---|---|---|---|---|---|---|
| Accuracy (primary) | 0.861 | — | 0.86051 (17,210,171 / 20,000,000) | −0.00049 | — | — | — | pass (see note) |
| AUC, macro one-vs-one (primary) | 0.9877 | — | 0.98772 | +0.00002 | — | — | — | pass (rounds to 0.9877) |
| Rej50% H→bb | 10638 | 188 | 10638.3 (k = 188) | +0.003% | yes | 188 | yes | pass |
| Rej50% H→cc | 4149 | 482 | 4149.4 (k = 482) | +0.009% | yes | 482 | yes | pass |
| Rej50% H→gg | 123 | 16260 | 123.4 (k = 16203) | +0.35% | no | 16195–16326 | yes | pass |
| Rej50% H→4q | 1864 | 1073 | 1870.9 (k = 1069) | +0.37% | no | 1073 | no | pass |
| Rej99% H→ℓνqq′ | 5479 | 365 | 5420.1 (k = 369) | −1.08% | no | 365 | no | pass |
| Rej50% t→bqq′ | 32787 | 61 | 32258.1 (k = 62) | −1.61% | no | 61 | no | pass |
| Rej99.5% t→bℓν | 15873 | 126 | 16260.2 (k = 123) | +2.44% | no | 126 | no | pass |
| Rej50% W→qq′ | 543 | 3683 | 542.9 (k = 3684) | −0.02% | no | 3680–3686 | yes | pass |
| Rej50% Z→qq̄ | 402 | 4975 | 402.3 (k = 4972) | +0.06% | no | 4969–4981 | yes | pass |

Accuracy note: 0.86050855 rounds to 0.861, but only by 171 jets (8.6e-6 above the 0.8605 edge). The difference from the paper, −0.00049, is half the pre-registered ±0.001 band.

All 9 rejections are inside the pre-registered Poisson band. On the pre-registered exact test, our k equals the claims.json k in **2 of 9** cases (H→bb, H→cc). On the post-hoc reading (any k that rounds to the published integer), it matches in 5 of 9. In the other 4 (H→4q, H→ℓνqq′, t→bqq′, t→bℓν), k is off by 1 to 4 QCD jets.

**ParT, pre-registered AMP variant (`--use-amp`, as in `train_JetClass.sh`)**

| Quantity | Paper | Pre-reg. k | Ours (AMP) | Diff | Exact (pre-reg.) | Post-hoc range | In range (post-hoc) | Status |
|---|---|---|---|---|---|---|---|---|
| Accuracy | 0.861 | — | 0.86051 | −0.00049 | — | — | — | pass |
| AUC | 0.9877 | — | 0.98772 | +0.00002 | — | — | — | pass |
| Rej50% H→bb | 10638 | 188 | 10638.3 (k = 188) | +0.003% | yes | 188 | yes | pass |
| Rej50% H→cc | 4149 | 482 | 4158.0 (k = 481) | +0.22% | no | 482 | no | pass |
| Rej50% H→gg | 123 | 16260 | 123.4 (k = 16210) | +0.31% | no | 16195–16326 | yes | pass |
| Rej50% H→4q | 1864 | 1073 | 1872.7 (k = 1068) | +0.46% | no | 1073 | no | pass |
| Rej99% H→ℓνqq′ | 5479 | 365 | 5434.8 (k = 368) | −0.81% | no | 365 | no | pass |
| Rej50% t→bqq′ | 32787 | 61 | 32786.9 (k = 61) | 0.000% | yes | 61 | yes | pass |
| Rej99.5% t→bℓν | 15873 | 126 | 16000.0 (k = 125) | +0.80% | no | 126 | no | pass |
| Rej50% W→qq′ | 543 | 3683 | 542.0 (k = 3690) | −0.18% | no | 3680–3686 | no | pass |
| Rej50% Z→qq̄ | 402 | 4975 | 402.5 (k = 4969) | +0.12% | no | 4969–4981 | yes | pass |

Pre-registered exact test: **2 of 9** (H→bb, t→bqq′). Post-hoc range: 4 of 9. The 5 misses on the post-hoc reading are off by 1 to 5 QCD jets.

We also compared fp32 and AMP jet by jet. The largest single-score difference is 0.042. The class with the highest score changes for 6,130 of the 20 M jets, and accuracy changes by 1e-6. Between the two runs k differs by 0 (H→bb), 1 (H→cc, H→4q, H→ℓνqq′, t→bqq′), 2 (t→bℓν), 3 (Z→qq̄), 6 (W→qq′: 3684 vs 3690) and 7 (H→gg: 16203 vs 16210) QCD jets. That is the same order as the 1–5 jets by which both runs miss the published counts.

**ParticleNet, optional (fp32, weaver-core 0.4.17, `models/ParticleNet_full.pt`)**

| Quantity | Paper | Pre-reg. k | Ours | Diff | Exact (pre-reg.) | Post-hoc range | In range (post-hoc) | Status |
|---|---|---|---|---|---|---|---|---|
| Accuracy | 0.844 | — | 0.84391 | −0.00009 | — | — | — | pass |
| AUC | 0.9849 | — | 0.98494 | +0.00004 | — | — | — | pass |
| Rej50% H→bb | 7634 | 262 | 7633.6 (k = 262) | −0.005% | yes | 262 | yes | pass |
| Rej50% H→cc | 2475 | 808 | 2475.2 (k = 808) | +0.010% | yes | 808 | yes | pass |
| Rej50% H→gg | 104 | 19231 | 103.8 (k = 19267) | −0.19% | no | 19139–19323 | yes | pass |
| Rej50% H→4q | 954 | 2096 | 953.7 (k = 2097) | −0.03% | no | 2096–2097 | yes | pass |
| Rej99% H→ℓνqq′ | 3339 | 599 | 3338.9 (k = 599) | −0.003% | yes | 599 | yes | pass |
| Rej50% t→bqq′ | 10526 | 190 | 10526.3 (k = 190) | +0.003% | yes | 190 | yes | pass |
| Rej99.5% t→bℓν | 11173 | 179 | 11173.2 (k = 179) | +0.002% | yes | 179 | yes | pass |
| Rej50% W→qq′ | 347 | 5764 | 347.2 (k = 5761) | +0.05% | no | 5756–5772 | yes | pass |
| Rej50% Z→qq̄ | 283 | 7067 | 282.8 (k = 7071) | −0.05% | no | 7055–7079 | yes | pass |

Pre-registered exact test: **5 of 9**. The 4 misses (H→gg, H→4q, W→qq′, Z→qq̄) are all columns where several k round to the published integer. Post-hoc range: 9 of 9, so all 11 numbers in the ParticleNet row round to the published values at the printed precision. `train_JetClass.sh` runs ParticleNet without AMP, so an fp32 run is the authors' own setup for this model. That fits with the closer match.

## What it took

1. **Environment** (`env/setup.sh`, `env/requirements.lock`).
   - Python 3.10, as the weaver-core README recommends.
   - weaver-core 0.4.17 installed from the tagged checkout.
   - Its dependencies resolved as they stood on 2024-08-07 (`uv --exclude-newer`), the day after 0.4.17 was published. This gave numpy 1.26.4, uproot 5.1.2, awkward 2.6.7 and scikit-learn 1.5.1.
   - torch 2.4.1+cu121. weaver-core pins no torch version, and 2.4 was current in August 2024.
   - uproot is below 5.2, so the loader hang in weaver-core issue #14 does not happen, and we used `--num-workers 3`.
   - A first attempt that resolved to current package versions was discarded. Its lock is kept in `runs/requirements.firsttry.lock`.
   - Table 1 predates weaver-core: it was made with the older hqucms/weaver, and the repo switched to weaver-core on 2022-12-15 (commit 29ef32b5, recorded in `claims.json` D10). 0.4.17 is the closest released version, not the code that made the table.
2. **Data** (`runs/download.sh`, `runs/extract.sh`).
   - Downloaded with `aria2c -x16 -s16` in about 25 minutes.
   - Size: 30,370,816,000 B, equal to the size listed by Zenodo (recorded in triage; `download.sh` checks against that value).
   - md5: 64e5156d26d101adeb43b8388207d767, equal to the Zenodo value.
   - Extracted 200 ROOT files (20 per class), about 22 minutes. Every file size equals the tar listing (`runs/extract_size_check.txt`).
   - Checkpoints come from the repo at the pinned commit. `ParT_full.pt` has md5 719fb783d8eeb27f609b103a82e100f6 and sha256 61e752f8…fec0, both matching the pre-registration.
3. **Pilot.** We ran ParT fp32 on one file per class (1 M jets) to check the whole chain end to end. Result: accuracy 0.8602, AUC 0.98767.
4. **Full runs** (`runs/run_all.sh`, `runs/predict.sh`). Each GPU call ran under `flock /mnt/e/Ciencia/.gpu.lock`. Wall times come from `runs/run_all.log`, and rates are 20,000,000 jets divided by them:
   - ParT fp32: 15:26:15–17:40:57 (8,082 s, ≈2,470 jets/s). The 0.5.3 variant pilot was interleaved under the same lock during this time.
   - ParT AMP: 17:40:57–19:28:55 (6,478 s, ≈3,090 jets/s).
   - ParticleNet fp32: 19:28:55–22:05:47 (9,412 s, ≈2,125 jets/s).
5. **Scoring** (`runs/score.py`, about 4 minutes per run, outputs in `runs/full_*/score.json`). It follows the pre-registered definitions:
   - D3, accuracy: argmax of the 10 outputs.
   - D4: `roc_auc_score(average='macro', multi_class='ovo')` on float64 scores. No renormalisation was needed: rows sum to 1 within 2.6e-7.
   - D5–D7: Rej from `roc_curve(drop_intermediate=False)`, taking the first ROC point with TPR ≥ X.
   - `runs/test_score.py` is a small self-check of the Rej reading on a hand-made ROC curve.

**Changes to the authors' code: none** (`patches/` is empty). The command differs from `train_JetClass.sh` in these points:

- `--predict` with the `.pt` checkpoint as `--model-prefix`;
- no training arguments;
- ParT main run without `--use-amp` (fp32, pre-registered D9); the AMP variant keeps it;
- one `weaver` call per class group instead of one call with all 10 groups, so the run can restart per class (weaver handles each group separately anyway and writes the same `pred_<group>.root` files);
- `--num-workers 3` instead of 2, which does not change any per-jet output.

**Fixes to our own scripts.** One bug in our scoring script. The log-ratio variant (D6b) hit ±inf for 120 ParticleNet jets whose float32 softmax output is exactly 0, and sklearn refused the input. We mapped ±inf to ±1e300, which keeps the rank order, and re-scored all three runs from the same predictions. The main score and the verdict do not depend on this variant.

**weaver-core 0.5.3 variant (D10).**

- Setup: its own environment (`env/setup_variant_0.5.3.sh`, `env/requirements-0.5.3.lock`: numpy 2.2.6, uproot 5.7.4, same torch), `--num-workers 0` because of issue #14, run on the pilot subset only (1 M jets).
- Result: the checkpoint loads strictly with no missing or unexpected keys, but the outputs are close to random. Accuracy 0.123, AUC 0.565, and the top-scoring class differs from 0.4.17 for 877,019 of the 1 M jets.
- Diagnosis (`runs/diag_weaver053/diag.log`, CPU, first 512 H→bb jets of `HToBB_100.root` only):
  - on every real particle the 0.5.3 loader gives exactly the same inputs as 0.4.17 (max |diff| 0);
  - padded slots do differ (max |diff| 2.6 in `pf_points`, 5.78 in `pf_features`, 824 in `pf_vectors`), so padding changed between versions too, but `pf_mask` is identical and masks those slots;
  - the 0.4.17 model gives identical scores on either set of inputs (max |score diff| 0);
  - the 0.5.3 model gives the same wrong scores on either set (max |score diff| 0, accuracy 0 on these 512 H→bb jets).

  On this sample, then, the difference is in the 0.5.3 model code (`weaver/nn/model/ParticleTransformer.py`), not in data loading. We did not track down which commit causes it, and we did not test ParticleNet under 0.5.3.

## Alternative readings

None of these change the verdict.

- **Operating point (D7).** For all 27 Rej values, three readings of the ROC curve give the same k: the first ROC point with TPR ≥ X, linear interpolation, and the nearest ROC point. The one exception is ParT fp32 t→bℓν, where interpolation gives k = 124 instead of 123. At each threshold exactly one jet sits on the cut.
- **Precision of the two-class score (D6).** We computed s(S)/(s(S)+s(QCD)) in float64 (main), in float32, and as the log difference in float64. All three give the same k everywhere except one case: ParT AMP H→gg gives k = 16225 in float32 instead of 16210. The float32 ratio creates up to 331 tied scores at the cut (ParT AMP, H→bb), but the ties never moved k in any other case.
- **Exact-match criterion (post-hoc).** The pre-registered exact test compares our k with one k per column from `claims.json`. It gives 2 of 9 (ParT fp32), 2 of 9 (ParT AMP) and 5 of 9 (ParticleNet). Read instead as "any k that rounds to the published integer", a criterion we chose after seeing the results, the counts are 5 of 9, 4 of 9 and 9 of 9. Every column where the two readings disagree has Rej below about 550, where 7 or more values of k round to the same integer.
- **fp32 against AMP as the "authors' setting".** The authors trained and evaluated ParT with `--use-amp`, so AMP is the closer copy of their setup. Neither of our runs gives all nine published values, even on the post-hoc reading. Where they miss, fp32 is off by 1–4 jets and AMP by 1–5 jets. Our own fp32 and AMP runs differ from each other by 0–7 jets (per column: H→bb 0, H→cc 1, H→gg 7, H→4q 1, H→ℓνqq′ 1, t→bqq′ 1, t→bℓν 2, W→qq′ 6, Z→qq̄ 3), so numerical drift of this size is plausible. We cannot say which source is behind the residual: GPU, torch/cuDNN version, or the older hqucms/weaver that produced Table 1 (it predates weaver-core; `claims.json` D10).

## Notes for the authors

Hello, and thank you for releasing the checkpoints and the full JetClass test set. We re-ran Table 1 with `models/ParT_full.pt` and `models/ParticleNet_full.pt` on all 20 M test jets, using weaver-core 0.4.17. ParT accuracy and AUC match at the printed precision. So do 5 of the 9 ParT rejections, in the sense that our value rounds to the published integer. The other 4 differ by 1–4 QCD jets out of 2,000,000. That is comparable to the 1–7 jet differences between our own fp32 and AMP runs, but we cannot pin down the cause (GPU, torch/cuDNN version, or the older weaver that made the table). All 11 numbers in the ParticleNet row match at the printed precision.

Two small suggestions:

1. **Pin weaver-core below 0.5 in the README.** The README says `pip install 'weaver-core>=0.4'`, which now installs 0.5.3 (tagged 2026-06-22). With 0.5.3, `ParT_full.pt` loads without any key error but gives close to random predictions: accuracy 0.123 and AUC 0.565 on 1 M test jets, against 0.860 with 0.4.17. On the first 512 H→bb jets of `HToBB_100.root`, the 0.5.3 loader gives the same values as 0.4.17 on every real particle (padded slots differ but are masked), and the 0.4.17 model scores are unchanged on 0.5.3 inputs, while the 0.5.3 model gives the same wrong scores on either set. That points to the 0.5.3 `ParticleTransformer` implementation. Since nothing fails loudly, a new user would get wrong numbers without any warning. Something like `pip install 'weaver-core>=0.4,<0.5'`, or a note on which 0.5 option restores the old behaviour, would prevent that. We did not test ParticleNet under 0.5.3.
2. **Say that the released `*_full.pt` files are the Table 1 models.** The README calls them pre-trained models for fine-tuning. Our results strongly indicate they are the ones behind Table 1. Saying so would save the next person the check.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer. Human review before publication: pending. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine or from arithmetic on logged values (the jet rates), and the commands, logs and outputs are in this folder.

Before anything ran, a separate agent read the paper and pre-registered the numeric claims, with every definition and tolerance the computation needed. A single agent then built the environment, ran the authors' code and released weights on one RTX 2070 SUPER (8 GB) and a Ryzen 9 3900X, compared the results with the paper and wrote this report. A reviewer agent checked the report against the logs and a reviser agent applied the corrections. A single agent did the computation; no second agent recomputed it blind.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues