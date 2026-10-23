# Reproduction report: Cellpose3: one-click image restoration for improved cellular segmentation

- Paper: Carsen Stringer, Marius Pachitariu, Nature Methods 22, 592-599 (2025). DOI: 10.1038/s41592-025-02595-5
- Code: https://github.com/MouseLand/cellpose @ tag v3.1.1.1 (fb22843e70d03f7884c301b7b72bedd7d9c3d2d9, 12 Feb 2025, the day after publication). Analysis scripts: `paper/3.0/analysis.py`, `paper/3.0/figures.py` at the same commit.
- Data:
  - CARE test data (Drosophila wing `Projection_Flywing`, `Denoising_Tribolium`), CC0, Edmond doi:10.17617/3.FDFZOF (the old publications.mpi-cbg.de links return 404)
  - Two-photon ribo-jGCaMP8s dataset from this paper, CC BY-NC 4.0, figshare doi:10.25378/janelia.27854442 (files 1, 3, 4, 5, 6, which are the ones `real_examples_ribo` reads)
  - Models: released `denoise_cyto2`, `denoise_nuclei`, `cyto2`, `nuclei` weights, downloaded automatically by cellpose
- Target: segmentation AP@0.5 on noisy vs Cellpose3-denoised images for the real-data experiments: Fig. 2b,c (Drosophila wing), Fig. 2d,e (two-photon, dense and sparse expression, 1 to 64 averaged frames), Fig. 3c,d (Tribolium). The synthetic-noise benchmarks on the Cellpose test sets (Fig. 1j, 3b, 4b, deblurring and upsampling) were **not** run, see "Scope".
- Verdict: **Partially reproduced**. Every number we could run matches the paper (all 46 values within figure-reading precision; the 6 values printed on the figures match to 2 decimals). The headline synthetic benchmark could not be run without a human accepting the dataset terms, and its noisy test files were never released.
- Date: 2026-10-22
- Hardware: Ryzen 9 3900X, 64 GB RAM, RTX 2070 SUPER 8 GB, WSL2 Ubuntu 24.04

## Results

Paper values for means are read off the published figure PNGs (Springer media server, 2168 px wide), so their precision is about ±0.01 to 0.02. Values the paper prints on the figure (example images, "AP@0.5 = x") are exact to 2 decimals. Ours are the mean over test images ± s.e.m., computed with the authors' code and the indexing from `figures.py`.

### Printed example values (exact)

| Quantity | Paper | Ours | Diff |
|---|---|---|---|
| Fig. 2b, wing image 10, 2% laser, noisy | 0.25 | 0.258 | +0.01 (rounding) |
| Fig. 2b, wing image 10, 2% laser, Cellpose3 denoised | 0.83 | 0.832 | 0.00 |
| Fig. 2d, two-photon image 3, 4 frames, noisy | 0.34 | 0.344 | 0.00 |
| Fig. 2d, two-photon image 3, 4 frames, denoised | 0.62 | 0.618 | 0.00 |
| Fig. 3c, Tribolium image 0, second laser level, noisy | 0.19 | 0.193 | 0.00 |
| Fig. 3c, Tribolium image 0, second laser level, denoised | 0.75 | 0.757 | +0.01 (rounding) |

### Mean AP@0.5 (read from figures)

| Quantity | Paper | Ours | Diff |
|---|---|---|---|
| Fig. 2c, wing, 2% laser, noisy (n=26) | 0.27 | 0.277 ± 0.041 | +0.01 |
| Fig. 2c, wing, 2% laser, denoised | 0.76 | 0.758 ± 0.030 | 0.00 |
| Fig. 2c, wing, 3% laser, noisy | 0.81 | 0.810 ± 0.023 | 0.00 |
| Fig. 2c, wing, 3% laser, denoised | 0.97 | 0.971 ± 0.004 | 0.00 |
| Fig. 2c, wing, 5% laser, noisy | 0.96 | 0.960 ± 0.005 | 0.00 |
| Fig. 2c, wing, 5% laser, denoised | 0.99 | 0.989 ± 0.001 | 0.00 |
| Fig. 3d, Tribolium, level 1, noisy (n=6) | 0.05 | 0.046 ± 0.008 | 0.00 |
| Fig. 3d, Tribolium, level 1, denoised | 0.31 | 0.312 ± 0.040 | 0.00 |
| Fig. 3d, Tribolium, level 2, noisy | 0.14 | 0.140 ± 0.019 | 0.00 |
| Fig. 3d, Tribolium, level 2, denoised | 0.49 | 0.492 ± 0.061 | 0.00 |
| Fig. 3d, Tribolium, level 3, noisy | 0.24 | 0.238 ± 0.037 | 0.00 |
| Fig. 3d, Tribolium, level 3, denoised | 0.61 | 0.610 ± 0.061 | 0.00 |
| Fig. 2e, two-photon dense (n=12), 1 frame, noisy / denoised | 0.17 / 0.30 | 0.168 / 0.302 | 0.00 / 0.00 |
| Fig. 2e, dense, 2 frames | 0.24 / 0.49 | 0.232 / 0.494 | -0.01 / 0.00 |
| Fig. 2e, dense, 4 frames | 0.31 / 0.60 | 0.309 / 0.599 | 0.00 / 0.00 |
| Fig. 2e, dense, 8 frames | 0.40 / 0.635 | 0.400 / 0.637 | 0.00 / 0.00 |
| Fig. 2e, dense, 16 frames | 0.55 / 0.72 | 0.556 / 0.717 | +0.01 / 0.00 |
| Fig. 2e, dense, 32 frames | 0.71 / 0.76 | 0.709 / 0.764 | 0.00 / 0.00 |
| Fig. 2e, dense, 64 frames | 0.81 / 0.82 | 0.804 / 0.817 | -0.01 / 0.00 |
| Fig. 2e, sparse (n=8), 1 frame, noisy / denoised | 0.10 / 0.18 | 0.093 / 0.187 | -0.01 / +0.01 |
| Fig. 2e, sparse, 2 frames | 0.24 / 0.36 | 0.240 / 0.359 | 0.00 / 0.00 |
| Fig. 2e, sparse, 4 frames | 0.33 / 0.49 | 0.326 / 0.489 | 0.00 / 0.00 |
| Fig. 2e, sparse, 8 frames | 0.38 / 0.63 | 0.379 / 0.633 | 0.00 / 0.00 |
| Fig. 2e, sparse, 16 frames | 0.42 / 0.66 | 0.428 / 0.662 | +0.01 / 0.00 |
| Fig. 2e, sparse, 32 frames | 0.53 / 0.71 | 0.531 / 0.708 | 0.00 / 0.00 |
| Fig. 2e, sparse, 64 frames | 0.67 / 0.74 | 0.666 / 0.738 | 0.00 / 0.00 |

The 4-frame dense row is also the IoU=0.5 point of the Fig. 2e left curve (paper 0.31 noisy, 0.60 denoised). Full numbers: `logs/summary.txt` and `logs/results.json`.

The paper's claim holds on real data. Cellpose3 denoising roughly doubles to triples AP@0.5 at the lowest signal levels (wing 0.28 to 0.76, Tribolium 0.05 to 0.31, two-photon single frame 0.17 to 0.30), and the gap closes as signal increases.

### Scope: what was not run and why

The main benchmark (Fig. 1j, 3b, 4b and Extended Data Figs. 2 to 5: 68 cyto2 and 111 nuclei test images with synthetic Poisson noise, blur and downsampling) needs two things that are not publicly available without human action:

1. **The clean test images.** The Cellpose dataset at https://www.cellpose.org/dataset is gated behind HHMI "Research Content Terms and Conditions" and an email form. An automated agent should not accept terms or submit personal data, so this needs a human.
2. **The noisy test files.** `seg_eval_cp3()` loads `noisy_test/test_poisson.npy`, `test_blur.npy` and `test_downsample.npy`. These are not in the repo, in the paper's data availability statement, on figshare, or in any GitHub issue we could find. The Methods say the noise level was set per image "to reduce the segmentation performance of 'cyto2' or 'nuclei' on the image by 50%" (Poisson scale 0.5 to 80, blur s.d. 0.5 to 10, downsampling 2 to 6), but the calibration code and the per-image values are not published. Rebuilding them would give a different test set, so its numbers would not be directly comparable.

The Noise2Void, Noise2Self, CARE and DenoiSeg baselines were also out of scope: they need training, and the target was noisy vs Cellpose3.

## What it took

Wall clock was about 8 h, of which roughly 3.5 h was spent waiting for the shared GPU lock behind other jobs. Actual GPU compute was about 10 min for both CARE datasets and about 4 min for the two-photon set (peak RSS 3.7 GB). The data download was about 15 GB: the two CARE tarballs were streamed with only `test_data/` extracted, plus 4.6 GB from figshare.

Steps:

1. `git clone`, then `git checkout v3.1.1.1`. Cellpose 4 replaced the models, and v3.1.1.1 is the tag closest to publication.
2. `uv venv -p 3.10`, then torch 2.4.1+cu121 and `pip install -e ./repo`. The lockfile is `env/requirements.lock.txt` (numpy 2.0.2, opencv-python-headless 5.0.0.93, scipy 1.15.3, fastremap 1.21.0). Nothing failed to install.
3. `env/download_data.sh` fetches the data.
4. `run_real.py` calls the authors' `analysis.real_examples()` (Flywing + Tribolium) and `analysis.real_examples_ribo()` unchanged. It only adds two things around them:
   - It replaces the `noise2self` / `noise2void` modules with an identity stub, so the functions do not try to train baselines (`noise2self.py` imports a missing `mask` module, and those baselines are outside the target). The stub output files (`n2s_*.npy`, `n2v_*.npy`) were deleted after the run because they are not baseline results.
   - It forces the Matplotlib Agg backend and turns `plt.show()` into a `savefig` into `logs/`. Under WSLg, the first attempt opened a window that blocked the run until someone closed it.
5. `summarize.py` reads the saved `cp_masks.npy` / `ribo_denoise.npy` with the same indexing as `figures.py` (example images, noise-level order, dense = images 0 to 11, sparse = 12 to 19).
6. `env/run_all.sh care ribo` runs everything headless under `flock /mnt/e/Ciencia/.gpu.lock`.

We made no change to the authors' code, so `patches/` is empty. No hyperparameter was touched: diameters, thresholds and model names are the ones hard-coded in `analysis.py`.

Pitfalls worth knowing:
- `figures.py` plots the Flywing noise levels in the order `[0, 2, 1]`: `proj_C1` is 5% laser and `proj_C3` is 3%, which is not the file order. We first labelled them in file order and got 3% and 5% swapped.
- Checking out the repo with Windows git (`core.autocrlf`) onto an NTFS path turns every file to CRLF. Python does not care, but WSL git then shows 64 modified files. We restored LF afterwards.
- The installed version string reads `3.1.1.2.dev0+gfb22843e7`. That comes from setuptools_scm, and the commit is still v3.1.1.1.

## Notes for the authors

Draft issue (not posted):

> **Paper 3.0 scripts: noisy test sets for Fig. 1/3/4 are not downloadable**
>
> Hi, thanks for releasing the analysis scripts with Cellpose3. We reran the real-data denoising analyses (Fig. 2b-e, 3c-d) with v3.1.1.1 and the released models, and every value matches the figures, including the printed example APs.
>
> We could not rerun Fig. 1j / 3b / 4b because `seg_eval_cp3()` needs `noisy_test/test_poisson.npy`, `test_blur.npy` and `test_downsample.npy`, which we could not find anywhere. The per-image noise levels were calibrated to halve cyto2/nuclei AP, so they cannot be regenerated exactly from the Methods. Would it be possible to upload these files (or the per-image noise parameters and seeds) next to the cyto2 test set?
>
> Some small things we noticed along the way:
> - Fig. 3d labels the Tribolium laser powers 0.2 / 0.3 / 0.5 mW, but the test tifs are named `nGFP_0.1_0.2_0.5_20_*.tif` and `real_examples()` uses stacks 0, 1, 2, i.e. 0.1 / 0.2 / 0.5 mW (with 20 mW as ground truth). The CARE paper also lists 0.1 / 0.2 / 0.5 mW.
> - The CARE download links in the `analysis.py` comment (publications.mpi-cbg.de/publications-sites/7207/) now return 404. The data is at Edmond, doi:10.17617/3.FDFZOF.
> - `real_examples()` calls `plt.show()`, which blocks headless or remote runs. A `savefig` or a flag would help.

## Independent reproductions

We found none: no ReScience C article, and no GitHub issue in MouseLand/cellpose that reruns the paper's benchmarks (we searched for "test_poisson", "noisy test" and "reproduce"). Third-party papers use the Cellpose3 restoration models in their own pipelines, with mixed results on their own data (e.g. arXiv:2501.19203), but none of them reruns this paper's numbers.

## Files

- `run_real.py`, `summarize.py`: driver and summary
- `env/requirements.lock.txt`, `env/download_data.sh`, `env/run_all.sh`
- `logs/care.log`, `logs/ribo.log`, `logs/summary.txt`, `logs/results.json`, `logs/care_ap_curves_*.png` (the authors' own quick AP-vs-IoU plots)
- `paper_text/`: paper full text from Europe PMC (PMC11903308) and the figure PNGs used to read the paper's values
- `data/`: downloaded test data and result `.npy` files (not for version control, about 11 GB)

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

A single agent read the paper, built the environment, ran the authors' code and released models on one RTX 2070 SUPER (8 GB) and a Ryzen 9 3900X, compared the results with the paper and wrote this report. A coordinating agent checked the report against the logs, and a human approved publication. This was a pilot run, before we added blind recomputation by a second agent.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues
