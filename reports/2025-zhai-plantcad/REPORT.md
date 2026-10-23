# Reproduction report: Cross-species modeling of plant genomes at single-nucleotide resolution using a pretrained DNA language model (PlantCaduceus / PlantCAD)

- Paper: Zhai J, Gokaslan A, Schiff Y, Berthel A, Liu Z-Y, Lai W-L, Miller ZR, Scheben A, Stitzer MC, Romay MC, Buckler ES, Kuleshov V. PNAS 122(24), e2421738122, 2025. DOI: 10.1073/pnas.2421738122
- Code: https://github.com/plantcad/plantcad @ 7240f0238f869b3ac25e4b5ad0996fad96ede9db (2026-08-07)
- Model: https://huggingface.co/kuleshov-group/PlantCaduceus_l32 (main @ e624c13c; weights actually loaded from refs/pr/6 @ 9f78fc06, see below)
- Data: https://huggingface.co/datasets/kuleshov-group/cross-species-single-nucleotide-annotation (TIS and Donor folders)
- Target: cross-species XGBoost auPRC of PlantCaduceus_l32 for TIS and splice donor in sorghum and maize, Dataset S4 of the SI (column "XGBoost-AUPRC"), the values plotted in Fig. 2 C and E
- Verdict: **Partially reproduced**
- Date: 2026-10-22
- Hardware: Ryzen 9 3900X, 64 GB RAM, RTX 2070 SUPER 8 GB, WSL2 Ubuntu 24.04

## Results

The full test sets hold 60.6M windows (Dataset S3) and PlantCaduceus_l32 runs at 6.2 windows/s on this card, about 115 days of GPU time. So the test sets were evaluated on a weighted random subsample; details under "Scope". All four paper values fall inside our 95% intervals.

| Quantity (PlantCaduceus_l32, XGBoost) | Paper (Dataset S4) | Ours | 95% CI (bootstrap) | Diff |
|---|---|---|---|---|
| TIS auPRC, *S. bicolor* | 0.8145 | 0.8096 | 0.752 to 0.858 | -0.005 |
| TIS auPRC, *Z. mays* | 0.6401 | 0.6959 | 0.638 to 0.765 | +0.056 |
| Donor auPRC, *S. bicolor* | 0.8812 | 0.8806 | 0.847 to 0.907 | -0.001 |
| Donor auPRC, *Z. mays* | 0.7736 | 0.8331 | 0.766 to 0.895 | +0.060 |
| Sanity check: TIS auPRC, *A. thaliana* chr5 validation | 0.9285 | 0.9261 | 0.912 to 0.937 | -0.002 |
| Sanity check: Donor auPRC, *A. thaliana* chr5 validation | 0.9816 | 0.9861 | 0.981 to 0.990 | +0.005 |

Sorghum matches almost exactly. Both maize estimates come out about 0.06 above the paper, with the paper value near the lower edge of our interval. With these sample sizes we can't tell whether that is noise or a real gap. Per-chunk predictions are in `runs/`, and `logs/scores.log` has the running estimates as chunks finished.

### Scope (why "partially")

1. **Test sets subsampled.** For each task we kept every positive (TIS) or a random 25% of positives (Donor), plus a Bernoulli sample of negatives: 2% for TIS sorghum, 0.6% for TIS maize and Donor sorghum, 0.2% for Donor maize. That is 71k to 82k windows per task, 300k in total. auPRC is computed with sample weights 1/rate, so the estimate targets the full-set auPRC. Without the weights the sample would inflate auPRC a lot. On synthetic data the weighted estimate gave 0.913 against a full-set 0.910, and the unweighted one 0.986 (`scripts/test_weighted_auprc.py`). The class counts we streamed match Dataset S3 exactly for all four test sets.
2. **Released classifiers, not retrained.** We used the authors' XGBoost models in `classifiers/PlantCaduceus_l32/` with their `src/predict_XGBoost.py`, unchanged. Retraining would have meant embedding the Arabidopsis train/valid sets too (256k windows for TIS, 750k for Donor, about 45 h more). The Arabidopsis validation check above shows the released classifiers plus our embeddings land on the paper's validation numbers.
3. Rice, cotton, soybean, TTS and acceptor were not run.

## What it took

- **Environment.** uv venv with Python 3.11, `repo/requirements.txt` as is (torch 2.5.1+cu124, transformers 4.49.0, xgboost 2.0.3), plus the official prebuilt wheels mamba-ssm 2.2.4 and causal-conv1d 1.5.0.post8 (cu12, torch 2.5, cxx11abiFALSE). No compiling. Mamba runs fine on sm_75: we ran `selective_scan_fn` and `causal_conv1d_fn` on their own in fp32 and fp16 (`scripts/kernel_probe.py`). Lockfile: `env/requirements.lock.txt`; build script: `env/setup_env.sh`; run env: `env/activate.sh`.
- **Crash at the default batch size.** `predict_XGBoost.py` defaults to `-batchSize 128`. On 8 GB it died with `CUBLAS_STATUS_EXECUTION_FAILED` inside `mamba_inner_fn`. Two reasons:
  - The script asks for float16 on sm_75 (`torch_dtype=optimal_dtype`), but every parameter comes back float32 with transformers 4.49.0 (546 of 546 tensors), so the model runs in fp32.
  - `output_hidden_states=True` keeps all 33 hidden states at 2x1024 channels, about 138 MB per window in fp32.

  Peak memory: 3.5 GB at batch 8, 6.2 GB at batch 16, 11.4 GB at batch 32 (spills into shared memory, 0.3 windows/s). We ran `-batchSize 8`, a command-line option and not part of the method. Speed: 6.2 windows/s.
- **Weights.** transformers 4.49 pulled `model.safetensors` from the Hub's auto-conversion PR (refs/pr/6) instead of `pytorch_model.bin` on main. We compared the two files: the 548 shared tensors are identical. The safetensors file just leaves out the 65 tied tensors (mamba_rev in/out projections and the LM head). The loaded model reports 225,354,752 parameters, matching the README's 225M, so the ties held and the README's doubled-parameter warning does not apply here.
- **One transient failure.** One chunk (TIS sorghum 005) died with `CUDA error: unknown error` mid-run. A rerun of the same chunk passed. We read it as a WSL/driver hiccup.
- **Runtime.** 42 chunks of 8,000 windows, 15 h of pure inference (16.8 h counting waits on the GPU lock shared with other jobs). About 24 h wall clock from clone to final scores. The data download took about 30 min at 23 MB/s, streaming the 33 GB of test files and keeping only the sample (1.9 GB on disk).
- **Changes to the authors' code:** none. `patches/` is empty on purpose. Our own scripts (sampling, chunking, weighted scoring, driver) are in `scripts/`.

## Notes for the authors

Draft issue text, not posted:

> **Reproducing the cross-species XGBoost results on an 8 GB GPU**
>
> Thanks for releasing the classifiers and the dataset. We reproduced the PlantCaduceus_l32 TIS and Donor auPRC for sorghum and maize (Dataset S4) on a weighted subsample of the test sets with the released classifiers. Sorghum matches within 0.005; maize lands about 0.06 higher, still inside our 95% interval. A few things came up:
>
> 1. With the pinned transformers 4.49.0, `from_pretrained(..., torch_dtype=torch.float16)` in `load_model_and_tokenizer` returns a float32 model for PlantCaduceus_l32 (all 546 parameter tensors). The log still says "Using float16". Is that expected? If the paper's embeddings were fp32 too, it might be worth dropping the dtype branch so the log doesn't mislead.
> 2. At the default `-batchSize 128`, embedding extraction needs well over 8 GB, since `output_hidden_states=True` keeps all 33 layers and the model runs in fp32. On an RTX 2070 SUPER it fails with `CUBLAS_STATUS_EXECUTION_FAILED` instead of an OOM message, which took a while to read. A note in `docs/xgboost-classifiers.md` (batch 8 fits 8 GB), or taking only the last layer, would help people on small GPUs.
> 3. `main` only has `pytorch_model.bin`, so transformers loads `model.safetensors` from the auto-conversion PR (refs/pr/6). The tensors are identical, but merging that PR or uploading safetensors to main would make the loaded revision explicit.
> 4. The full test sets (60M windows for sorghum and maize alone) are out of reach for most people without a cluster. Releasing the per-window predictions behind Fig. 2, or an official smaller test split, would make the figure easy to check.
> 5. Small typo in Dataset S4: "S. biclor".

## Prior reproductions

We found no independent reproduction: nothing in ReScience C, and none of the 40 issues in the GitHub repo report re-running the cross-species benchmark (checked 2026-10-21).

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

A single agent read the paper, built the environment, ran the authors' code and released weights and classifiers on one RTX 2070 SUPER (8 GB) and a Ryzen 9 3900X, compared the results with the paper and wrote this report. A coordinating agent checked the report against the logs, and a human approved publication. This was a pilot run, before we added blind recomputation by a second agent.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues
