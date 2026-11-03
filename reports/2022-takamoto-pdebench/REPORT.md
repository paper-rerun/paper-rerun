# Reproduction report: PDEBench: An Extensive Benchmark for Scientific Machine Learning

- Paper: Takamoto, M., Praditia, T., Leiteritz, R., MacKinlay, D., Alesiani, F., Pflüger, D., Niepert, M. NeurIPS 2022 Datasets and Benchmarks Track, pp. 1596-1611. DOI: 10.48550/arXiv.2210.07182 (the proceedings version has no DOI: https://proceedings.neurips.cc/paper_files/paper/2022/hash/0a9747136d411fb83f0cf81820d44afb-Abstract-Datasets_and_Benchmarks.html)
- Code: https://github.com/pdebench/PDEBench @ b5b646f12802c283265e4c850566e2a11503624a. This is the last commit before the metric change 268ba5e of 21/10/2024.
- Data: DaRUS doi:10.18419/darus-2986, dataset version 1.0 (2022) files, fetched by file id. Checkpoints: DaRUS doi:10.18419/darus-2987, the 2022 tars.
- Target: the nRMSE of the pre-trained FNO and U-Net in Tables 6 (1D Advection), 7 (1D Burgers) and 8 (2D Darcy Flow) of the NeurIPS 2022 supplement. That is 26 values. The other 7 metrics in the same tables (182 values) are secondary. The authors replaced every Advection and Burgers value in arXiv v7 (26/08/2024). They regenerated the Advection data after a time-scaling bug in the generator (issue #46) and retrained the models in November 2023. This check targets the published 2022 version with the 2022 data and weights. v7 is out of scope (pre-registered as D1). Darcy is the same in all versions.
- Verdict: **Partially reproduced** (21 of 26 nRMSE values match at the paper's 2 significant figures). One of the 5 misses, Burgers ν=0.001 FNO, is 0.012% below the rounding edge.
- Date: 2026-11-03
- Hardware: Ryzen 9 3900X, 64 GB RAM (31 GB visible to WSL2), RTX 2070 SUPER 8 GB not used, WSL2 Ubuntu 24.04. The run was CPU only, capped at 4 cores, at nice 19.

## Results

Before any run, a separate agent pre-registered the claims, definitions and tolerance in `claims.json` (sha256 9a740b46…fe4ce60). The rule: a value matches if ours, formatted with `{:.1e}`, equals the printed value. "Ours" comes from the `.pickle` written by the authors' own `train_models_forward.py` with `if_training=False`. The test set is the first 1000 samples of each file, all of them used. The scoring code is `metrics.py` at b5b646f.

| Quantity (nRMSE) | Paper | Ours | Ours, 2 s.f. | Diff (rel.) | Match |
|---|---|---|---|---|---|
| Advection β=0.1, U-Net | 6.0e-02 | 0.059551 | 6.0e-02 | -0.7% | yes |
| Advection β=0.1, FNO | 9.3e-03 | 0.0092796 | 9.3e-03 | -0.2% | yes |
| Advection β=0.4, U-Net | 6.7e-01 | 0.66675 | 6.7e-01 | -0.5% | yes |
| Advection β=0.4, FNO | 1.1e-02 | 0.010931 | 1.1e-02 | -0.6% | yes |
| Advection β=1.0, U-Net | 2.0e-02 | 0.019636 | 2.0e-02 | -1.8% | yes |
| Advection β=1.0, FNO | 5.9e-03 | 0.62654 | 6.3e-01 | +10519% | **no** |
| Advection β=4.0, U-Net | 2.6e-02 | 0.029359 | 2.9e-02 | +12.9% | **no** |
| Advection β=4.0, FNO | 1.0e-02 | 0.010004 | 1.0e-02 | +0.0% | yes |
| Burgers ν=0.001, U-Net | 3.4e-01 | 0.34209 | 3.4e-01 | +0.6% | yes |
| Burgers ν=0.001, FNO | 4.2e-02 | 0.041495 | 4.1e-02 | -1.2% | **no** (0.012% below the rounding edge 0.0415) |
| Burgers ν=0.01, U-Net | 3.0e-01 | 0.30294 | 3.0e-01 | +1.0% | yes |
| Burgers ν=0.01, FNO | 2.0e-02 | 0.018192 | 1.8e-02 | -9.0% | **no** (near) |
| Burgers ν=0.1, U-Net | 2.8e-01 | 0.28033 | 2.8e-01 | +0.1% | yes |
| Burgers ν=0.1, FNO | 4.5e-03 | 0.0043432 | 4.3e-03 | -3.5% | **no** (near) |
| Burgers ν=1.0, U-Net | 3.6e-01 | 0.36013 | 3.6e-01 | +0.0% | yes |
| Burgers ν=1.0, FNO | 3.1e-03 | 0.0030544 | 3.1e-03 | -1.5% | yes |
| Darcy β=0.01, U-Net | 1.1e+00 | 1.0635 | 1.1e+00 | -3.3% | yes |
| Darcy β=0.01, FNO | 2.5e+00 | 2.4581 | 2.5e+00 | -1.7% | yes |
| Darcy β=0.1, U-Net | 1.8e-01 | 0.17723 | 1.8e-01 | -1.5% | yes |
| Darcy β=0.1, FNO | 2.2e-01 | 0.22124 | 2.2e-01 | +0.6% | yes |
| Darcy β=1.0, U-Net | 3.3e-02 | 0.032508 | 3.3e-02 | -1.5% | yes (0.024% above the rounding edge 0.0325) |
| Darcy β=1.0, FNO | 6.4e-02 | 0.064192 | 6.4e-02 | +0.3% | yes |
| Darcy β=10, U-Net | 8.2e-03 | 0.0081677 | 8.2e-03 | -0.4% | yes |
| Darcy β=10, FNO | 1.2e-02 | 0.011868 | 1.2e-02 | -1.1% | yes |
| Darcy β=100, U-Net | 4.4e-03 | 0.0043752 | 4.4e-03 | -0.6% | yes |
| Darcy β=100, FNO | 6.4e-03 | 0.0064259 | 6.4e-03 | +0.4% | yes |

By PDE:
- **Darcy:** all 10 match. We assumed `reduced_resolution=2` for the Darcy FNO from the U-Net case (D5). All five FNO values match under it.
- **Advection:** 6 of 8 match.
- **Burgers:** 5 of 8 match. Every U-Net nRMSE matches. 3 of the 4 FNOs miss, all on the low side, by 1.2% to 9%.

**Values near a rounding edge.** D13 asks the report to flag every value within 1% of a rounding boundary. None of these was re-run. 14 of the 26 are in that band. They come from `within_1pct_of_rounding_edge` in `runs/results.json`, and the distance is relative to the nearest edge:

| Quantity (nRMSE) | Ours | Nearest edge | Distance | Match |
|---|---|---|---|---|
| Burgers ν=0.001, FNO | 0.041495 | 0.0415 | -0.012% | **no** |
| Darcy β=1.0, U-Net | 0.032508 | 0.0325 | +0.024% | yes |
| Advection β=0.1, U-Net | 0.059551 | 0.0595 | +0.086% | yes |
| Burgers ν=1.0, FNO | 0.0030544 | 0.00305 | +0.145% | yes |
| Darcy β=10, U-Net | 0.0081677 | 0.00815 | +0.218% | yes |
| Advection β=0.4, U-Net | 0.66675 | 0.665 | +0.263% | yes |
| Advection β=0.1, FNO | 0.0092796 | 0.00925 | +0.320% | yes |
| Darcy β=0.01, FNO | 2.4581 | 2.45 | +0.330% | yes |
| Darcy β=100, FNO | 0.0064259 | 0.00645 | -0.374% | yes |
| Darcy β=1.0, FNO | 0.064192 | 0.0645 | -0.478% | yes |
| Darcy β=100, U-Net | 0.0043752 | 0.00435 | +0.579% | yes |
| Burgers ν=0.01, U-Net | 0.30294 | 0.305 | -0.675% | yes |
| Advection β=1.0, U-Net | 0.019636 | 0.0195 | +0.698% | yes |
| Burgers ν=0.001, U-Net | 0.34209 | 0.345 | -0.845% | yes |

Two of these are very close. Burgers ν=0.001 FNO misses by 0.012% of the edge, and Darcy β=1.0 U-Net matches by 0.024%. A float difference of that size between our CPU and the authors' GPU could flip either one, so the 21/26 count could be 20 or 22. The other 12 values sit 0.09% to 0.85% from the edge and are less exposed.

**Comparison with the authors' own rerun.** In issue #39 the maintainer posted all 8 metrics for the five Darcy U-Nets. Our 40 values agree with his. 32 are identical at the precision he printed. The other 8 are fRMSE values he printed to 8 digits, and they differ from ours from the 6th digit on (at most 4e-6 relative). This includes the three Darcy U-Net secondary values that miss Table 8:

| Darcy U-Net value | Ours | Maintainer (#39) | Table 8 |
|---|---|---|---|
| β=0.1, bRMSE | 0.000855 | 0.00085 | 8.6e-04 |
| β=10, fRMSE low | 0.00574525 | 0.00574524 | 5.8e-03 |
| β=10, fRMSE high | 0.00035455 | 0.00035455 | 3.6e-04 |

His rerun misses Table 8 in the same three places. The pre-registration says all 40 of his values round to Table 8 (`claims.json`, tolerance basis), and that is not correct.

**Secondary metrics (same runs).** 140 of the 182 values match at 2 significant figures:

| Metric | Matches |
|---|---|
| RMSE | 22/26 |
| max error | 19/26 |
| cRMSE | 18/26 |
| bRMSE | 21/26 |
| fRMSE low | 19/26 |
| fRMSE mid | 21/26 |
| fRMSE high | 20/26 |

Most of the 42 misses come from three groups:
- **Advection β=1.0 FNO:** all 7 secondary metrics are off by 2× to 660×.
- **Burgers ν=0.01, 0.1 and 1.0 FNO:** 21 misses, all 7 metrics of each model. All are below the paper, by 5% to 57%. This includes ν=1.0, whose nRMSE matches. The 7 secondary metrics of the ν=0.001 FNO all match.
- **Advection β=4.0 U-Net:** 4 misses (max error +6.3%, cRMSE +19.3%, fRMSE low -1.8%, fRMSE high +3.2%).

The other 10 misses are spread over 6 settings and range from 0.6% to 3.1%:
- Advection β=0.4 FNO: max error -2.6%, cRMSE -2.9%, fRMSE low -2.1%;
- Advection β=4.0 FNO: cRMSE -1.5%, fRMSE mid -1.0%;
- Darcy β=10 U-Net: fRMSE low -0.9%, fRMSE high -1.5%;
- Advection β=0.4 U-Net: max error -3.1%;
- Burgers ν=0.1 U-Net: cRMSE -1.8%;
- Darcy β=0.1 U-Net: bRMSE -0.6%.

The full list is in `runs/results.json`.

## Alternative readings

These diagnostics do not change the verdict.

**V1, metric from 268ba5e and later (input steps excluded).** Every nRMSE grows by exactly 41/31 (1D) or 2 (Darcy). That is the expected effect of dropping the copied inputs from the average: the 10 input steps in 1D, or the a(x) slot in Darcy. Examples:
- Advection β=0.1 U-Net: 0.0788 instead of 0.0596.
- Darcy β=0.01 U-Net: 2.127 instead of 1.064.

**V2, supplement Eq. 4 taken literally** (square root of each per-sample, per-step ratio ‖e‖/‖u‖, same averaging). The values are usually much larger, for example 0.205 instead of 0.0596 for Advection β=0.1 U-Net. They are smaller for both Darcy β=0.01 models: 0.674 instead of 1.064 for the U-Net, and 1.017 instead of 2.458 for the FNO. Under this reading, 0 of the 26 nRMSE values would match, whether the input steps are kept in the average or dropped. This supports the pre-registered choice (D8): the tables were produced by the code, not by Eq. 4 as printed.

**Advection β=1.0 FNO, cross-check.** We scored each of the four 2022 Advection FNO checkpoints on each of the four Advection test sets, with the same rollout and `metric_func`. We checked our direct reader against the authors' loader on the full β=4.0 file, and the arrays were identical. The other three test sets were read from the same byte layout in the downloaded head pieces. The diagonal reproduces the pipeline values to about 2e-7 relative.

| Checkpoint | β=0.1 data | β=0.4 data | β=1.0 data | β=4.0 data |
|---|---|---|---|---|
| beta0.1_FNO.pt | **0.0093** | 0.86 | 0.69 | 0.82 |
| beta0.4_FNO.pt | 0.63 | **0.0109** | 0.77 | 0.88 |
| beta1.0_FNO.pt | 0.63 | 0.0118 | 0.63 | 0.71 |
| beta4.0_FNO.pt | 0.64 | 0.60 | 0.34 | **0.0100** |

The file named `1D_Advection_Sols_beta1.0_FNO.pt` performs like a model trained on β=0.4 data: nRMSE 0.0118 there, against 0.63 on β=1.0. Its weights differ from `beta0.4_FNO.pt` (epoch 362 against 499). So it looks like a β=0.4 training run saved under the β=1.0 name, not a duplicate file. The β=1.0 data file itself is fine: the β=1.0 U-Net on the same file gives 2.0e-02, as in the paper. So the paper's 5.9e-03 for β=1.0 FNO cannot be checked with the released checkpoint.

## What it took

1. **Downloads** (serial, about 22 GB in 51 min, about 7.3 MB/s on average). The downloader was restarted once during the fifth checkpoint tar. The four tars already done were skipped and that tar was fetched again. Each file was checked against the size and md5 the DaRUS API reports:
   - the 6 checkpoint tars, md5 OK;
   - the 5 Darcy files, full, md5 OK;
   - one full 1D file (Advection β=4.0, 8,232,968,312 B, md5 OK).

   For the other seven 1D files we downloaded only the header plus the first 1000 samples (bytes 0-823,298,047) and the last 6,264 B. This is pre-registered as D14. Before relying on these partial copies we checked them on Advection β=4.0. The partial copy and the full file give bit-identical values for all 8 metrics, for both models. A partial copy has no full-file md5. Instead, the server's Content-Range total matched the expected size, and the md5 of each piece is in `data/sparse/*.done`. Drive E: does not keep sparse files, so each full-size file was rebuilt just before its run and deleted after it.
2. **Environment.** Python 3.9.25 with torch 1.13.1+cpu, built with uv, following the repo's `pyproject.toml` (`torch~=1.13.0`). We also used numpy 1.26.4, h5py 3.14.0 and hydra-core 1.3.8. deepxde and pyro-ppl are left out because the forward FNO/U-Net path does not import them. Files: `env/requirements.in`, `env/requirements.lock`, `env/freeze.txt`, `env/setup.sh`.
3. **Checkpoint checks before running.** All 26 had the expected input shapes: FNO1d fc0 (20, 11), FNO2d (20, 3), U-Net 1D first conv (32, 10, 3), U-Net Darcy (32, 1, 3, 3). Each Darcy U-Net `*_Unet_PF_1.pt` was copied, bytes unchanged, to the name the code builds, `*_Unet-PF-1.pt` (D11).
4. **Runs.** We used the authors' entry point (`train_models_forward.py`) and configs (`+args=config_Adv.yaml`, `config_Bgs.yaml` or `config_Darcy.yaml`), changed only by Hydra command-line overrides. The full command of every run is in `runs/pipeline.log`. The overrides:
   - all runs: `++args.filename`, `++args.model_name`, `++args.if_training=False`, `++args.data_path`;
   - Darcy: `++args.initial_step=1`, `++args.t_train=2`, `++args.reduced_resolution=2`, `++args.reduced_resolution_t=1` (the last two equal what `config/args/config_Darcy.yaml` already has);
   - Darcy U-Net, in addition: `++args.ar_mode=True`, `++args.pushforward=True`, `++args.unroll_step=1`.

   `t_train=2` came from the triage and differs from the config's `t_train: 1`. It does not enter the scores: with `if_training=False`, `metrics()` loops up to `yy.shape[-2]` and never reads `t_train`. It does matter for the Darcy U-Net file name. With `t_train: 1` the code sets `unroll_step = t_train - 1 = 0` and would look for `*_Unet-PF-0.pt` (`unet/train.py`, lines 131-137). For the FNO it has no effect.

   Wall time per run was 42-142 s for Darcy and 126-270 s for 1D. The whole pipeline took about 1 h 46 min (16:52 to 18:39). A second pass with our own script (`runs/diag.py`) reran the same rollout and saved the predictions (`runs/preds/`). It reproduced the authors' nRMSE for all 26 to within 1e-6 relative.
5. **Changes to the authors' code: none.** No patches were needed: `repo/` is at b5b646f with a clean `git status`, so no `patches/` folder was created. No method or hyperparameter was changed.

The scripts, logs and outputs are in `runs/`: `pipeline.py`, `pipeline.log`, `download.log`, `logs/`, `jobs/*/…pickle`, `results.json` and `xcheck_adv_fno.json`. The run logs are in `runs/logs/` (one per run, plus `xcheck_adv_fno.log`), not in a top-level `logs/` folder.

## Notes for the authors

Thank you for keeping the 2022 data and checkpoints downloadable. Almost everything reran on CPU without touching the code. Here are a few things we ran into. Notes 1-3 are about the 2022 release: the NeurIPS tables and the 2022 tars on DaRUS. We know the Advection and Burgers values were replaced in arXiv v7 after #46 and the 2023 retraining. We did not check v7.

1. **The 2022 Advection β=1.0 FNO checkpoint in `fno/advection_FNO.tar` (DaRUS file 133576) looks mislabelled.** On the 2022 β=1.0 test set, `1D_Advection_Sols_beta1.0_FNO.pt` gives nRMSE 0.63 instead of the 5.9e-03 in NeurIPS Table 6. On the 2022 β=0.4 test set it gives 0.0118. Could it be a β=0.4 run saved under the β=1.0 name? If the right file still exists, it would be great to add it next to the 2022 tars.
2. **The 2022 Burgers FNO checkpoints differ from NeurIPS Table 7.** The nRMSE of the ν=0.001, 0.01 and 0.1 FNOs is 1-9% below Table 7. All 7 secondary metrics of the ν=0.01, 0.1 and 1.0 FNOs are 5-57% below, while the secondary metrics of the ν=0.001 FNO match. Every Burgers U-Net nRMSE matches. Maybe these tars come from a different training run than the one behind the 2022 table?
3. **The 2022 Advection β=4.0 U-Net gives 2.9e-02 instead of the 2.6e-02 in NeurIPS Table 6** (cRMSE +19%).
4. **The stored Darcy β=0.01 FNO checkpoint has `epoch` = 0.** It still reproduces the table's 2.5. If that is intended, it would help to say so, since a reader may suspect a broken file.
5. **Configs for the pre-trained Darcy models.** Re-evaluating them with `config/args/config_Darcy.yaml` needs `initial_step=1`, because the file has `initial_step: 10`. The U-Net also needs a renamed file: the tar has `*_Unet_PF_1.pt`, but the code looks for `*_Unet-PF-1.pt`. To build that name, the code also needs `ar_mode=True`, `pushforward=True` and a `t_train` of at least 2. The `reduced_resolution` conflict is with `config/config_darcy.yaml`, which has `reduced_resolution: 1` (#48). `config/args/config_Darcy.yaml` already has 2, the value that reproduces the table. A short note in `config/README.md` would save the next person a search (see also #39).
6. **The supplement's Eq. 4 and frequency bands differ from `metrics.py`.** Eq. 4 has a square root over the ratio. The text gives the bands as 0-4/5-12/13-∞, while the code uses 0-3/4-11/12-end. The tables follow the code. Also, before 268ba5e the averages include the input steps (#41). This makes every 1D value 31/41 of the error over the predicted steps, and every Darcy value 1/2. A one-line erratum next to the tables would help anyone comparing against them.
7. **`pdebench_data_urls.csv` points to the 2023+ files.** Reproducing the NeurIPS tables needs the version-1.0 file ids (1331xx/1332xx). It may be worth listing those too.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

A separate agent pre-registered the claims, definitions and tolerances (`claims.json`, hash frozen) before any run. Then a single agent built the environment, ran the authors' code and released weights on a Ryzen 9 3900X (CPU only), compared the results with the paper and wrote this report. A reviewer agent checked the draft against the files in this folder, and a reviser agent corrected it. A human reads the report and decides on publication before anything is posted. This was a pilot run, before we added blind recomputation by a second agent.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues